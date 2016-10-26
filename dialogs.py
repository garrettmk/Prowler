import arrow
import csv

from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox

from importcsv_ui import Ui_ImportCSV
from progressdialog_ui import Ui_progressDialog
from opsdialog_ui import Ui_opsDialog


class ImportCSVDialog(QDialog, Ui_ImportCSV):

    def __init__(self, parent=None, vendors=[]):
        super(ImportCSVDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.fileButton.clicked.connect(self.open_file)

        self.vendorBox.addItems(vendors)

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
                    self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
                    return

            # Count the rows. Also scan for errors
            try:
                rows = sum(1 for row in reader)
            except Exception as e:
                self.statusLabel.setText('Error: ' + str(e))
                self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
                return

            self.startBox.setValue(0)
            self.endBox.setValue(rows)

        self.statusLabel.setText('')
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

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


class OperationDialog(QDialog, Ui_opsDialog):

    def __init__(self, amz_sources=[], vnd_sources=[], amz_ops=[], vnd_ops=[], parent=None):
        super(OperationDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.amz_ops = amz_ops
        self.vnd_ops = vnd_ops

        # Populate the combo boxes
        self.amazonBox.addItems(amz_sources)
        self.vendorBox.addItems(vnd_sources)

        # UI connections
        self.selectAmazon.toggled.connect(self.amazonBox.setEnabled)
        self.selectVendor.toggled.connect(self.vendorBox.setEnabled)
        self.selectAmazon.toggled.connect(self.populate_ops_box)

        self.priceCheck.toggled.connect(self.priceFromBox.setEnabled)
        self.priceCheck.toggled.connect(self.priceToBox.setEnabled)
        self.priceCheck.toggled.connect(self.priceToLabel.setEnabled)

        self.lastUpdateCheck.toggled.connect(self.dateTimeEdit.setEnabled)

        # Set the initial state
        self.selectAmazon.setChecked(True)
        self.vendorBox.setEnabled(False)
        self.populate_ops_box()
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())

    def populate_ops_box(self):
        self.opsBox.clear()
        if self.selectAmazon.isChecked():
            self.opsBox.addItems(self.amz_ops)
        else:
            self.opsBox.addItems(self.vnd_ops)

    @property
    def source(self):
        if self.selectAmazon.isChecked():
            return 'Amazon', self.amazonBox.currentText()
        else:
            return 'Vendor', self.vendorBox.currentText()

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
        return self.opsBox.currentText()
