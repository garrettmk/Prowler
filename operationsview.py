from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox, QWidget

from database import *
from operations import OperationsManager, Operation

from baseview import BaseView
from operationsview_ui import Ui_operationsView
from dialogs import OperationDialog


class OperationsView(BaseView, Ui_operationsView):

    def __init__(self, parent=None):
        super(OperationsView, self).__init__(parent=parent)
        self.setupUi(self)

        self.add_toolbar_actions([self.actionStart, self.actionPause, self.actionNew_batch])

        # Connections
        self.clearPendingBtn.clicked.connect(self.on_clear_pending)
        self.clearCompletedBtn.clicked.connect(self.on_clear_completed)
        self.clearErrorsBtn.clicked.connect(self.on_clear_errors)

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

        est_time = 0
        for op_name in self.opsman.supported_ops:
            num = self.dbsession.query(Operation).\
                                 filter(and_(Operation.complete == False, Operation.error == False)).\
                                 filter(Operation.operation == op_name).\
                                 count()

            est_time += num * self.opsman.get_wait(op_name, -1)

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
        if source == 'All Vendor products':
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
            op = Operation.GenericOperation(operation=dialog.operation,
                                            params=dialog.params,
                                            listing_id=row.id)
            self.dbsession.add(op)

        self.dbsession.commit()
        self.update_counts()

    def on_clear_pending(self):
        if QMessageBox.question(self, 'Confirm', 'Delete all pending operations?') == QMessageBox.Yes:
            self.dbsession.query(Operation).filter_by(complete=False, error=False).delete()
            self.dbsession.commit()
            self.update_counts()

    def on_clear_completed(self):
        if QMessageBox.question(self, 'Confirm', 'Delete all completed operations?') == QMessageBox.Yes:
            self.dbsession.query(Operation).filter_by(complete=True, error=False).delete()
            self.dbsession.commit()
            self.update_counts()

    def on_clear_errors(self):
        if QMessageBox.question(self, 'Confirm', 'Delete all failed operations?') == QMessageBox.Yes:
            self.dbsession.query(Operation).filter_by(error=True).delete()
            self.dbsession.commit()
            self.update_counts()
