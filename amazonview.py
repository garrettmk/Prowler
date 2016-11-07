import webbrowser

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QAbstractItemView, QDataWidgetMapper, QHeaderView, QTabWidget, QHBoxLayout
from PyQt5.QtWidgets import QMessageBox, QAbstractSpinBox, QItemDelegate, QLineEdit, QFrame, QMenu, QAction
from PyQt5.QtSql import QSqlTableModel

from database import *
from operations import OperationsManager

from abstractview import saquery_to_qtquery
from productview import ProductView, ProductDetailsWidget, ProductLinksWidget
from dialogs import WatchProductDialog, VndProductDialog, SearchAmazonDialog

from amz_product_details_ui import Ui_amzProductDetails
from amz_product_history_ui import Ui_amzProductHistory
from amz_product_sourcing_ui import Ui_amzProductSourcing

from delegates import CurrencyDelegate, IntegerDelegate, ReadOnlyDelegate, DataMapperDelegate


class AmzProductDetailsWidget(ProductDetailsWidget, Ui_amzProductDetails):

    def __init__(self, parent=None):
        super(AmzProductDetailsWidget, self).__init__(parent=parent)
        # setupUi() is called by the base class

        self.categoryLine.textChanged.connect(lambda: self.categoryLine.home(False))

        # Set up the data widget mapper
        self.mapper.addMapping(self.salesRankLine, self.productModel.fieldIndex('salesrank'))
        self.mapper.addMapping(self.offersBox, self.productModel.fieldIndex('offers'))

        # Connections
        self.openCamelBtn.clicked.connect(self.open_camelcamelcamel)

    def set_listing(self, listing):
        super(AmzProductDetailsWidget, self).set_listing(listing)

        category = listing.category.name if listing else ''
        self.categoryLine.setText(category)

        if listing and listing.hasprime:
            hasprime = 'Yes'
        elif listing and not listing.hasprime:
            hasprime = 'No'
        else:
            hasprime = 'N/A'

        self.primeLine.setText(hasprime)

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
                                     filter(AmzProductHistory.amz_listing_id == amz_id,
                                            AmazonMerchant.id == AmzProductHistory.merchant_id).\
                                     order_by(AmzProductHistory.timestamp.desc())

        qt_query = saquery_to_qtquery(query)
        qt_query.exec_()
        self.historyModel.setQuery(qt_query)
        self.historyModel.select()


class AmzProductLinksWidget(ProductLinksWidget):

    def __init__(self, parent=None):
        super(AmzProductLinksWidget, self).__init__(parent=parent)
        # setupUi() is called by the base class

        self.actionNewLinkedListing = QAction('New source listing', self)
        self.actionNewLinkedListing.triggered.connect(self.new_source_listing)
        self.context_menu.addAction(self.actionNewLinkedListing)

    def set_listing(self, listing):
        super(AmzProductLinksWidget, self).set_listing(listing)
        listing_id = listing.id if listing else None

        stmt = self.dbsession.query(LinkedProducts.confidence,
                                    VendorListing,
                                    VendorListing.unit_price). \
                              filter(LinkedProducts.vnd_listing_id == VendorListing.id,
                                     LinkedProducts.amz_listing_id == listing_id). \
                              subquery()

        query = self.dbsession.query(stmt.c.id.label('id'),
                                     func.printf('%.1f%%', stmt.c.confidence).label('Conf.'),
                                     Vendor.name.label('Vendor'),
                                     stmt.c.sku.label('SKU'),
                                     stmt.c.title.label('Title'),
                                     stmt.c.price.label('Price'),
                                     stmt.c.quantity.label('Quantity'),
                                     stmt.c.unit_price.label('Unit Price')). \
                               filter(Vendor.id == stmt.c.vendor_id)

        qt_links_query = saquery_to_qtquery(query)
        qt_links_query.exec_()
        self.linksModel.setQuery(qt_links_query)
        self.linksModel.select()

    def new_source_listing(self):
        dialog = VndProductDialog(self)
        ok = dialog.exec_()
        if not ok:
            return

        listing = dialog.get_listing()
        vnd_name = dialog.vendor_name

        # Check for a vendor with this name
        vendor = self.dbsession.query(Vendor).filter_by(name=vnd_name).first()

        if vendor:
            prior = self.dbsession.query(Listing).filter_by(sku=listing.sku, vendor_id=vendor.id).first()
            if prior:
                QMessageBox.information(self, 'Error', 'Vendor/SKU combination is already in use.')
                return
        else:
            vendor = Vendor(name=vnd_name)

        listing.vendor = vendor
        listing.updated = func.now()
        self.dbsession.add(listing)
        self.dbsession.flush()

        # Create a link
        link = LinkedProducts(amz_listing_id=self.parent_listing.id, vnd_listing_id=listing.id, confidence=100)
        self.dbsession.add(link)
        self.dbsession.commit()

        self.set_listing(self.parent_listing)


class AmzProductSourcingWidget(QWidget, Ui_amzProductSourcing):

    def __init__(self, parent=None):
        super(AmzProductSourcingWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.amz_listing = None
        self.vnd_listing = None
        self.sel_price_point = None
        self.dbsession = Session()

        # Set up the model and table
        self.pricePointsModel = QSqlTableModel(self)
        self.pricePointsTable.setModel(self.pricePointsModel)
        self.pricePointsModel.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.pricePointsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.pricePointsTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.pricePointsTable.verticalHeader().hide()
        self.pricePointsTable.setContextMenuPolicy(Qt.CustomContextMenu)

        self.pricePointsModel.dataChanged.connect(self.edit_price_point)
        self.pricePointsTable.selectionModel().currentRowChanged.connect(self.on_selection_change)
        self.pricePointsTable.customContextMenuRequested.connect(self.pricePoints_context_menu)

        # Populate
        self.set_listing(None)

        # More table setup
        self.pricePointsTable.setItemDelegateForColumn(self.pricePointsModel.fieldIndex('id'), ReadOnlyDelegate(parent=self))
        self.pricePointsTable.setItemDelegateForColumn(self.pricePointsModel.fieldIndex('Margin'), ReadOnlyDelegate(parent=self))
        self.pricePointsTable.setItemDelegateForColumn(self.pricePointsModel.fieldIndex('Profit'), CurrencyDelegate(readonly=True, parent=self))
        self.pricePointsTable.setItemDelegateForColumn(self.pricePointsModel.fieldIndex('Price'), CurrencyDelegate(parent=self))
        self.pricePointsTable.setItemDelegateForColumn(self.pricePointsModel.fieldIndex('FBA Fees'), CurrencyDelegate(parent=self))

        # Connections
        self.actionNew_price_point.triggered.connect(self.new_price_point)
        self.actionDelete_price_point.triggered.connect(self.delete_price_point)
        self.actionGet_FBA_fees.triggered.connect(self.get_fba_fees)

    def on_selection_change(self, current, previous):
        id_idx = self.pricePointsModel.index(current.row(), self.pricePointsModel.fieldIndex('id'))
        price_id = id_idx.data(Qt.DisplayRole)

        self.sel_price_point = self.dbsession.query(AmzPriceAndFees).filter_by(id=price_id).first()

    def set_listing(self, listing):
        self.vnd_listing = None
        self.sel_price_point = None
        self.amz_listing = listing

        self.update_price_points()

    def set_vnd_listing(self, listing):
        self.vnd_listing = listing
        self.update_price_points()

    def update_price_points(self):
        self.sel_price_point = None
        amz_id = self.amz_listing.id if self.amz_listing else None

        if self.amz_listing and self.vnd_listing:
            vnd_cost = self.vnd_listing.unit_price * self.amz_listing.quantity
        else:
            vnd_cost = 0

        stmt = self.dbsession.query(AmzPriceAndFees.id,
                                    AmzPriceAndFees.price,
                                    AmzPriceAndFees.fba,
                                    label('profit', AmzPriceAndFees.price - AmzPriceAndFees.fba - vnd_cost)).\
                              filter_by(amz_listing_id=amz_id).\
                              subquery()

        margin_exp = func.printf('%.2f', stmt.c.profit / vnd_cost) if vnd_cost else func.printf('N/A')

        query = self.dbsession.query(stmt.c.id.label('id'),
                                     stmt.c.price.label('Price'),
                                     stmt.c.fba.label('FBA Fees'),
                                     stmt.c.profit.label('Profit'),
                                     label('Margin', margin_exp))

        qt_query = saquery_to_qtquery(query)
        qt_query.exec_()
        self.pricePointsModel.clear()
        self.pricePointsModel.setQuery(qt_query)
        self.pricePointsModel.select()

    def pricePoints_context_menu(self, point):
        self.actionNew_price_point.setEnabled(bool(self.amz_listing))
        self.actionDelete_price_point.setEnabled(bool(self.sel_price_point))
        self.actionGet_FBA_fees.setEnabled(bool(self.sel_price_point and self.sel_price_point.price))

        menu = QMenu(self)
        menu.addActions([self.actionNew_price_point,
                         self.actionDelete_price_point,
                         self.actionGet_FBA_fees])

        point = self.pricePointsTable.viewport().mapToGlobal(point)
        menu.popup(point)

    def new_price_point(self):
        new_price = AmzPriceAndFees(amz_listing_id=self.amz_listing.id)
        self.dbsession.add(new_price)
        self.dbsession.commit()

        self.update_price_points()

    def delete_price_point(self):
        self.dbsession.delete(self.sel_price_point)
        self.dbsession.commit()

        self.update_price_points()

    def edit_price_point(self, topleft, bottomright, roles):
        data = topleft.data(Qt.DisplayRole)
        column = topleft.column()

        if column == self.pricePointsModel.fieldIndex('Price'):
            self.sel_price_point.price = data
        elif column == self.pricePointsModel.fieldIndex('FBA Fees'):
            self.sel_price_point.fba = data
        else:
            return

        self.dbsession.commit()
        self.update_price_points()

    def get_fba_fees(self):
        price = self.sel_price_point.price
        fee_op = Operation.GetMyFeesEstimate(listing_id=self.amz_listing.id,
                                             params={'price': price})
        opsman = OperationsManager.get_instance()
        opsman.register_callback(fee_op, self.get_fees_callback)

        self.dbsession.add(fee_op)
        self.dbsession.commit()

    def get_fees_callback(self, op):
        if op.error:
            QMessageBox.information(self, 'Error', 'Could not get FBA fees: %s' % op.message)
            return

        self.update_price_points()


class AmazonView(ProductView):

    def __init__(self, parent=None):
        super(AmazonView, self).__init__(parent=parent)

        self.amz_listing = None
        self.vnd_listing = None

        self.details = AmzProductDetailsWidget()
        self.history = AmzProductHistoryWidget()
        self.links = AmzProductLinksWidget()
        self.sourcing = AmzProductSourcingWidget()

        self.links.selection_changed.connect(self.link_selection_changed)

        line1 = QFrame()
        line1.setFrameShape(QFrame.VLine)
        line1.setFrameShadow(QFrame.Sunken)

        details_layout = QHBoxLayout()
        details_layout.setContentsMargins(5, 0, 5, 5)
        details_layout.addWidget(self.details)
        details_layout.addWidget(line1)
        details_layout.addWidget(self.history)

        details_widget = QWidget()
        details_widget.setLayout(details_layout)

        line2 = QFrame()
        line2.setFrameShape(QFrame.VLine)
        line2.setFrameShadow(QFrame.Sunken)

        sourcing_layout = QHBoxLayout()
        sourcing_layout.setContentsMargins(5, 0, 5, 5)
        sourcing_layout.addWidget(self.links)
        sourcing_layout.addWidget(line2)
        sourcing_layout.addWidget(self.sourcing)

        sourcing_widget = QWidget()
        sourcing_widget.setLayout(sourcing_layout)

        # Create the tabs
        self.tabs = QTabWidget(self)
        self.tabs.addTab(details_widget, 'Product Details')
        self.tabs.addTab(sourcing_widget, 'Sourcing')

        self.layout().addWidget(self.tabs)

        # Connections
        self.mainTable.selectionModel().currentRowChanged.connect(self.on_selection_change)

        # Populate the table
        self.populate_source_box()
        self.show_listings()

        # Toolbar actions
        self.actionSearch_Amazon = QAction(QIcon('icons/searchamazon.gif'), 'Search Amazon...', self)
        self.actionSearch_Amazon.triggered.connect(self.search_amazon)

        self.tool_buttons.append(self.actionSearch_Amazon)

        # Create some context menu actions
        self.actionWatch_this_product = QAction(QIcon('icons/watch_product.png'), 'Watch this product...', self)
        self.actionRemove_watch = QAction('Remove product watch', self)

        self.actionWatch_this_product.triggered.connect(self.watch_product)
        self.actionRemove_watch.triggered.connect(self.remove_watch)

        self.mainTable_context_actions.extend([self.actionWatch_this_product,
                                              self.actionRemove_watch])

    def is_amazon(self):
        return True

    def on_selection_change(self, current, previous):
        src_idx = self.mainTable.model().mapToSource(current)
        id_idx = self.mainModel.index(src_idx.row(), self.mainModel.fieldIndex('id'))
        amz_id = id_idx.data(Qt.DisplayRole)

        self.amz_listing = self.dbsession.query(AmazonListing).filter_by(id=amz_id).one()
        self.details.set_listing(self.amz_listing)
        self.history.set_listing(self.amz_listing)
        self.links.set_listing(self.amz_listing)
        self.sourcing.set_listing(self.amz_listing)

    def link_selection_changed(self):
        self.sourcing.set_vnd_listing(self.links.sel_listing)

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

    def maybe_enable_mainTable_actions(self):
        super(AmazonView, self).maybe_enable_mainTable_actions()
        
        self.actionWatch_this_product.setEnabled(bool(self.amz_listing))
        amz_id = self.amz_listing.id if self.amz_listing else None

        watch = self.dbsession.query(Operation).filter_by(listing_id=amz_id,
                                                          operation='UpdateAmazonListing').\
                                                filter(Operation.param_string.contains('repeat')).\
                                                first()

        self.actionRemove_watch.setEnabled(bool(watch))

    def watch_product(self):
        old_op = self.dbsession.query(Operation).filter(Operation.listing_id == self.amz_listing.id,
                                                        Operation.operation == 'UpdateAmazonListing').\
                                                   first()
        if old_op:
            period = old_op.params.get('repeat', 60)
        else:
            period = 60

        dialog = WatchProductDialog(period=period, parent=self)
        ok = dialog.exec()

        if not ok:
            return

        if old_op:
            self.dbsession.delete(old_op)

        watch_op = Operation.UpdateAmazonListing(listing_id=self.amz_listing.id,
                                                 params={'log': True, 'repeat': dialog.period})
        self.dbsession.add(watch_op)
        self.dbsession.commit()

    def remove_watch(self):
        watch = self.dbsession.query(Operation).filter_by(listing_id=self.amz_listing.id,
                                                          operation='UpdateAmazonListing').\
                                                filter(Operation.param_string.contains('repeat')).\
                                                first()

        self.dbsession.delete(watch)
        self.dbsession.commit()

    def search_amazon(self):
        dialog = SearchAmazonDialog(self)
        ok = dialog.exec_()

        if not ok:
            return

        terms = dialog.search_terms
        list_name = dialog.list_name

        op = Operation.SearchAmazon(params={'terms': terms, 'addtolist': list_name},
                                    priority=10)

        opsman = OperationsManager.get_instance()
        opsman.register_callback(op, self.search_complete)

        self.dbsession.add(op)
        self.dbsession.commit()

    def search_complete(self, op):
        self.populate_source_box()
