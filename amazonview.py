import arrow
import webbrowser

from PyQt5.QtCore import Qt, QDateTime, QPointF
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtWidgets import QWidget, QAbstractItemView, QDataWidgetMapper, QHeaderView, QTabWidget, QHBoxLayout
from PyQt5.QtWidgets import QMessageBox, QStackedWidget, QItemDelegate, QLineEdit, QFrame, QMenu, QAction, QTableView
from PyQt5.QtWidgets import QVBoxLayout, QGraphicsItem
from PyQt5.QtSql import QSqlTableModel, QSqlQueryModel
from PyQt5.QtChart import QChartView, QChart, QDateTimeAxis, QValueAxis, QLineSeries, QScatterSeries

from database import *
from operations import OperationsManager

from productview import ProductView, ProductDetailsWidget, ProductLinksWidget
from dialogs import WatchProductDialog, VndProductDialog, SearchAmazonDialog, SearchListingsDialog

from amz_product_details_ui import Ui_amzProductDetails
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
        self.watchCheck.stateChanged.connect(self.watchPeriod.setEnabled)
        self.watchCheck.clicked.connect(self.modify_watch)
        self.watchPeriod.editingFinished.connect(self.modify_watch)
        self.watchCheck.setChecked(False)
        self.watchPeriod.setEnabled(False)

    def set_listing(self, listing):
        super(AmzProductDetailsWidget, self).set_listing(listing)

        category = listing.category.name if listing else ''
        self.categoryLine.setText(category)

        if listing:
            self.primeLine.setText('Yes' if listing.hasprime else 'No')
        else:
            self.primeLine.setText('N/A')

        watch = self.dbsession.query(Operation).filter_by(listing_id=listing.id if listing else None).\
                                                filter(and_(Operation.operation == 'UpdateAmazonListing',
                                                            Operation.param_string.contains('repeat'))).\
                                                first()
        if watch:
            self.watchCheck.setChecked(True)
            self.watchPeriod.setValue(watch.params['repeat'] / 60)
        else:
            self.watchCheck.setChecked(False)

    def open_camelcamelcamel(self):
        if self.listing is None:
            QMessageBox(self, 'Error', 'No listing selected.')
            return

        webbrowser.open('http://camelcamelcamel.com/search?sq=%s' % self.listing.sku)

    def modify_watch(self):
        if self.listing is None:
            return

        have_watch = self.watchCheck.checkState()
        watch_period = self.watchPeriod.value() * 60

        watch = self.dbsession.query(Operation).filter(Operation.listing_id == self.listing.id,
                                                       Operation.operation == 'UpdateAmazonListing',
                                                       Operation.param_string.contains('repeat')).\
                                                first()
        if not have_watch and watch:
            self.dbsession.delete(watch)
            self.dbsession.commit()
            return

        if watch is None:
            current_watch = Operation.UpdateAmazonListing(listing_id=self.listing.id)
            self.dbsession.add(current_watch)

        watch.params = {'log': True, 'repeat': watch_period}
        watch.priority = 5
        self.dbsession.commit()


class AmzProductHistoryWidget(QWidget):

    def __init__(self, parent=None):
        super(AmzProductHistoryWidget, self).__init__(parent=parent)

        self.setMaximumHeight(300)
        self.listing = None
        self.dbsession = Session()
        self.stack = QStackedWidget()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)

        self.setLayout(layout)

        # Set up the table and model
        self.historyModel = QSqlTableModel(self)
        self.historyTable = QTableView()
        self.historyTable.setModel(self.historyModel)
        self.historyTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.historyTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.historyTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.historyTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.historyTable.customContextMenuRequested.connect(self.context_menu)
        self.stack.addWidget(self.historyTable)

        # Set up the chart
        chart_view = QChartView()
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setContextMenuPolicy(Qt.CustomContextMenu)
        chart_view.customContextMenuRequested.connect(self.context_menu)

        self.stack.removeWidget(self.stack.widget(1))
        self.stack.addWidget(chart_view)

        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.setFlags(QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsSelectable)
        chart_view.setChart(self.chart)

        # Create the axes
        rcolor = QColor(50, 130, 220)
        pcolor = QColor(0, 200, 0)
        ocolor = QColor(255, 175, 0)

        self.timeAxis = QDateTimeAxis()
        self.timeAxis.setFormat('M/dd hh:mm')
        self.timeAxis.setTitleText('Date/Time')
        self.chart.addAxis(self.timeAxis, Qt.AlignBottom)

        self.rankAxis = QValueAxis()
        self.rankAxis.setLabelFormat('%\'i')
        self.rankAxis.setTitleText('Sales Rank')
        self.rankAxis.setLinePenColor(rcolor)
        self.rankAxis.setLabelsColor(rcolor)
        self.chart.addAxis(self.rankAxis, Qt.AlignLeft)

        self.priceAxis = QValueAxis()
        self.priceAxis.setLabelFormat('$%.2f')
        self.priceAxis.setTitleText('Price')
        self.priceAxis.setLinePenColor(pcolor)
        self.priceAxis.setLabelsColor(pcolor)
        self.chart.addAxis(self.priceAxis, Qt.AlignRight)

        # Create the series
        self.rankLine = QLineSeries()
        self.chart.addSeries(self.rankLine)
        self.rankLine.attachAxis(self.timeAxis)
        self.rankLine.attachAxis(self.rankAxis)
        self.rankLine.setColor(rcolor)

        self.priceLine = QLineSeries()
        self.chart.addSeries(self.priceLine)
        self.priceLine.attachAxis(self.timeAxis)
        self.priceLine.attachAxis(self.priceAxis)
        self.priceLine.setColor(pcolor)

        # Populate the table and chart
        self.set_listing(None)

        # Final table setup
        self.historyTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.historyTable.horizontalHeader().setSectionResizeMode(self.historyModel.fieldIndex('Merchant'), QHeaderView.Stretch)

        # Context menu actions
        self.actionSwitch_view = QAction('Show chart')
        self.actionSwitch_view.triggered.connect(self.switch_view)

        self.set_listing(None)

        self.stack.setCurrentIndex(1)

    def set_listing(self, listing):
        self.listing = listing
        amz_id = listing.id if listing else None

        query = self.dbsession.query(AmzProductHistory.timestamp.label('Date/Time'),
                                     AmzProductHistory.salesrank.label('Sales Rank'),
                                     AmzProductHistory.offers.label('Offers'),
                                     AmzProductHistory.hasprime.label('Prime'),
                                     AmzProductHistory.price.label('Price'),
                                     AmazonMerchant.name.label('Merchant')).\
                                     filter(AmzProductHistory.amz_listing_id == amz_id,
                                            AmazonMerchant.id == AmzProductHistory.merchant_id).\
                                     order_by(AmzProductHistory.timestamp.desc())

        qt_query = saquery_to_qtquery(query)
        qt_query.exec_()
        self.historyModel.setQuery(qt_query)
        self.historyModel.select()

        # Update the chart
        self.rankLine.clear()
        self.priceLine.clear()

        for row in self.dbsession.query(AmzProductHistory).filter_by(amz_listing_id=amz_id):
            time = row.timestamp.timestamp() * 1000
            self.rankLine.append(time, row.salesrank or 0)
            self.priceLine.append(time, row.price or 0)

        self.reset_axes()

    def reset_axes(self):
        r = self.rankLine.pointsVector()
        p = self.priceLine.pointsVector()

        # If there is only one data point, set the min and max to the day before and the day after
        if len(r) == 1:
            tmin = QDateTime.fromMSecsSinceEpoch(r[0].x(), Qt.LocalTime).addDays(-1)
            tmax = QDateTime.fromMSecsSinceEpoch(r[0].x(), Qt.LocalTime).addDays(+1)
        else:
            tmin = min(r, key=lambda pt: pt.x(), default=QPointF(QDateTime.currentDateTime().addDays(-1).toMSecsSinceEpoch(), 0)).x()
            tmax = max(r, key=lambda pt: pt.x(), default=QPointF(QDateTime.currentDateTime().addDays(+1).toMSecsSinceEpoch(), 0)).x()
            tmin = QDateTime.fromMSecsSinceEpoch(tmin, Qt.LocalTime)
            tmax = QDateTime.fromMSecsSinceEpoch(tmax, Qt.LocalTime)

        self.timeAxis.setMin(tmin)
        self.timeAxis.setMax(tmax)

        # Find the min and max values of the series
        min_point = lambda pts: min(pts, key=lambda pt: pt.y(), default=QPointF(0, 0))
        max_point = lambda pts: max(pts, key=lambda pt: pt.y(), default=QPointF(0, 0))

        rmin = min_point(r)
        rmax = max_point(r)
        pmin = min_point(p)
        pmax = max_point(p)

        # Scale the mins and maxes to 'friendly' values
        scalemin = lambda v, step: ((v - step / 2) // step) * step
        scalemax = lambda v, step: ((v + step / 2) // step + 1) * step

        # The the axis bounds

        rmin = max(scalemin(rmin.y(), 1000), 0)
        rmax = scalemax(rmax.y(), 1000)
        pmin = max(scalemin(pmin.y(), 5), 0)
        pmax = scalemax(pmax.y(), 5)

        self.rankAxis.setMin(rmin)
        self.rankAxis.setMax(rmax)
        self.priceAxis.setMin(pmin)
        self.priceAxis.setMax(pmax)


    def context_menu(self, point):
        current_widget = self.stack.currentWidget()
        if isinstance(current_widget, QTableView):
            self.actionSwitch_view.setText('Show chart')
        else:
            self.actionSwitch_view.setText('Show table')

        menu = QMenu(self)
        menu.addAction(self.actionSwitch_view)
        point = current_widget.viewport().mapToGlobal(point)
        menu.popup(point)

    def switch_view(self):
        current_index = self.stack.currentIndex()
        next_index = 0 if current_index else 1
        self.stack.setCurrentIndex(next_index)


class AmzProductLinksWidget(ProductLinksWidget):
    """A subclass of ProductLinksWidget, specialized to show vendor listings linked to a
    parent AmazonListing.
    """

    def __init__(self, parent=None):
        super(AmzProductLinksWidget, self).__init__(parent=parent)
        # setupUi() is called by the base class

        self.actionEditLinkedListing = QAction('Create/edit source listing...', self)
        self.actionEditLinkedListing.triggered.connect(self.edit_source_listing)
        self.context_menu.addAction(self.actionEditLinkedListing)

        self.actionFindSources = QAction('Find sources...', self)
        self.actionFindSources.triggered.connect(self.find_sources)
        self.context_menu.addAction(self.actionFindSources)

    def generate_query(self, parent_listing):
        """Return a SQLAlchemy query object, used to populate the table."""
        parent_id = parent_listing.id if parent_listing else None

        stmt = self.dbsession.query(LinkedProducts.confidence,
                                    VendorListing,
                                    VendorListing.unit_price). \
                              filter(LinkedProducts.vnd_listing_id == VendorListing.id,
                                     LinkedProducts.amz_listing_id == parent_id). \
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
        return query

    def reload(self):
        """Reload the table."""
        self.set_listing(self.parent_listing)

    def maybe_enable_context_actions(self):
        """Enable or disable context actions prior to showing the menu."""
        super(AmzProductLinksWidget, self).maybe_enable_context_actions()
        self.actionEditLinkedListing.setEnabled(bool(self.parent_listing))
        self.actionFindSources.setEnabled(bool(self.parent_listing))

    def edit_source_listing(self):
        """Show the vendor listing popup editor. Edits the currently selected listing, or creates a new one."""
        dialog = VndProductDialog(self.sel_listing, self)
        ok = dialog.exec_()
        if not ok:
            return

        if self.sel_listing is None:
            listing = dialog.listing

            # Create a link
            link = LinkedProducts(amz_listing_id=self.parent_listing.id, vnd_listing_id=listing.id, confidence=100)
            self.dbsession.add(link)
            self.dbsession.commit()

        self.reload()

    def find_sources(self):
        """Show the SearchListingsDialog. Link selected results to the current parent listing."""
        dialog = SearchListingsDialog(amazon=False, parent=self)
        ok = dialog.exec_()
        if not ok:
            return

        selected_ids = dialog.selected_ids

        for listing_id in selected_ids:
            link = LinkedProducts(amz_listing_id=self.parent_listing.id, vnd_listing_id=listing_id, confidence=100)
            self.dbsession.merge(link)

        self.dbsession.commit()
        self.reload()

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
        self.pricePointsTable.setItemDelegateForColumn(self.pricePointsModel.fieldIndex('Prep Cost'), CurrencyDelegate(parent=self))
        self.pricePointsTable.setItemDelegateForColumn(self.pricePointsModel.fieldIndex('Shipping'), CurrencyDelegate(parent=self))

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
                                    AmzPriceAndFees.prep,
                                    AmzPriceAndFees.ship,
                                    label('profit', AmzPriceAndFees.price \
                                                    - func.ifnull(AmzPriceAndFees.fba, 0) \
                                                    - func.ifnull(AmzPriceAndFees.prep, 0) \
                                                    - func.ifnull(AmzPriceAndFees.ship, 0) \
                                                    - vnd_cost)).\
                              filter_by(amz_listing_id=amz_id).\
                              subquery()

        if vnd_cost:
            margin_exp = func.printf('%.2f%%', stmt.c.profit / (vnd_cost \
                                                                + func.ifnull(stmt.c.prep, 0) \
                                                                + func.ifnull(stmt.c.ship, 0)) * 100)
        else:
            margin_exp = func.printf('N/A')

        query = self.dbsession.query(stmt.c.id.label('id'),
                                     stmt.c.price.label('Price'),
                                     stmt.c.fba.label('FBA Fees'),
                                     stmt.c.prep.label('Prep Cost'),
                                     stmt.c.ship.label('Shipping'),
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
        elif column == self.pricePointsModel.fieldIndex('Prep Cost'):
            self.sel_price_point.prep = data
        elif column == self.pricePointsModel.fieldIndex('Shipping'):
            self.sel_price_point.ship = data
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

        self.links.linksTable.selectRow(0)

    def link_selection_changed(self):
        self.sourcing.set_vnd_listing(self.links.sel_listing)

    def show_listings(self):
        source = self.sourceBox.currentText()

        query = self.dbsession.query(AmazonListing.id.label('id'),
                                     AmazonCategory.name.label('Category'),
                                     AmazonListing.salesrank.label('Sales Rank'),
                                     AmazonListing.brand.label('Brand'),
                                     AmazonListing.model.label('Model'),
                                     AmazonListing.quantity.label('Quantity'),
                                     AmazonListing.price.label('Price'),
                                     AmazonListing.title.label('Description'),
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
        """Add an UpdateAmazonListing operation for each selected listing."""
        dialog = WatchProductDialog(period=1, parent=self)
        ok = dialog.exec()

        if not ok:
            return

        selected_ids = [index.data() for index in self.mainTable.selectionModel().selectedRows()]
        for listing_id in selected_ids:
            # Check if a watch has already been set
            old_op = self.dbsession.query(Operation).filter(Operation.listing_id==listing_id,
                                                            Operation.operation=='UpdateAmazonListing',
                                                            Operation.param_string.contains('repeat')).\
                                                    first()
            if old_op:
                self.dbsession.delete(old_op)

            # Create and add a new update operation
            watch_op = Operation.UpdateAmazonListing(listing_id=listing_id,
                                                     priority=5,
                                                     params={'log': True, 'repeat': dialog.period * 60})
            self.dbsession.add(watch_op)

        self.dbsession.commit()

    def remove_watch(self):
        """Remove watch operations from the selected listings."""
        selected_ids = [index.data() for index in self.mainTable.selectionModel().selectedRows()]

        for listing_id in selected_ids:
            self.dbsession.query(Operation).filter(Operation.listing_id == listing_id,
                                                   Operation.operation == 'UpdateAmazonListing',
                                                   Operation.param_string.contains('repeat')).\
                                            delete()
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
