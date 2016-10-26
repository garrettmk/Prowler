import requests
import amazonmws as mws
import mwskeys
import logging

from PyQt5.QtCore import QObject, QThread, QMutex, QMutexLocker, pyqtSignal, pyqtSlot

from database import *


class OperationsManager(QObject):

    __instance__ = None
    supported_ops = ['ListMatchingProducts', 'StatusMessage']

    operation_complete = pyqtSignal(int)
    status_message = pyqtSignal(str)

    def __new__(cls, *args, **kwargs):
        if cls.__instance__ is None:
            cls.__instance__ = QObject.__new__(cls, *args, **kwargs)
        return cls.__instance__


    def __init__(self, parent=None):
        super(OperationsManager, self).__init__(parent=parent)
        self.dbsession = Session()
        self.scheduled = {}
        self.mutex = QMutex()

        # Set up the Amazon MWS api and throttling manager
        self.mwsapi = mws.Throttler(mws.Products(mwskeys.accesskey, mwskeys.secretkey, mwskeys.sellerid), blocking=False)
        self.mwsapi.api.make_request = self.print_request
        self.mwsapi.set_priority_quota('ListMatchingProducts', priority=0, quota=18)
        self.mwsapi.set_priority_quota('ListMatchingProducts', priority=10, quota=2)

    def add_operation(self, op):
        self.dbsession.add(op)
        self.load_next(op.api_call)

    def start(self):
        """Starts processing operations in the database."""
        self.status_message.emit('Begin processing operations...')
        for op_type in self.supported_ops:
            self.load_next(op_type)

    def stop(self):
        """Remove all pending operations from the queue."""
        self.status_message.emit('Stopping all operations.')
        for t_id in self.scheduled:
            self.killTimer(t_id)

        self.scheduled.clear()

    def load_next(self, api_call):
        """Load and schedule the next operation using api_call from the database."""
        # Sort operations by first by priority, then by scheduled time, then by id
        next_op = self.dbsession.query(Operation). \
                                 filter(Operation.complete == False). \
                                 filter(Operation.operation.like('{}%'.format(api_call))). \
                                 order_by(Operation.priority.desc()). \
                                 order_by(Operation.scheduled). \
                                 order_by(Operation.id). \
                                 first()

        if next_op is None:
            return

        # We only want one operation of a given type scheduled at a time, so bump the currently scheduled op
        # if it's priority is lower. If there is already a scheduled operation of this type, return
        for t_id, s_op in {k: v for k, v in self.scheduled.items()}.items():
            if s_op.api_call == api_call and s_op.priority < next_op.priority:
                self.killTimer(t_id)
                self.scheduled.pop(t_id)
            elif s_op.api_call == api_call:
                return

        self.schedule_op(next_op)

    def schedule_op(self, op, wait=None):
        # Get next available time from the throttler
        if wait is None:
            wait = self.mwsapi.request_wait(op.api_call, op.priority)

        # Schedule the timer
        timer_id = self.startTimer(wait * 1000 * 1.1)
        self.scheduled[timer_id] = op

    def timerEvent(self, event):
        """Do the operation scheduled by the given timer."""
        # Kill the timer and reschedule the op if necessary
        timer_id = event.timerId()
        self.killTimer(timer_id)
        op = self.scheduled.pop(timer_id)

        wait = self.mwsapi.request_wait(op.api_call, op.priority)
        if wait:
            self.schedule_op(op, wait)
            return

        # Handle the operation
        handler = getattr(self, op.op_name, None)
        if handler:
            self.status_message.emit('Processing: \'%s\', id=%i, priority=%i' % (op.op_name, op.id, op.priority))
            handler(op)
        else:
            self.status_message.emit("Warning: no method defined for operation '%s'" % op.op_name)

        if op.complete:
            self.operation_complete.emit(op.id)

        self.load_next(op.api_call)

    def ListMatchingProducts(self, op):
        """Query Amazon for products matching """
        self.mwsapi.ListMatchingProducts(priority=op.priority)
        op.complete = True
        self.dbsession.commit()

    def print_request(self, *args, **kwargs):
        #print(args, kwargs)
        pass