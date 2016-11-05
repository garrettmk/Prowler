import webbrowser

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QAbstractItemView, QDataWidgetMapper, QHeaderView, QTabWidget, QHBoxLayout
from PyQt5.QtWidgets import QMessageBox, QAbstractSpinBox, QItemDelegate, QLineEdit, QFrame
from PyQt5.QtSql import QSqlTableModel

from database import *

from abstractview import saquery_to_qtquery
from productview import ProductView, ProductViewDetails
from amz_product_details_ui import Ui_amzProductDetails
from amz_product_history_ui import Ui_amzProductHistory


class DataMapperDelegate(QItemDelegate):

    def setEditorData(self, widget, index):
        data = index.data()

        if isinstance(widget, QAbstractSpinBox):
            if not data:
                widget.setValue(0)
            else:
                widget.setValue(data)
        elif isinstance(widget, QLineEdit):
            widget.setText(str(data))


class AmzProductDetailsWidget(ProductViewDetails, Ui_amzProductDetails):

    def __init__(self, parent=None):
        super(AmzProductDetailsWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.listing = None
        self.dbsession = Session()

        # Set up the model
        self.productModel = QSqlTableModel(self)
        self.set_listing(None)

        # Set up the UI
        self.titleLine.textChanged.connect(lambda: self.titleLine.home(False))
        self.brandLine.textChanged.connect(lambda: self.brandLine.home(False))
        self.modelLine.textChanged.connect(lambda: self.modelLine.home(False))
        self.categoryLine.textChanged.connect(lambda: self.categoryLine.home(False))

        # Set up the data widget mapper
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.productModel)
        self.mapper.setItemDelegate(DataMapperDelegate(self))

        self.mapper.addMapping(self.titleLine, self.productModel.fieldIndex('title'))
        self.mapper.addMapping(self.brandLine, self.productModel.fieldIndex('brand'))
        self.mapper.addMapping(self.modelLine, self.productModel.fieldIndex('model'))
        self.mapper.addMapping(self.asinLine, self.productModel.fieldIndex('sku'))
        self.mapper.addMapping(self.upcLine, self.productModel.fieldIndex('upc'))
        self.mapper.addMapping(self.priceBox, self.productModel.fieldIndex('price'))
        self.mapper.addMapping(self.quantityBox, self.productModel.fieldIndex('quantity'))
        self.mapper.addMapping(self.salesRankLine, self.productModel.fieldIndex('salesrank'))
        self.mapper.addMapping(self.offersBox, self.productModel.fieldIndex('offers'))
        self.mapper.addMapping(self.primeLine, self.productModel.fieldIndex('hasprime'))

        self.productModel.modelReset.connect(self.mapper.toFirst)

        # Connections
        self.openAmazonBtn.clicked.connect(self.open_listing_url)
        self.openGoogleBtn.clicked.connect(self.google_listing)
        self.openUPCLookupBtn.clicked.connect(self.upc_lookup)
        self.openCamelBtn.clicked.connect(self.open_camelcamelcamel)

    def set_listing(self, listing):
        self.listing = listing
        listing_id = listing.id if listing else None

        category = listing.category.name if listing else ''
        self.categoryLine.setText(category)

        query = self.dbsession.query(AmazonListing).filter_by(id=listing_id)
        qt_query = saquery_to_qtquery(query)
        qt_query.exec_()

        self.productModel.setQuery(qt_query)
        self.productModel.select()

    def open_camelcamelcamel(self):
        if self.listing is None:
            QMessageBox(self, 'Error', 'No listing selected.')
            return

        webbrowser.open('http://camelcamelcamel.com/search?sq=%s' % self.listing.sku)


class AmzProductHistoryWidget(QWidget, Ui_amzProductHistory):

    def __init__(self, parent=None):
        super(AmzProductHistoryWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.historyModel = QSqlTableModel(self)
        self.historyTable.setModel(self.historyModel)

        self.dbsession = Session()

        self.set_listing(None)

    def set_listing(self, listing):
        self.listing = listing
        amz_id = listing.id if listing else None

        query = self.dbsession.query(AmzProductHistory.timestamp.label('Date/Time'),
                                     AmzProductHistory.salesrank.label('Sales Rank'),
                                     AmzProductHistory.offers.label('Offers'),
                                     AmzProductHistory.hasprime.label('Prime'),
                                     AmazonMerchant.name.label('Merchant')).\
                                     filter_by(id=amz_id).\
                                     filter(AmazonMerchant.id == AmzProductHistory.merchant_id).\
                                     order_by(AmzProductHistory.timestamp.desc())

        qt_query = saquery_to_qtquery(query)
        qt_query.exec_()
        self.historyModel.setQuery(qt_query)
        self.historyModel.select()


class AmazonView(ProductView):

    def __init__(self, parent=None):
        super(AmazonView, self).__init__(parent=parent)

        self.amz_listing = None
        self.vnd_listing = None

        self.details = AmzProductDetailsWidget()
        self.history = AmzProductHistoryWidget()

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)

        details_layout = QHBoxLayout()
        details_layout.setContentsMargins(5, 0, 5, 5)
        details_layout.addWidget(self.details)
        details_layout.addWidget(line)
        details_layout.addWidget(self.history)

        details_widget = QWidget()
        details_widget.setLayout(details_layout)

        # Create the tabs
        self.tabs = QTabWidget(self)
        self.tabs.addTab(details_widget, 'Product Details')

        self.layout().addWidget(self.tabs)

        # Connections
        self.mainTable.selectionModel().currentRowChanged.connect(self.on_selection_change)

        # Populate the table
        self.show_listings()

    def is_amazon(self):
        return True

    def on_selection_change(self, current, previous):
        src_idx = self.mainTable.model().mapToSource(current)
        id_idx = self.mainModel.index(src_idx.row(), self.mainModel.fieldIndex('id'))
        amz_id = id_idx.data(Qt.DisplayRole)

        self.amz_listing = self.dbsession.query(AmazonListing).filter_by(id=amz_id).one()
        self.details.set_listing(self.amz_listing)
        self.history.set_listing(self.amz_listing)

    def show_listings(self, source=None):
        query = self.dbsession.query(AmazonListing.id,
                                     AmazonListing.sku.label('ASIN'),
                                     AmazonCategory.name.label('Category'),
                                     AmazonListing.salesrank.label('Sales Rank'),
                                     AmazonListing.brand.label('Brand'),
                                     AmazonListing.model.label('Model'),
                                     AmazonListing.quantity.label('Quantity'),
                                     AmazonListing.price.label('Price'),
                                     AmazonListing.title.label('Description'),
                                     AmazonListing.updated.label('Last Update')
                                     ).filter(Vendor.id == VendorListing.vendor_id). \
                                       filter(AmazonListing.category_id == AmazonCategory.id)

        if source and source != 'All Amazon products':
            # Is it a list name?
            list_id = self.dbsession.query(List.id).filter_by(name=source).scalar()
            if list_id:
                query = query.join(ListMembership).filter_by(list_id=list_id)

        qtquery = saquery_to_qtquery(query)
        qtquery.exec_()
        self.mainModel.setQuery(qtquery)
        self.mainModel.select()

        self.mainTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.mainTable.horizontalHeader().setSectionResizeMode(self.mainModel.fieldIndex('Description'),
                                                               QHeaderView.Stretch)




            # def product_changed(self, current, previous):
    #     """Handle a change of selection in the main table. Updates the stored Amazon listing, and tells
    #     the vendor listing table and the price point table to update."""
    #     # Get the id of the currently selected listing
    #     source_idx = self.mainTable.model().mapToSource(current)
    #     id_idx = self.mainModel.index(source_idx.row(), self.mainModel.fieldIndex('id'))
    #     amz_id = self.mainModel.data(id_idx, Qt.DisplayRole)
    #
    #     # Store the selected Amazon listing for use in other methods
    #     self.amz_listing = self.dbsession.query(AmazonListing).filter_by(id=amz_id).first()
    #
    #     # Set the 'Amazon quantity' box on the Sourcing tab
    #     self.detailTabs.amzQuantityBox.setValue(self.amz_listing.quantity)
    #
    #     # Update the vendor listing and price point tables
    #     self.vnd_listing = None
    #     self.calc_landed_cost()
    #     self.update_vendor_listings()
    #     self.update_price_points()
    #
    # def update_vendor_listings(self):
    #     """Populate the vendor listing table with listings linked to self.amz_listing."""
    #     if self.amz_listing is None:
    #         amz_id = None
    #     else:
    #         amz_id = self.amz_listing.id
    #
    #     # Populate the vendor sources table
    #     stmt = self.dbsession.query(LinkedProducts.confidence, VendorListing, VendorListing.unit_price).\
    #                           filter(LinkedProducts.vnd_listing_id == VendorListing.id,
    #                                  LinkedProducts.amz_listing_id == amz_id).\
    #                           subquery()
    #
    #     sa_query = self.dbsession.query(stmt.c.id.label('id'),
    #                                     stmt.c.confidence.label('Conf'),
    #                                     Vendor.name.label('Vendor'),
    #                                     stmt.c.sku.label('SKU'),
    #                                     stmt.c.price.label('Price'),
    #                                     stmt.c.quantity.label('Quantity'),
    #                                     stmt.c.unit_price.label('Unit Price')
    #                                     ).filter(Vendor.id == stmt.c.vendor_id)
    #
    #     qt_query = saquery_to_qtquery(sa_query)
    #     qt_query.exec_()
    #     self.sourcesModel.setQuery(qt_query)
    #     self.sourcesModel.select()
    #
    # def source_changed(self, current, previous):
    #     """Handle a change of selection in the vendor listing table. Updates self.vnd_listing, and tells the
    #     price point table to update its calculations."""
    #     # Get the id of the currently selected vendor listing
    #     id_idx = self.sourcesModel.index(current.row(), self.mainModel.fieldIndex('id'))
    #     vnd_listing_id = self.sourcesModel.data(id_idx, Qt.DisplayRole)
    #
    #     # Store the currently selected vendor listing for use in other methods
    #     self.vnd_listing = self.dbsession.query(VendorListing).filter_by(id=vnd_listing_id).first()
    #
    #     # Update the landed cost and price points
    #     self.calc_landed_cost()
    #     self.update_price_points()
    #
    # def calc_landed_cost(self):
    #     """Recalculates the inventory cost box."""
    #     if self.amz_listing is None:
    #         self.detailTabs.costEachBox.setValue(0)
    #         return
    #
    #     if self.vnd_listing is None:
    #         unit_price = 0
    #         tax_rate = 0
    #         shipping_in_rate = 0
    #     else:
    #         unit_price = self.vnd_listing.unit_price
    #         tax_rate = self.vnd_listing.vendor.tax_rate
    #         shipping_in_rate = self.vnd_listing.vendor.ship_rate
    #
    #     amz_quant = self.amz_listing.quantity
    #     subtotal = unit_price * amz_quant
    #
    #     tax = subtotal * tax_rate
    #     shipping_in = subtotal * shipping_in_rate
    #
    #     subtotal += + tax + shipping_in
    #
    #     packaging = self.detailTabs.packagingBox.value()
    #     shipping_out = self.detailTabs.shippingBox.value()
    #
    #     total = subtotal + packaging + shipping_out
    #
    #     self.detailTabs.costEachBox.setValue(total)
    #
    # def update_price_points(self):
    #     """Populate the price points table with entries related to self.amz_listing."""
    #     if self.amz_listing is None:
    #         amz_id = None
    #     else:
    #         amz_id = self.amz_listing.id
    #
    #     landed_cost = self.detailTabs.costEachBox.value()
    #
    #     stmt = self.dbsession.query(AmzPriceAndFees.price,
    #                                 AmzPriceAndFees.fba,
    #                                 label('profit', AmzPriceAndFees.price - AmzPriceAndFees.fba - landed_cost)).\
    #                           filter_by(amz_listing_id=amz_id).\
    #                           subquery()
    #
    #     query = self.dbsession.query(stmt.c.price.label('Price'),
    #                                  stmt.c.fba.label('FBA fees'),
    #                                  stmt.c.profit.label('Profit'),
    #                                  label('Margin', func.printf('%.2f', stmt.c.profit / landed_cost)))
    #
    #     qt_query = saquery_to_qtquery(query)
    #     qt_query.exec_()
    #     self.pricesModel.setQuery(qt_query)
    #     self.pricesModel.select()

