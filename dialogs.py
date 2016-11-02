import csv
from collections import OrderedDict
from itertools import chain

import arrow
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox
from PyQt5.QtWidgets import QWidget
from database import *
from selectlist_ui import Ui_selectListDialog
from importcsv_ui import Ui_ImportCSV
from listmatchingproducts_params_ui import Ui_listMatchingProductsParams
from opsdialog_ui import Ui_opsDialog
from progressdialog_ui import Ui_progressDialog

class ImportCSVDialog(QDialog, Ui_ImportCSV):

    def __init__(self, parent=None, vendors=[]):
        super(ImportCSVDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.vendorBox.addItems(vendors)
        self.okbutton = self.buttonBox.button(QDialogButtonBox.Ok)

        self.fileButton.clicked.connect(self.open_file)
        self.vendorBox.currentTextChanged.connect(self.maybe_enable_ok)

        self.okbutton.setEnabled(False)
        self.file_is_ok = False

    def maybe_enable_ok(self):
        if self.file_is_ok and self.vendorBox.currentText():
            self.okbutton.setEnabled(True)
        else:
            self.okbutton.setEnabled(False)

    def open_file(self):
        filename, ftype = QFileDialog.getOpenFileName(self, caption='Open CSV', filter='CSV Files (*.csv)')
        if not filename:
            return

        self.fileLine.setText(filename)

        req_fields = ['Brand', 'Model', 'Quantity', 'Price']

        with open(filename) as file:
            reader = csv.DictReader(file)

            for field in req_fields:
                if field not in reader.fieldnames:
                    self.statusLabel.setText('File does not contain all required fields: ' + ', '.join(req_fields))
                    self.okbutton.setEnabled(False)
                    self.file_is_ok = False
                    return

            # Count the rows. Also scan for errors
            try:
                rows = sum(1 for row in reader)
            except Exception as e:
                self.statusLabel.setText('Error: ' + str(e))
                self.okbutton.setEnabled(False)
                self.file_is_ok = False
                return

            self.startBox.setValue(0)
            self.endBox.setValue(rows)

        self.statusLabel.setText('')
        self.file_is_ok = True
        self.maybe_enable_ok()

    @property
    def filename(self):
        return self.fileLine.text()

    @property
    def startrow(self):
        return self.startBox.value()

    @property
    def endrow(self):
        return self.endBox.value()

    @property
    def vendorname(self):
        return self.vendorBox.currentText()


class ProgressDialog(QDialog, Ui_progressDialog):

    def __init__(self, text='', minimum=0, maximum=100, parent=None):
        super(ProgressDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.setResult(QDialog.Accepted)
        self.status_text = text
        self.progress_min = minimum
        self.progress_max = maximum

    @property
    def status_text(self):
        return self.statusLabel.text()

    @status_text.setter
    def status_text(self, value):
        self.statusLabel.setText(value)

    @property
    def progress_min(self):
        return self.progressBar.minimum()

    @progress_min.setter
    def progress_min(self, value):
        self.progressBar.setMinimum(value)

    @property
    def progress_max(self):
        return self.progressBar.maximum()

    @progress_max.setter
    def progress_max(self, value):
        self.progressBar.setMaximum(value)

    @property
    def progress_value(self):
        return self.progressBar.value()

    @progress_value.setter
    def progress_value(self, value):
        self.progressBar.setValue(value)


class ListMatchingProductsParameters(QWidget, Ui_listMatchingProductsParams):

    def __init__(self, parent=None):
        super(ListMatchingProductsParameters, self).__init__(parent=parent)
        self.setupUi(self)

    @property
    def params(self):
        params = {}

        params['linkif'] = {'conf': self.confidenceBox.value()}
        params['priceif'] = {'salesrank': self.salesRankBox.value()}
        params['feesif'] = {'priceratio': '%.2f' % (self.differenceBox.value() / 100)}

        return params


class OperationDialog(QDialog, Ui_opsDialog):

    def __init__(self, parent=None):
        super(OperationDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.dbsession = Session()

        # Set up the operations list and parameter widgets
        self.amz_ops = OrderedDict()
        self.amz_ops['GetLowestOfferListingsForASIN'] = QWidget()
        self.amz_ops['GetMyFeesEstimate'] = QWidget()

        self.vnd_ops = OrderedDict()
        self.vnd_ops['ListMatchingProducts'] = ListMatchingProductsParameters()

        for key, widget in chain(self.amz_ops.items(), self.vnd_ops.items()):
            self.paramsStack.addWidget(widget)

        # Populate the source combo box
        self.amz_srcs = []
        self.vnd_srcs = []

        for result in self.dbsession.query(List).all():
            if result.is_amazon:
                self.amz_srcs.append(result.name)
            else:
                self.vnd_srcs.append(result.name)

        self.vnd_srcs.extend([result.name for result in self.dbsession.query(Vendor.name).\
                                                                       filter(Vendor.id != 0).\
                                                                       all()])
        self.amz_srcs.insert(0, 'All Amazon products')
        self.vnd_srcs.insert(0, 'All Vendor products')

        # Populate the combo boxes
        self.sourceBox.addItems(self.amz_srcs)
        self.sourceBox.addItems(self.vnd_srcs)

        # UI connections
        self.sourceBox.currentIndexChanged.connect(self.populate_ops_box)
        self.opsBox.currentTextChanged.connect(self.show_parameters)

        self.priceCheck.toggled.connect(self.priceFromBox.setEnabled)
        self.priceCheck.toggled.connect(self.priceToBox.setEnabled)
        self.priceCheck.toggled.connect(self.priceToLabel.setEnabled)

        self.lastUpdateCheck.toggled.connect(self.dateTimeEdit.setEnabled)

        # Set the initial state
        self.populate_ops_box()
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())

    def populate_ops_box(self):
        self.opsBox.clear()
        if self.sourceBox.currentIndex() < len(self.amz_srcs):
            self.opsBox.addItems(self.amz_ops.keys())
        else:
            self.opsBox.addItems(self.vnd_ops.keys())

    def show_parameters(self, op_name):
        if op_name in self.amz_ops:
            self.paramsStack.setCurrentWidget(self.amz_ops[op_name])
        elif op_name in self.vnd_ops:
            self.paramsStack.setCurrentWidget(self.vnd_ops[op_name])

    @property
    def source(self):
        return self.sourceBox.currentText()

    @property
    def no_linked_products(self):
        return self.noLinksCheck.isChecked()

    @property
    def filter_price(self):
        return self.priceCheck.isChecked()

    @property
    def min_price(self):
        return self.priceFromBox.value()

    @property
    def max_price(self):
        return self.priceToBox.value()

    @property
    def filter_last_update(self):
        return self.lastUpdateCheck.isChecked()

    @property
    def last_update_datetime(self):
        qdatetime = self.dateTimeEdit.dateTime()
        return arrow.get(qdatetime.toTime_t())

    @property
    def operation(self):
        op_name = self.opsBox.currentText()
        return op_name

    @property
    def params(self):
        # Get the current parameter widget
        param_widget = self.paramsStack.currentWidget()
        try:
            params = param_widget.params
        except AttributeError:
            params = {}

        return params


class SelectListDialog(QDialog, Ui_selectListDialog):

    def __init__(self, list_names=None, parent=None):
        super(SelectListDialog, self).__init__(parent=parent)
        self.setupUi(self)

        if list_names:
            self.listNameBox.addItems(list_names)

    @property
    def list_name(self):
        return self.listNameBox.currentText()