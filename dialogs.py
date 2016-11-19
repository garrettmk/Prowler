import arrow
import csv

from collections import OrderedDict
from itertools import chain

from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox, QMessageBox, QHeaderView
from PyQt5.QtWidgets import QWidget
from PyQt5.QtSql import QSqlTableModel

from database import *

from selectlist_ui import Ui_selectListDialog
from importcsv_ui import Ui_ImportCSV
from findamazonmatches_params_ui import Ui_listMatchingProductsParams
from testmargins_params_ui import Ui_testMarginsParams
from opsdialog_ui import Ui_opsDialog
from progressdialog_ui import Ui_progressDialog
from vnd_product_dialog_ui import Ui_vndProductDialog
from search_amazon_dialog_ui import Ui_searchAmazonDialog
from search_listings_dialog_ui import Ui_searchListingsDialog
from watch_dialog_ui import Ui_setWatchDialog
from edit_vendor_ui import Ui_editVendorDialog


class ImportCSVDialog(QDialog, Ui_ImportCSV):
    """A dialog for selecting a CSV file to import from."""

    def __init__(self, parent=None):
        """Initialize the dialog."""
        super(ImportCSVDialog, self).__init__(parent=parent)
        self.setupUi(self)

        session = Session()

        # Populate vendor names
        vendor_names = [result.name for result in session.query(Vendor.name).filter(Vendor.name != 'Amazon')]
        self.vendorBox.addItems(vendor_names)

        # Populate list names
        list_names = [result.name for result in session.query(List.name).filter(List.is_amazon == False)]
        self.listBox.addItems(list_names)

        # Shortcut to the OK button
        self.okbutton = self.buttonBox.button(QDialogButtonBox.Ok)

        # Connections
        self.fileButton.clicked.connect(self.open_file)
        self.vendorBox.currentTextChanged.connect(self.maybe_enable_ok)

        # Set the initial state
        self.okbutton.setEnabled(False)
        self.file_is_ok = False

    def maybe_enable_ok(self):
        """Enable or disable the OK button based on the current state of the form."""
        c1 = self.file_is_ok
        c2 = self.vendorBox.currentText()
        c3 = (self.addToListCheck.isChecked() and self.listBox.currentText()) or not self.addToListCheck.isChecked()

        self.okbutton.setEnabled(bool(c1 and c2 and c3))

    def open_file(self):
        """Respond to the 'Open File' action. """
        filename, ftype = QFileDialog.getOpenFileName(self, caption='Open CSV', filter='CSV Files (*.csv)')
        if not filename:
            return

        self.fileLine.setText(filename)

        req_fields = ['brand', 'model', 'quantity', 'price', 'sku']

        with open(filename) as file:
            reader = csv.DictReader(file)

            # Make sure the file contains the required fields
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
        """Return the path of the selected file."""
        return self.fileLine.text()

    @property
    def startrow(self):
        """Return the value of the 'start row' spin box."""
        return self.startBox.value()

    @property
    def endrow(self):
        """Return the value of the 'end row' spin box."""
        return self.endBox.value()

    @property
    def vendorname(self):
        """Return the name of the vendor to import into."""
        return self.vendorBox.currentText()

    @property
    def list_name(self):
        """Return the name of the list to import into."""
        if self.addToListCheck.isChecked() and self.listBox.currentText():
            return self.listBox.currentText()
        else:
            return None


class ProgressDialog(QDialog, Ui_progressDialog):
    """A dialog for showing a progress bar."""

    def __init__(self, text='', minimum=0, maximum=100, parent=None):
        """Initialize the dialog."""
        super(ProgressDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.setResult(QDialog.Accepted)
        self.status_text = text
        self.progress_min = minimum
        self.progress_max = maximum

    @property
    def status_text(self):
        """Return text in the status label."""
        return self.statusLabel.text()

    @status_text.setter
    def status_text(self, value):
        """Set the text of the status label."""
        self.statusLabel.setText(value)

    @property
    def progress_min(self):
        """Return the progress bar's minimum value."""
        return self.progressBar.minimum()

    @progress_min.setter
    def progress_min(self, value):
        """Set the progress bar's minimum value."""
        self.progressBar.setMinimum(value)

    @property
    def progress_max(self):
        """Return the progress bar's maximum value."""
        return self.progressBar.maximum()

    @progress_max.setter
    def progress_max(self, value):
        """Set the progress bar's maximum value."""
        self.progressBar.setMaximum(value)

    @property
    def progress_value(self):
        """Return the progress bar's current value."""
        return self.progressBar.value()

    @progress_value.setter
    def progress_value(self, value):
        """Set the progress bar's current value."""
        self.progressBar.setValue(value)


class OperationParametersWidget(QWidget):
    """A base class for widgets that specify operation parameters."""

    def __init__(self, parent=None):
        """Initialize the widget."""
        super(OperationParametersWidget, self).__init__(parent=parent)

    @property
    def params(self):
        """Return the parameters as a dictionary."""
        return {}


class FindAmazonMatchesParams(OperationParametersWidget, Ui_listMatchingProductsParams):
    """A widget for specifying operations for the FindAmazonMatches operation."""

    def __init__(self, parent=None):
        """Initialize the widget."""
        super(FindAmazonMatchesParams, self).__init__(parent=parent)
        self.setupUi(self)

        session = Session()

        list_names = [result.name for result in session.query(List.name).filter_by(is_amazon=True).all()]
        self.listNamesBox.addItems(list_names)

        self.testMarginsCheck.stateChanged.connect(self.listNamesBox.setEnabled)

    @property
    def params(self):
        """Return the selected parameters as a dictionary."""
        params = {}

        params['linkif'] = {'conf': self.confidenceBox.value()}

        if self.testMarginsCheck.isChecked():
            testmargins_params = {}
            testmargins_params['salesrank'] = self.salesRankBox.value()
            testmargins_params['list'] = self.listNamesBox.currentText()
            testmargins_params['threshold'] = self.marginBox.value() / 100
            params['testmargins'] = testmargins_params

        return params


class TestMarginsParams(OperationParametersWidget, Ui_testMarginsParams):
    """A widget for specifying parameters for the TestMargins operation."""

    def __init__(self, parent=None):
        """Initialize the widget."""
        super(TestMarginsParams, self).__init__(parent=parent)
        self.setupUi(self)

        session = Session()

        list_names = [result.name for result in session.query(List.name).filter_by(is_amazon=True).all()]
        self.listBox.addItems(list_names)

    @property
    def params(self):
        """Return the selected parameters as a dictionary."""
        params = {}

        params['confidence'] = self.confidenceBox.value()
        params['threshold'] = self.marginBox.value() / 100
        params['list'] = self.listBox.currentText()

        return params


class OperationDialog(QDialog, Ui_opsDialog):
    """A dialog for specifying bulk operation parameters. A custom widget (like TestMarginsParams) must be used
    in order to specify custom parameters.
    """

    def __init__(self, parent=None):
        """Initialize the dialog."""
        super(OperationDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.dbsession = Session()

        # Set up the operations list and parameter widgets
        self.amz_ops = OrderedDict()
        self.amz_ops['TestMargins'] = TestMarginsParams()
        self.amz_ops['ItemLookup'] = OperationParametersWidget()
        self.amz_ops['GetMyFeesEstimate'] = OperationParametersWidget()
        self.amz_ops['UpdateAmazonListing'] = OperationParametersWidget()

        self.vnd_ops = OrderedDict()
        self.vnd_ops['FindAmazonMatches'] = FindAmazonMatchesParams()

        for key, widget in chain(self.amz_ops.items(), self.vnd_ops.items()):
            self.paramsStack.addWidget(widget)

        # Populate the source combo box
        self.amz_srcs = ['Amazon']
        self.vnd_srcs = ['All vendor products']

        for result in self.dbsession.query(List).all():
            if result.is_amazon:
                self.amz_srcs.append(result.name)
            else:
                self.vnd_srcs.append(result.name)

        self.vnd_srcs.extend([result.name for result in self.dbsession.query(Vendor.name).\
                                                                       filter(Vendor.name != 'Amazon').\
                                                                       all()])

        # Populate the combo boxes
        self.sourceBox.addItems(self.amz_srcs)
        self.sourceBox.insertSeparator(len(self.amz_srcs))
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
        """Clear the operations combo and re-populate with either Amazon-compatible or Vendor-compatible operation
        names.
        """
        self.opsBox.clear()
        if self.sourceBox.currentIndex() < len(self.amz_srcs):
            self.opsBox.addItems(self.amz_ops.keys())
        else:
            self.opsBox.addItems(self.vnd_ops.keys())

    def show_parameters(self, op_name):
        """Show that parameters widget for the specified operation."""
        if op_name in self.amz_ops:
            self.paramsStack.setCurrentWidget(self.amz_ops[op_name])
        elif op_name in self.vnd_ops:
            self.paramsStack.setCurrentWidget(self.vnd_ops[op_name])

    @property
    def source(self):
        """Return the name of the selected source."""
        return self.sourceBox.currentText()

    @property
    def no_linked_products(self):
        """Return the state of the 'No Linked Products' filter check."""
        return self.noLinksCheck.isChecked()

    @property
    def filter_price(self):
        """Return the state of the 'filter on price' checkbox."""
        return self.priceCheck.isChecked()

    @property
    def min_price(self):
        """Return the value of the 'minimum price' spin box."""
        return self.priceFromBox.value()

    @property
    def max_price(self):
        """Return the value of the 'maximum price' spin box."""
        return self.priceToBox.value()

    @property
    def filter_last_update(self):
        """Return the state of the 'last updated' filter check box."""
        return self.lastUpdateCheck.isChecked()

    @property
    def last_update_datetime(self):
        """Return the value in the 'last updated' datetime editor."""
        qdatetime = self.dateTimeEdit.dateTime()
        return arrow.get(qdatetime.toTime_t())

    @property
    def operation(self):
        """Return the name of the selected operation."""
        op_name = self.opsBox.currentText()
        return op_name

    @property
    def params(self):
        """Return a dictionary of parameters for the selected operation."""
        # Get the current parameter widget
        param_widget = self.paramsStack.currentWidget()
        return param_widget.params


class SelectListDialog(QDialog, Ui_selectListDialog):
    """A simple dialog for specifying a list name."""

    def __init__(self, show_amazon=False, readonly=False, parent=None):
        """Initialize the dialog. If show_amazon is True, show only lists of Amazon listings. If readonly is True,
        disable editing in the list name combo box.
        """
        super(SelectListDialog, self).__init__(parent=parent)
        self.setupUi(self)

        session = Session()

        list_names = [result.name for result in session.query(List.name).filter_by(is_amazon=show_amazon)]
        self.listNameBox.addItems(list_names)

        self.listNameBox.setEditable(not readonly)

    @property
    def list_name(self):
        """Return the text of the list name combo box."""
        return self.listNameBox.currentText()


class VndProductDialog(QDialog, Ui_vndProductDialog):
    """A dialog for viewing/editing a single VendorListing."""

    def __init__(self, listing=None, parent=None):
        """Initialize the widgets. Set the current widget to listing, if provided. If listing is None, assume
        that we are creating a new listing.
        """
        super(VndProductDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.dbsession = Session()
        self.listing = listing

        # Connections
        self.titleLine.textChanged.connect(self.maybe_enable_ok)
        self.brandLine.textChanged.connect(self.maybe_enable_ok)
        self.modelLine.textChanged.connect(self.maybe_enable_ok)
        self.skuLine.textChanged.connect(self.maybe_enable_ok)
        self.vendorBox.currentTextChanged.connect(self.maybe_enable_ok)
        self.accepted.connect(self.update_listing)

        # Initialize values
        self.titleLine.setText(getattr(listing, 'title', ''))
        self.urlLine.setText(getattr(listing, 'url', ''))
        self.brandLine.setText(getattr(listing, 'brand', ''))
        self.modelLine.setText(getattr(listing, 'model', ''))
        self.skuLine.setText(getattr(listing, 'sku', ''))
        self.upcLine.setText(str(getattr(listing, 'upc', '')))
        self.priceBox.setValue(getattr(listing, 'price', 0))
        self.quantityBox.setValue(getattr(listing, 'quantity', 1))

        vendor_names = [result.name for result in self.dbsession.query(Vendor.name).\
                                                                 filter(Vendor.name != 'Amazon').\
                                                                 all()]
        self.vendorBox.addItems(vendor_names)

        if hasattr(listing, 'vendor'):
            self.vendorBox.setCurrentText(listing.vendor.name)

    def maybe_enable_ok(self):
        """Enable the OK button if the conditions are met."""
        if self.titleLine.text() \
            and self.brandLine.text() \
                and self.modelLine.text() \
                    and self.skuLine.text() \
                        and self.vendorBox.currentText():

            prior = self.dbsession.query(VendorListing.id).\
                                   join(Vendor).\
                                   filter(VendorListing.sku == self.skuLine.text(),
                                          Vendor.name == self.vendorBox.currentText()).\
                                   first()

            if prior and (self.listing is None or self.listing.id != prior.id):
                decision = False
            else:
                decision = True
        else:
            decision = False

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(decision)

    def update_listing(self):
        """Update the current listing with the information in the widgets."""
        # Get or create the vendor
        vendor = self.dbsession.query(Vendor).filter_by(name=self.vendorBox.currentText()).first()
        if vendor is None:
            vendor = Vendor(name=self.vendorBox.currentText())

        if self.listing is None:
            self.listing = VendorListing()
            self.dbsession.add(self.listing)

        self.listing.vendor = vendor
        self.listing.sku = self.skuLine.text()
        self.listing.title = self.titleLine.text()
        self.listing.brand = self.brandLine.text()
        self.listing.model = self.modelLine.text()
        self.listing.upc = self.upcLine.text()
        self.listing.quantity = self.quantityBox.value()
        self.listing.price = self.priceBox.value()
        self.listing.url = self.urlLine.text()

        self.dbsession.commit()


class SearchAmazonDialog(QDialog, Ui_searchAmazonDialog):
    """A simple dialog for starting a SearchAmazon operation and storing the results in a list."""

    def __init__(self, parent=None):
        """Initialize the widgets."""
        super(SearchAmazonDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.dbsession = Session()

        self.searchLine.textChanged.connect(self.maybe_enable_ok)
        self.listBox.currentTextChanged.connect(self.maybe_enable_ok)

        list_names = [result.name for result in self.dbsession.query(List.name).filter_by(is_amazon=True).all()]
        self.listBox.addItems(list_names)

        self.maybe_enable_ok()

    def maybe_enable_ok(self):
        """Enable the OK button if the conditions are met."""
        enabled = bool(self.searchLine.text()) and bool(self.listBox.currentText())
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enabled)

    @property
    def list_name(self):
        """Return the name of the list to store results in."""
        return self.listBox.currentText()

    @property
    def search_terms(self):
        """Return the search terms."""
        return self.searchLine.text()


class SearchListingsDialog(QDialog, Ui_searchListingsDialog):
    """A dialog for doing quick searches of the database and selecting the results."""

    def __init__(self, show_amazon=False, parent=None):
        """Initialize the widgets. show_amazon specifies whether the dialog should show Amazon listings, or
        Vendor listings.
        """
        super(SearchListingsDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.amazon = show_amazon
        self.dbsession = Session()

        # Populate the sources combo box
        condition = Vendor.name == 'Amazon' if show_amazon else Vendor.name != 'Amazon'

        vendor_names = [result.name for result in self.dbsession.query(Vendor.name).filter(condition)]
        list_names = [result.name for result in self.dbsession.query(List.name).filter(List.is_amazon == show_amazon)]

        if not show_amazon:
            vendor_names.insert(0, 'All Vendor products')

        self.sourceBox.addItems(vendor_names)
        self.sourceBox.addItems(list_names)

        # Set up the main table and model
        self.resultsModel = QSqlTableModel(self)
        self.resultsTable.setModel(self.resultsModel)

        # Populate the table headers
        self.search()

        # More table set up
        self.resultsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.resultsTable.horizontalHeader().setSectionResizeMode(self.resultsModel.fieldIndex('Title'), QHeaderView.Stretch)
        self.resultsTable.horizontalHeader().setSectionHidden(self.resultsModel.fieldIndex('id'), True)

        # Connections
        self.searchButton.clicked.connect(self.search)

    def search(self):
        """Search the database and populate the results table."""
        keywords = self.keywordsLine.text() or 'abcdefghijklmnop123456789'
        keywords = keywords.split()

        brand_clauses = or_(*[Listing.brand.contains(term) for term in keywords])
        model_clauses = or_(*[Listing.model.contains(term) for term in keywords])
        title_clauses = or_(*[Listing.title.contains(term) for term in keywords])

        query = self.dbsession.query(Listing.id.label('id'),
                                     Vendor.name.label('Vendor'),
                                     Listing.sku.label('SKU'),
                                     Listing.brand.label('Brand'),
                                     Listing.model.label('Model'),
                                     Listing.title.label('Title')).\
                                filter(Vendor.id == Listing.vendor_id,
                                       or_(brand_clauses, model_clauses, title_clauses))

        source_name = self.sourceBox.currentText()
        if source_name == 'All Vendor products':
            query = query.filter(Vendor.id > 0)
        else:
            # Is it a vendor name?
            vendor_id = self.dbsession.query(Vendor.id).filter_by(name=source_name).scalar()
            if vendor_id:
                query = query.filter_by(vendor_id=vendor_id)
            else:
                # Is it a list name?
                list_id = self.dbsession.query(List.id).filter_by(name=source_name).scalar()
                if list_id:
                    query = query.join(ListMembership).filter_by(list_id=list_id)

        qt_query = saquery_to_qtquery(query)
        qt_query.exec_()
        self.resultsModel.setQuery(qt_query)
        self.resultsModel.select()

    def keyPressEvent(self, event):
        """Override the return key to perform a search, instead of accepting the dialog."""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            event.accept()
            self.search()

    @property
    def selected_ids(self):
        """Return the IDs of the selected results."""
        selection = self.resultsTable.selectionModel().selectedRows()
        return [idx.data() for idx in selection]


class SetWatchDialog(QDialog, Ui_setWatchDialog):
    """A simple dialog for specifying watch conditions."""

    def __init__(self, parent=None):
        super(SetWatchDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.watchBtn.toggled.connect(self.periodBox.setEnabled)

    @property
    def has_watch(self):
        """Return True if the listings should have a watch."""
        return bool(self.watchBtn.isChecked())

    @property
    def period(self):
        """Return the selected watch period, in hours."""
        return self.periodBox.value()


class EditVendorDialog(QDialog, Ui_editVendorDialog):
    """A dialog that provides viewing and editing for Vendor features."""

    def __init__(self, default=None, parent=None):
        """Initialize the widgets with info from the vendor specified by default. Default is a name."""
        super(EditVendorDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.dbsession = Session()
        self.selected_vendor = None

        # Fill in the vendor names
        vendor_names = [result.name for result in self.dbsession.query(Vendor.name).filter(Vendor.name != 'Amazon')]
        self.vendorBox.addItems(vendor_names)

        # Connections
        self.accepted.connect(self.update_vendor)
        self.vendorBox.currentTextChanged.connect(self.update_vendor)
        self.vendorBox.currentTextChanged.connect(self.on_vendor_changed)

        # Initialize
        if default:
            self.vendorBox.setCurrentText(default)
        else:
            self.vendorBox.setCurrentIndex(0)
            self.on_vendor_changed()

    def on_vendor_changed(self):
        """Update the widgets with the info from the newly selected vendor."""
        self.selected_vendor = self.dbsession.query(Vendor).filter_by(name=self.vendorBox.currentText()).first()

        self.nameLine.setText(self.selected_vendor.name)
        self.urlLine.setText(self.selected_vendor.url)
        self.taxBox.setValue(self.selected_vendor.tax_rate * 100)
        self.shippingBox.setValue(self.selected_vendor.ship_rate * 100)

    def update_vendor(self):
        """Updates the selected vendor with the info from the widgets."""
        if self.selected_vendor is None:
            return

        self.selected_vendor.name = self.nameLine.text()
        self.selected_vendor.url = self.urlLine.text()
        self.selected_vendor.tax_rate = self.taxBox.value() / 100
        self.selected_vendor.ship_rate = self.shippingBox.value() / 100
