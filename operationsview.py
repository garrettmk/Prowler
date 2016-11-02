from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox

from database import *
from operations import OperationsManager, Operation

from abstractview import AbstractView
from operationsview_ui import Ui_operationsView
from dialogs import OperationDialog


class OperationsView(AbstractView, Ui_operationsView):

    def __init__(self, parent=None):
        super(OperationsView, self).__init__(parent=parent)
        self.setupUi(self)
        self.tool_buttons = [self.actionStart, self.actionPause, self.actionNew_batch]

        # Connect to the operations manager
        self.opsman = OperationsManager.get_instance()
        self.opsman.status_message.connect(self.messageList.addItem)
        self.opsman.status_message.connect(self.messageList.scrollToBottom)

        self.actionStart.triggered.connect(self.opsman.start)
        self.actionPause.triggered.connect(self.opsman.stop)
        self.actionNew_batch.triggered.connect(self.new_batch_operation)

        self.update_counts()

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_counts)
        self.update_timer.start(5000)

    def update_counts(self):
        pending = self.dbsession.query(Operation).filter(and_(Operation.complete == False, Operation.error == False)).count()
        completed = self.dbsession.query(Operation).filter(Operation.complete == True).count()
        errors = self.dbsession.query(Operation).filter(Operation.error == True).count()

        # TODO: use api calls to calculate remaining time, not operation names
        est_time = 0
        for op_name in self.opsman.supported_ops:
            num = self.dbsession.query(Operation).\
                                 filter(and_(Operation.complete == False, Operation.error == False)).\
                                 filter(Operation.current_operation.like('%s%%' % op_name)).\
                                 count()

            est_time += num * self.opsman.mwsapi.throttle_limits(op_name).restore_rate

        self.pendingBox.setValue(pending)
        self.completedBox.setValue(completed)
        self.errorBox.setValue(errors)

        m, s = divmod(est_time, 60)
        h, m = divmod(m, 60)

        self.timeRemaining.setText('%d hr %d min %d sec' % (h, m, s))

    def new_batch_operation(self):
        dialog = OperationDialog(parent=self)
        ok = dialog.exec_()
        if not ok:
            return

        source = dialog.source

        # Determine the correct source
        if source == 'All Amazon products':
            query = self.dbsession.query(Listing).filter_by(vendor_id=0)
        elif source == 'All Vendor products':
            query = self.dbsession.query(Listing).filter(Listing.vendor_id != 0)
        else:
            vendor_id = self.dbsession.query(Vendor.id).filter_by(name=source).scalar()
            if vendor_id:
                query = self.dbsession.query(Listing).filter_by(vendor_id=vendor_id)
            else:
                list_id = self.dbsession.query(List.id).filter_by(name=source).scalar()
                if list_id is None:
                    QMessageBox.critical(self, 'Error', 'Source \'%s\' could not be found.' % source)
                    return
                query = self.dbsession.query(Listing).join(ListMembership).filter_by(list_id=list_id)

        if dialog.no_linked_products:
            query = query.filter(and_(~Listing.amz_links.any(), ~Listing.vnd_links.any()))

        if dialog.filter_price:
            query = query.filter(Listing.price.between(dialog.min_price, dialog.max_price))

        # Add to the operation table
        for row in query:
            op = Operation(listing_id=row.id)
            op.append(dialog.operation, dialog.params)
            self.dbsession.add(op)

        self.dbsession.commit()
        self.update_counts()
        self.actionStart.trigger()
