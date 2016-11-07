import webbrowser

from PyQt5.QtCore import Qt, QSortFilterProxyModel, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QAbstractItemView, QComboBox, QWidgetAction, QMenu, QMessageBox
from PyQt5.QtWidgets import QDataWidgetMapper, QHeaderView
from PyQt5.QtSql import QSqlTableModel

from delegates import DataMapperDelegate

from database import *

from abstractview import AbstractView, saquery_to_qtquery
from productview_ui import Ui_productView
from product_links_ui import Ui_listingLinks
from dialogs import SelectListDialog


class ProductDetailsWidget(QWidget):
    """Base class for the AmzProductDetailsWidget and VndProductDetailsWidget classes. Doesn't have it's own
    UI, but depends on certain UI elements (like self.titleLine) to be available. Make sure that self.setupUi()
    is called by inherited classes before the call to super().__init__()"""

    def __init__(self, parent=None):
        super(ProductDetailsWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.sel_listing = None
        self.dbsession = Session()

        # Set up the model
        self.productModel = QSqlTableModel(self)
        self.set_listing(None)

        ProductDetailsWidget.set_listing(self, None)

        # Set up the data widget mapper
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.productModel)
        self.mapper.setItemDelegate(DataMapperDelegate(self))
        self.mapper.currentIndexChanged.connect(self.lines_home)

        self.mapper.addMapping(self.titleLine, self.productModel.fieldIndex('title'))
        self.mapper.addMapping(self.brandLine, self.productModel.fieldIndex('brand'))
        self.mapper.addMapping(self.modelLine, self.productModel.fieldIndex('model'))
        self.mapper.addMapping(self.skuLine, self.productModel.fieldIndex('sku'))
        self.mapper.addMapping(self.upcLine, self.productModel.fieldIndex('upc'))
        self.mapper.addMapping(self.priceBox, self.productModel.fieldIndex('price'))
        self.mapper.addMapping(self.quantityBox, self.productModel.fieldIndex('quantity'))

        self.productModel.modelReset.connect(self.mapper.toFirst)

        # Connections
        self.openUrlBtn.clicked.connect(self.open_listing_url)
        self.openGoogleBtn.clicked.connect(self.google_listing)
        self.openUPCLookupBtn.clicked.connect(self.upc_lookup)

    def lines_home(self):
        """Reset text lines to home position."""
        self.titleLine.home(False)
        self.brandLine.home(False)
        self.modelLine.home(False)

    def set_listing(self, listing):
        """Set the widget's currently selected listing."""
        self.sel_listing = listing
        listing_id = listing.id if listing else None

        listing_type = VendorListing if isinstance(listing, VendorListing) else AmazonListing

        query = self.dbsession.query(listing_type).filter_by(id=listing_id)
        qt_query = saquery_to_qtquery(query)
        qt_query.exec_()

        self.productModel.setQuery(qt_query)
        self.productModel.select()

    def open_vendor(self):
        """Open a vendor info dialog."""

    def open_listing_url(self):
        """Open the listing's URL in a separate window."""
        if self.sel_listing is None or self.sel_listing.url is None:
            QMessageBox.information(self, 'Error', 'No URL available.')
            return

        webbrowser.open(self.sel_listing.url)

    def google_listing(self):
        """Search Google for the listing's brand and model."""
        if self.sel_listing is None \
            or self.sel_listing.brand is None \
            or self.sel_listing.model is None:
            QMessageBox.information(self, 'Error', 'No listing selected, or required information unavailable.')
            return

        q = '{} {}'.format(self.sel_listing.brand, self.sel_listing.model).replace(' ', '+')
        url = 'http://www.google.com/?gws_rd=ssl#q={}'.format(q)

        webbrowser.open(url)

    def upc_lookup(self):
        """Open a UPC lookup in a separate window."""
        if self.sel_listing is None \
            or self.sel_listing.upc is None:
            QMessageBox.information(self, 'Error', 'No listing selected, or no UPC code available.')
            return

        url = 'http://www.upcitemdb.com/upc/%s' % self.sel_listing.upc
        webbrowser.open(url)

    def delete_listing(self):
        """Delete the currently selected listing from the database."""


class ProductLinksWidget(QWidget, Ui_listingLinks):

    selection_changed = pyqtSignal()

    def __init__(self, parent=None):
        super(ProductLinksWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.parent_listing = None
        self.sel_listing = None
        self.dbsession = Session()

        # Set up the model and table
        self.linksModel = QSqlTableModel(self)
        self.linksTable.setModel(self.linksModel)
        self.linksTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.linksTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.linksTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.linksTable.setContextMenuPolicy(Qt.CustomContextMenu)

        self.linksTable.customContextMenuRequested.connect(self.context_menu)
        self.linksTable.selectionModel().currentRowChanged.connect(self.on_selection_change)

        # Populate
        self.set_listing(None)

        # More table setup
        self.linksTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.linksTable.horizontalHeader().setSectionResizeMode(self.linksModel.fieldIndex('Title'), QHeaderView.Stretch)
        self.linksTable.verticalHeader().hide()

        # Context menu actions
        self.context_menu = QMenu()
        self.context_menu.addActions([self.actionDelete_link])
        self.actionDelete_link.triggered.connect(self.delete_link)

    def set_listing(self, listing):
        """Set's the root listing. Overridden by subclasses."""
        self.parent_listing = listing
        self.sel_listing = None

    def on_selection_change(self, current, previous):
        """Update self.sel_listing"""
        id_idx = self.linksModel.index(current.row(), self.linksModel.fieldIndex('id'))
        listing_id = id_idx.data(Qt.DisplayRole)

        self.sel_listing = self.dbsession.query(Listing).filter_by(id=listing_id).first()
        self.selection_changed.emit()

    def context_menu(self, point):
        self.actionDelete_link.setEnabled(bool(self.sel_listing))

        point = self.linksTable.viewport().mapToGlobal(point)
        self.context_menu.popup(point)

    def delete_link(self):
        if isinstance(self.parent_listing, AmazonListing):
            sel_link = self.dbsession.query(LinkedProducts).filter_by(amz_listing_id=self.parent_listing.id,
                                                                      vnd_listing_id=self.sel_listing.id).\
                                                            one()
        elif isinstance(self.parent_listing, VendorListing):
            sel_link = self.dbsession.query(LinkedProducts).filter_by(amz_listing_id=self.sel_listing.id,
                                                                      vnd_listing_id=self.parent_listing.id).\
                                                            one()

        self.dbsession.delete(sel_link)
        self.dbsession.commit()
        self.set_listing(self.parent_listing)


class ProductView(AbstractView, Ui_productView):

    def __init__(self, parent=None):
        super(ProductView, self).__init__(parent=parent)
        self.setupUi(self)

        # Set up the main model and table
        self.mainModel = QSqlTableModel(self)
        sort_model = QSortFilterProxyModel(self)
        sort_model.setSourceModel(self.mainModel)

        self.mainTable.setModel(sort_model)
        self.mainTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.mainTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.mainTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.mainTable.setSortingEnabled(True)
        self.mainTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mainTable.customContextMenuRequested.connect(self.mainTable_context_menu)

        # Set up common toolbar actions
        self.sourceBox = QComboBox(self)
        sourceBoxAction = QWidgetAction(self)
        sourceBoxAction.setDefaultWidget(self.sourceBox)

        self.tool_buttons = [sourceBoxAction, self.actionReload, self.actionDelete_list]

        # Set up common context menu actions
        self.mainTable_context_actions = [self.actionAdd_to_list, self.actionRemove_from_list]

        # Default UI connections
        self.sourceBox.currentTextChanged.connect(self.show_listings)
        self.actionAdd_to_list.triggered.connect(self.action_add_to_list)
        self.actionRemove_from_list.triggered.connect(self.remove_from_list)
        self.actionReload.triggered.connect(self.show_listings)
        self.actionDelete_list.triggered.connect(self.delete_list)

    def is_amazon(self):
        """Helper method, returns True if this view shows Amazon products, False if vendor products."""
        return False

    def show_listings(self):
        """Overridden in subclasses: generates a query and populates the main table."""
        pass

    def populate_source_box(self):
        """Populate the source combo box with appropriate vendor and list names."""
        if self.is_amazon():
            vendornames = ['All Amazon products']
        else:
            vendornames = ['All Vendor products']
            vendornames.extend([result.name for result in self.dbsession.query(Vendor.name) if result.name != 'Amazon'])

        listnames = [result.name for result in self.dbsession.query(List.name).filter_by(is_amazon=self.is_amazon())]

        self.sourceBox.clear()
        self.sourceBox.addItems(vendornames)
        self.sourceBox.addItems(listnames)

    def maybe_enable_mainTable_actions(self):
        """Enable or disable context menu actions prior to showing the menu."""

    def mainTable_context_menu(self, point):
        """Popup a context menu on the main table, using the actions in self.mainTable_context_actions."""
        self.maybe_enable_mainTable_actions()

        menu = QMenu(self)
        menu.addActions(self.mainTable_context_actions)

        point = self.mainTable.viewport().mapToGlobal(point)
        menu.popup(point)

    def action_add_to_list(self):
        """Respond to the 'Add to List' menu action."""
        # Get the selected id's
        selection = self.mainTable.selectionModel().selectedRows()

        if not selection:
            return

        # Get the names of the lists already in the db
        list_names = [result.name for result in self.dbsession.query(List.name). \
            filter_by(is_amazon=self.is_amazon()). \
            all()]

        # Show the selection dialog
        dialog = SelectListDialog(list_names, parent=self)
        ok = dialog.exec()
        if not ok:
            return

        # Get the selected list, or create a new list
        sel_list = self.dbsession.query(List).filter_by(name=dialog.list_name).scalar()
        if sel_list is None:
            sel_list = List(name=dialog.list_name, is_amazon=self.is_amazon())
            self.dbsession.add(sel_list)

        # Add the selected id's to the selected list
        listing_ids = [index.data() for index in selection]
        for listing_id in listing_ids:
            membership = self.dbsession.query(ListMembership). \
                filter_by(list_id=sel_list.id, listing_id=listing_id). \
                first()
            if membership:
                continue
            else:
                membership = ListMembership(list=sel_list, listing_id=listing_id)
                self.dbsession.add(membership)

        self.dbsession.commit()
        self.populate_source_box()

    def remove_from_list(self):
        """Delete list memberships for the selected listings."""
        selection = self.mainTable.selectionModel().selectedRows()
        if not selection:
            return

        selected_ids = [index.data() for index in selection]

        # Get the set of list names common to all selected listings
        list_names_set = set()

        for listing_id in selected_ids:
            list_names = [result.name for result in self.dbsession.query(List.name).\
                                                                    join(ListMembership).\
                                                                    filter(ListMembership.listing_id==listing_id).\
                                                                    all()]
            list_names_set.update(list_names)

        # Show the selection dialog
        dialog = SelectListDialog(list_names_set, readonly=True, parent=self)
        ok = dialog.exec_()
        if not ok:
            return

        # Get the ID of the selected list
        list_id = self.dbsession.query(List.id).filter_by(name=dialog.list_name).scalar()

        # Delete the list memberships
        for listing_id in selected_ids:
            self.dbsession.query(ListMembership).filter_by(list_id=list_id, listing_id=listing_id).delete()

        self.dbsession.commit()
        self.show_listings()

    def delete_list(self):
        """Delete the currently selected list."""
        list_name = self.sourceBox.currentText()

        if list_name == 'All Amazon products' \
                or list_name == 'All Vendor products'\
                or list_name == 'Amazon':
            QMessageBox.information(self, 'Error', '\'%s\' cannot be deleted.' % list_name)
            return

        # Is it a vendor name?
        sel_source = self.dbsession.query(Vendor).filter_by(name=list_name).first()
        sel_source = sel_source or self.dbsession.query(List).filter_by(name=list_name).first()

        if isinstance(sel_source, Vendor):
            question = 'Delete all products from vendor \'%s\'?' % sel_source.name
        elif isinstance(sel_source, List):
            question = 'Delete list \'%s\'?' % sel_source.name

        answer = QMessageBox.question(self, 'Confirm', question)

        if answer == QMessageBox.Yes:
            self.dbsession.delete(sel_source)
            self.dbsession.commit()
            self.populate_source_box()
            self.show_listings()