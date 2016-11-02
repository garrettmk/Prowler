from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QAbstractItemView, QDataWidgetMapper, QHeaderView
from PyQt5.QtSql import QSqlTableModel

from database import *

from abstractview import saquery_to_qtquery
from productview import ProductView
from amazondetails_ui import Ui_amazonViewDetails


class AmazonViewDetails(QWidget, Ui_amazonViewDetails):

    def __init__(self, parent=None):
        super(AmazonViewDetails, self).__init__(parent=parent)
        self.setupUi(self)

        self.titleLine.textChanged.connect(lambda: self.titleLine.home(False))

        # Set up the sources table
        self.sourcesTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sourcesTable.setSelectionMode(QAbstractItemView.SingleSelection)

        # Set up the price point table
        self.pricePointsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.pricePointsTable.setSelectionMode(QAbstractItemView.SingleSelection)


class AmazonView(ProductView):

    def __init__(self, parent=None):
        super(AmazonView, self).__init__(parent=parent)

        self.amz_listing = None
        self.vnd_listing = None

        # Create the details section
        self.detailTabs = AmazonViewDetails(self)
        self.layout().addWidget(self.detailTabs)

        # Create some shortcuts
        self.sourcesTable = self.detailTabs.sourcesTable
        self.pricePointsTable = self.detailTabs.pricePointsTable

        # Set up the sources model
        self.sourcesModel = QSqlTableModel(self)
        self.sourcesTable.setModel(self.sourcesModel)

        self.update_vendor_listings()

        self.sourcesTable.verticalHeader().hide()
        self.sourcesTable.horizontalHeader().setSectionHidden(0, True)
        self.sourcesTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.sourcesTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        # Set up the price point model
        self.pricesModel = QSqlTableModel(self)
        self.pricePointsTable.setModel(self.pricesModel)

        self.update_price_points()

        self.pricePointsTable.verticalHeader().hide()

        # Populate the table
        self.populate_source_box()
        self.show_listings()

        # Set up the data widget mapper
        mapper = QDataWidgetMapper(self)
        mapper.setModel(self.mainTable.model())
        self.mainTable.selectionModel().currentRowChanged.connect(mapper.setCurrentModelIndex)

        mapper.addMapping(self.detailTabs.titleLine, self.mainModel.fieldIndex('Description'))
        mapper.addMapping(self.detailTabs.brandLine, self.mainModel.fieldIndex('Brand'))
        mapper.addMapping(self.detailTabs.modelLine, self.mainModel.fieldIndex('Model'))
        mapper.addMapping(self.detailTabs.asinLine, self.mainModel.fieldIndex('ASIN'))
        mapper.addMapping(self.detailTabs.upcLine, self.mainModel.fieldIndex('UPC'))
        mapper.addMapping(self.detailTabs.categoryLine, self.mainModel.fieldIndex('Category'))
        mapper.addMapping(self.detailTabs.priceBox, self.mainModel.fieldIndex('Price'))
        mapper.addMapping(self.detailTabs.salesRankLine, self.mainModel.fieldIndex('Sales Rank'))

        # Connections
        self.mainTable.selectionModel().currentRowChanged.connect(self.product_changed)
        self.sourcesTable.selectionModel().currentRowChanged.connect(self.source_changed)

    def product_changed(self, current, previous):
        """Handle a change of selection in the main table. Updates the stored Amazon listing, and tells
        the vendor listing table and the price point table to update."""
        # Get the id of the currently selected listing
        source_idx = self.mainTable.model().mapToSource(current)
        id_idx = self.mainModel.index(source_idx.row(), self.mainModel.fieldIndex('id'))
        amz_id = self.mainModel.data(id_idx, Qt.DisplayRole)

        # Store the selected Amazon listing for use in other methods
        self.amz_listing = self.dbsession.query(AmazonListing).filter_by(id=amz_id).first()

        # Set the 'Amazon quantity' box on the Sourcing tab
        self.detailTabs.amzQuantityBox.setValue(self.amz_listing.quantity)

        # Update the vendor listing and price point tables
        self.vnd_listing = None
        self.calc_landed_cost()
        self.update_vendor_listings()
        self.update_price_points()

    def update_vendor_listings(self):
        """Populate the vendor listing table with listings linked to self.amz_listing."""
        if self.amz_listing is None:
            amz_id = None
        else:
            amz_id = self.amz_listing.id

        # Populate the vendor sources table
        stmt = self.dbsession.query(LinkedProducts.confidence, VendorListing, VendorListing.unit_price).\
                              filter(LinkedProducts.vnd_listing_id == VendorListing.id,
                                     LinkedProducts.amz_listing_id == amz_id).\
                              subquery()

        sa_query = self.dbsession.query(stmt.c.id.label('id'),
                                        stmt.c.confidence.label('Conf'),
                                        Vendor.name.label('Vendor'),
                                        stmt.c.sku.label('SKU'),
                                        stmt.c.price.label('Price'),
                                        stmt.c.quantity.label('Quantity'),
                                        stmt.c.unit_price.label('Unit Price')
                                        ).filter(Vendor.id == stmt.c.vendor_id)

        qt_query = saquery_to_qtquery(sa_query)
        qt_query.exec_()
        self.sourcesModel.setQuery(qt_query)
        self.sourcesModel.select()

    def source_changed(self, current, previous):
        """Handle a change of selection in the vendor listing table. Updates self.vnd_listing, and tells the
        price point table to update its calculations."""
        # Get the id of the currently selected vendor listing
        id_idx = self.sourcesModel.index(current.row(), self.mainModel.fieldIndex('id'))
        vnd_listing_id = self.sourcesModel.data(id_idx, Qt.DisplayRole)

        # Store the currently selected vendor listing for use in other methods
        self.vnd_listing = self.dbsession.query(VendorListing).filter_by(id=vnd_listing_id).first()

        # Update the landed cost and price points
        self.calc_landed_cost()
        self.update_price_points()

    def calc_landed_cost(self):
        """Recalculates the inventory cost box."""
        if self.amz_listing is None:
            self.detailTabs.costEachBox.setValue(0)
            return

        if self.vnd_listing is None:
            unit_price = 0
            tax_rate = 0
            shipping_in_rate = 0
        else:
            unit_price = self.vnd_listing.unit_price
            tax_rate = self.vnd_listing.vendor.tax_rate
            shipping_in_rate = self.vnd_listing.vendor.ship_rate

        amz_quant = self.amz_listing.quantity
        subtotal = unit_price * amz_quant

        tax = subtotal * tax_rate
        shipping_in = subtotal * shipping_in_rate

        subtotal += + tax + shipping_in

        packaging = self.detailTabs.packagingBox.value()
        shipping_out = self.detailTabs.shippingBox.value()

        total = subtotal + packaging + shipping_out

        self.detailTabs.costEachBox.setValue(total)

    def update_price_points(self):
        """Populate the price points table with entries related to self.amz_listing."""
        if self.amz_listing is None:
            amz_id = None
        else:
            amz_id = self.amz_listing.id

        landed_cost = self.detailTabs.costEachBox.value()

        stmt = self.dbsession.query(AmzPriceAndFees.price,
                                    AmzPriceAndFees.fba,
                                    label('profit', AmzPriceAndFees.price - AmzPriceAndFees.fba - landed_cost)).\
                              filter_by(amz_listing_id=amz_id).\
                              subquery()

        query = self.dbsession.query(stmt.c.price.label('Price'),
                                     stmt.c.fba.label('FBA fees'),
                                     stmt.c.profit.label('Profit'),
                                     label('Margin', func.printf('%.2f', stmt.c.profit / landed_cost)))

        qt_query = saquery_to_qtquery(query)
        qt_query.exec_()
        self.pricesModel.setQuery(qt_query)
        self.pricesModel.select()

    def is_amazon(self):
        return True

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
                                     ).filter(Vendor.id == VendorListing.vendor_id).\
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
        self.mainTable.horizontalHeader().setSectionResizeMode(self.mainModel.fieldIndex('Description'), QHeaderView.Stretch)
