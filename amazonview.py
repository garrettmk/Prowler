import webbrowser

from PyQt5.QtCore import Qt, QDateTime, QPointF
from PyQt5.QtGui import QIcon, QPainter, QColor
from PyQt5.QtWidgets import QWidget, QAbstractItemView, QDataWidgetMapper, QHeaderView, QTabWidget, QHBoxLayout
from PyQt5.QtWidgets import QMessageBox, QStackedWidget, QItemDelegate, QLineEdit, QFrame, QMenu, QAction, QTableView
from PyQt5.QtWidgets import QVBoxLayout, QGraphicsItem
from PyQt5.QtChart import QChartView, QChart, QDateTimeAxis, QValueAxis, QLineSeries, QScatterSeries
from delegates import CurrencyDelegate, ReadOnlyDelegate, IntegerDelegate, BooleanDelegate, UTCtoLocalDelegate

from database import *
import dbhelpers

from operations import OperationsManager

from prowlerwidgets import ProwlerTableWidget, ProductDetailsWidget
from baseview import BaseSourceView
from dialogs import VndProductDialog, SearchAmazonDialog, SearchListingsDialog, SetWatchDialog

from amz_product_details_ui import Ui_amzProductDetails


class AmzProductDetailsWidget(ProductDetailsWidget, Ui_amzProductDetails):
    """Subclass of ProductDetailsWidget, specialized to show details of an Amazon listing."""

    def __init__(self, parent=None):
        super(AmzProductDetailsWidget, self).__init__(parent=parent)
        # setupUi() is called by the parent class

        # UI connections
        self.watchCheck.stateChanged.connect(self.watchPeriod.setEnabled)
        self.watchCheck.clicked.connect(self.modify_watch)
        self.watchPeriod.editingFinished.connect(self.modify_watch)
        self.watchCheck.setChecked(False)
        self.watchPeriod.setEnabled(False)

        # Set up the data widget mapper
        self.mapper.addMapping(self.salesRankLine, self.model.fieldIndex('salesrank'))
        self.mapper.addMapping(self.offersBox, self.model.fieldIndex('offers'))

        # Update other fields
        self.mapper.currentIndexChanged.connect(self.update_category)
        self.mapper.currentIndexChanged.connect(self.update_watch)
        self.mapper.currentIndexChanged.connect(self.update_prime)

    def update_category(self):
        """Update the category line."""
        cat_name = self.source.category.name if self.source else ''
        self.categoryLine.setText(cat_name)
        self.categoryLine.home(False)

    def update_watch(self):
        """Update the watch check and spinbox."""
        watch = dbhelpers.get_watch(self.dbsession, getattr(self.source, 'id', None))

        if watch:
            self.watchCheck.setChecked(True)
            self.watchPeriod.setValue(watch.params['repeat'] / 60)
        else:
            self.watchCheck.setChecked(False)
            self.watchPeriod.setValue(0)

    def update_prime(self):
        """Update the 'has prime' line."""
        has_prime = str(self.source.hasprime) if self.source else ''
        self.primeLine.setText(has_prime)

    def modify_watch(self):
        """Modify or remove a watch on the product."""
        if self.source is None:
            return

        have_watch = self.watchCheck.checkState()
        watch_period = self.watchPeriod.value() * 60

        dbhelpers.set_watch(self.dbsession, self.source.id, watch_period if have_watch else None)
        self.dbsession.commit()


class AmzHistoryTableWidget(ProwlerTableWidget):
    """Shows the logged history of an AmazonListing."""

    def __init__(self, parent=None):
        super(AmzHistoryTableWidget, self).__init__(parent=parent)

        # Disable selection
        self.table.setSelectionMode(QAbstractItemView.NoSelection)

        # Populate columns
        self.set_source(None)

        # Table setup
        self.table.horizontalHeader().setSectionResizeMode(self.model.fieldIndex('Merchant'), QHeaderView.Stretch)
        self.table.verticalHeader().hide()

        # Display delegates
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Date/Time'), UTCtoLocalDelegate(parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Sales Rank'), IntegerDelegate(parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Offers'), IntegerDelegate(parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Price'), CurrencyDelegate(parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Prime'), BooleanDelegate(terms=['No', 'Yes'], parent=self))

    def generate_query(self, source):
        source_id = getattr(source, 'id', None)

        query = self.dbsession.query(AmzProductHistory.timestamp.label('Date/Time'),
                                     AmzProductHistory.salesrank.label('Sales Rank'),
                                     AmzProductHistory.offers.label('Offers'),
                                     AmzProductHistory.hasprime.label('Prime'),
                                     AmzProductHistory.price.label('Price'),
                                     AmazonMerchant.name.label('Merchant')). \
                               filter(AmzProductHistory.amz_listing_id == source_id,
                                      AmazonMerchant.id == AmzProductHistory.merchant_id). \
                               order_by(AmzProductHistory.timestamp.desc())

        return query


class AmzHistoryChart(QWidget):
    """A chart that graphs the history of an AmazonListing's sales rank, price, and number of offers."""

    def __init__(self, parent=None):
        super(AmzHistoryChart, self).__init__(parent=parent)

        self.dbsession = Session()
        self.context_menu_actions = []

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Set up the chart
        self.chart_view = QChartView(self)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chart_view.customContextMenuRequested.connect(self.context_menu)

        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.setFlags(QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsSelectable)
        self.chart_view.setChart(self.chart)

        self.layout().addWidget(self.chart_view)

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

    def add_context_action(self, action):
        """Add an action to the chart's context menu."""
        self.context_menu_actions.append(action)

    def add_context_actions(self, actions):
        """Adds all action in an iterable."""
        self.context_menu_actions.extend(actions)

    def remove_context_action(self, action):
        """Removes an action from the chart's context menu."""
        self.context_menu_actions.remove(action)

    def context_menu(self, point):
        """Show a context menu on the chart."""
        menu = QMenu(self)
        menu.addActions(self.context_menu_actions)

        point = self.chart_view.viewport().mapToGlobal(point)
        menu.popup(point)

    def set_source(self, source):
        """Set the source listing for the graph."""
        self.source = source
        amz_id = getattr(source, 'id', None)

        # Update the chart
        self.rankLine.clear()
        self.priceLine.clear()

        for row in self.dbsession.query(AmzProductHistory).filter_by(amz_listing_id=amz_id):
            time = row.timestamp.timestamp() * 1000
            self.rankLine.append(time, row.salesrank or 0)
            self.priceLine.append(time, row.price or 0)

        self.reset_axes()

    def reset_axes(self):
        """Resets the chart axes."""
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


class AmzProductLinksWidget(ProwlerTableWidget):
    """A subclass of ProductLinksWidget, specialized to show vendor listings linked to an AmazonListing."""

    def __init__(self, parent=None):
        super(AmzProductLinksWidget, self).__init__(parent=parent)
        # setupUi() is called by the base class

        self.set_source(None)

        # Set the table to sort by price by default
        self.table.sortByColumn(self.model.fieldIndex('Unit Price'), Qt.AscendingOrder)

        # Display delegates
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Price'), CurrencyDelegate(parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Quantity'), IntegerDelegate(parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Unit Price'), CurrencyDelegate(parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Tax Ea.'), CurrencyDelegate(parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Ship Ea.'), CurrencyDelegate(parent=self))

        # Some context actions
        self.action_find_sources = QAction('Find sources...', self)
        self.action_find_sources.triggered.connect(self.on_find_sources)

        self.action_edit_src_listing = QAction('Create/edit source listing...', self)
        self.action_edit_src_listing.triggered.connect(self.on_edit_src_listing)

        self.add_context_actions([self.action_edit_src_listing,
                                  self.action_find_sources])

    def set_source(self, source):
        super(AmzProductLinksWidget, self).set_source(source)

        # Hide the id column
        self.table.setColumnHidden(self.model.fieldIndex('id'), True)

    def generate_query(self, source):
        """Return a SQLAlchemy query object, used to populate the table."""
        source_id = getattr(source, 'id', None)

        stmt = self.dbsession.query(LinkedProducts.confidence,
                                    VendorListing,
                                    VendorListing.unit_price,
                                    Vendor.tax_rate,
                                    Vendor.ship_rate). \
                              filter(LinkedProducts.vnd_listing_id == VendorListing.id,
                                     LinkedProducts.amz_listing_id == source_id,
                                     Vendor.id == VendorListing.vendor_id). \
                              subquery()

        query = self.dbsession.query(stmt.c.id.label('id'),
                                     func.printf('%.1f%%', stmt.c.confidence).label('Conf.'),
                                     Vendor.name.label('Vendor'),
                                     stmt.c.sku.label('SKU'),
                                     stmt.c.title.label('Title'),
                                     stmt.c.price.label('Price'),
                                     stmt.c.quantity.label('Quantity'),
                                     stmt.c.unit_price.label('Unit Price'),
                                     label('Tax Ea.', stmt.c.tax_rate * stmt.c.unit_price),
                                     label('Ship Ea.', stmt.c.ship_rate * stmt.c.unit_price)). \
                               filter(Vendor.id == stmt.c.vendor_id)
        return query

    def on_find_sources(self):
        """Search for related listings in the database."""
        dialog = SearchListingsDialog(show_amazon=False, parent=self)
        ok = dialog.exec_()
        if not ok:
            return

        amz_id = self.source.id

        vnd_ids = dialog.selected_ids
        for vnd_id in vnd_ids:
            dbhelpers.link_products_ids(self.dbsession, amz_id, vnd_id)

        self.dbsession.commit()
        self.reload()

    def on_edit_src_listing(self):
        """Create or modify a linked vendor listing."""
        selection = self.dbsession.query(VendorListing).filter_by(id=self.get_selected_id()).first()

        dialog = VndProductDialog(selection, self)
        ok = dialog.exec_()
        if not ok:
            return

        if selection is None:
            dbhelpers.link_products(self.dbsession, self.source, dialog.listing)

        self.dbsession.commit()
        self.reload()


class AmzPricingWidget(ProwlerTableWidget):
    """A subclass of ProwlerTableWidget that shows price points and profit calculations for a given AmazonListing."""
    def __init__(self, parent=None):
        super(AmzPricingWidget, self).__init__(parent=parent)

        self.vnd_source = None

        # Set up the table
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(QHeaderView.AllEditTriggers)

        self.model.dataChanged.connect(self.edit_price_point)

        # Populate columns
        self.set_source(None)

        # More table setup
        self.table.setItemDelegateForColumn(self.model.fieldIndex('id'), ReadOnlyDelegate(parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Margin'), ReadOnlyDelegate(parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Profit'), CurrencyDelegate(readonly=True, parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Price'), CurrencyDelegate(parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('FBA Fees'), CurrencyDelegate(parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Prep Cost'), CurrencyDelegate(parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Shipping'), CurrencyDelegate(parent=self))

        # Create some actions
        self.action_new_price = QAction(QIcon('icons/price_tag.png'), 'New price point', self)
        self.action_delete_price = QAction(QIcon('icons/delete.png'), 'Delete price point', self)
        self.action_get_fba_fees = QAction(QIcon('icons/fee.png'), 'Get FBA fees', self)

        self.action_new_price.triggered.connect(self.on_new_price)
        self.action_delete_price.triggered.connect(self.on_delete_price)
        self.action_get_fba_fees.triggered.connect(self.on_get_fba_fees)

        self.add_context_actions([self.action_new_price,
                                  self.action_delete_price,
                                  self.action_get_fba_fees])

    def set_vnd_source(self, listing):
        """Set the vendor listing used to calculate profits."""
        self.vnd_source = listing
        self.reload()

    def set_source(self, source):
        super(AmzPricingWidget, self).set_source(source)

        # Hide the id column
        self.table.setColumnHidden(self.model.fieldIndex('id'), True)

    def generate_query(self, source):
        amz_id = getattr(source, 'id', None)

        if self.source and self.vnd_source:
            vnd_cost = self.vnd_source.unit_price * self.source.quantity
            vnd_cost += (vnd_cost * self.vnd_source.vendor.tax_rate) + (vnd_cost * self.vnd_source.vendor.ship_rate)
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

        return query

    def on_new_price(self):
        """Create a new price point linked to the current source."""
        new_price = AmzPriceAndFees(amz_listing_id=self.source.id)
        self.dbsession.add(new_price)
        self.dbsession.commit()
        self.reload()

    def on_delete_price(self):
        """Delete any selected price points."""

        for price_id in self.selected_ids:
            price = self.dbsession.query(AmzPriceAndFees).filter_by(id=price_id).first()
            self.dbsession.delete(price)

        self.dbsession.commit()
        self.reload()

    def on_get_fba_fees(self):
        """Request FBA fees for the selected price points."""

        opsman = OperationsManager.get_instance()

        for price_id in self.selected_ids:
            price = self.dbsession.query(AmzPriceAndFees).filter_by(id=price_id).first()

            fee_op = Operation.GetMyFeesEstimate(listing_id=self.source.id,
                                                 priority=10,
                                                 params={'price': price.price})

            opsman.register_callback(fee_op, self.get_fees_callback)
            self.dbsession.add(fee_op)

        self.dbsession.commit()

    def get_fees_callback(self, op):
        """Reload when the fee request finishes"""
        if op.error:
            QMessageBox.information(self, 'Error', 'Could not get FBA fees for \'%s\': %s' % (op.listing.sku, op.message))
            return

        self.reload()

    def edit_price_point(self, topleft, bottomright, roles):
        """Handle editing data."""
        data = topleft.data(Qt.DisplayRole)
        column = topleft.column()

        price = self.dbsession.query(AmzPriceAndFees).filter_by(id=self.selected_ids[-1]).first()

        if column == self.model.fieldIndex('Price'):
            price.price = data
        elif column == self.model.fieldIndex('FBA Fees'):
            price.fba = data
        elif column == self.model.fieldIndex('Prep Cost'):
            price.prep = data
        elif column == self.model.fieldIndex('Shipping'):
            price.ship = data
        else:
            return

        self.dbsession.commit()
        self.reload()


class AmzSourceViewWidget(ProwlerTableWidget):
    """Shows a table of listings belonging to Amazon or and Amazon list."""

    def __init__(self, parent=None):
        super(AmzSourceViewWidget, self).__init__(parent=parent)

        # Populate table columns
        self.set_source(None)

        # Table setup
        self.table.verticalHeader().hide()

        self.table.setItemDelegateForColumn(self.model.fieldIndex('Sales Rank'), IntegerDelegate(parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Quantity'), IntegerDelegate(parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Price'), CurrencyDelegate(parent=self))
        self.table.setItemDelegateForColumn(self.model.fieldIndex('Prime'), BooleanDelegate(terms=['No', 'Yes'], parent=self))

    def set_source(self, source):
        super(AmzSourceViewWidget, self).set_source(source)

        # Column setup
        self.table.setColumnHidden(self.model.fieldIndex('id'), True)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(self.model.fieldIndex('Title'), QHeaderView.Stretch)

    def generate_query(self, source):
        query = self.dbsession.query(AmazonListing.id.label('id'),
                                     AmazonCategory.name.label('Category'),
                                     AmazonListing.salesrank.label('Sales Rank'),
                                     AmazonListing.brand.label('Brand'),
                                     AmazonListing.model.label('Model'),
                                     AmazonListing.quantity.label('Quantity'),
                                     AmazonListing.price.label('Price'),
                                     AmazonListing.hasprime.label('Prime'),
                                     AmazonListing.title.label('Title')).\
                                filter(Vendor.id == AmazonListing.vendor_id). \
                                filter(AmazonListing.category_id == AmazonCategory.id)

        if isinstance(source, Vendor):
            query = query.filter_by(vendor_id=source.id)
        if isinstance(source, List):
            query = query.join(ListMembership).filter_by(list_id=source.id)

        return query


class AmazonView(BaseSourceView):
    """View of an Amazon-based source, with product details, history, linked listings, and sourcing widgets."""

    def __init__(self, parent=None):
        super(AmazonView, self).__init__(parent=parent)
        self.setup_ui()

        self.shows_amazon = True

        # Tell the parent class about our widgets
        self.source_table_widget = self.source_view
        self.product_details_widget = self.product_details
        self.product_links_widget = self.product_links

        # Custom toolbar buttons
        self.action_search_amazon.triggered.connect(self.on_search_amazon)

        # Create context actions for the child widgets
        self.action_show_hist_table = QAction('Show table')
        self.action_show_hist_chart = QAction('Show chart')

        self.action_show_hist_table.triggered.connect(self.on_show_hist_table)
        self.action_show_hist_chart.triggered.connect(self.on_show_hist_chart)

        self.action_open_camel3 = QAction(QIcon('icons/camel.png'), 'Open in CamelCamelCamel...', self)
        self.action_open_camel3.triggered.connect(self.on_open_camel3)

        self.action_set_watch = QAction(QIcon('icons/watch.png'), 'Set watch...', self)
        self.action_set_watch.triggered.connect(self.on_set_watch)

        # Add context actions to the child widgets
        self.source_view.double_clicked.connect(self.action_open_in_browser.trigger)
        self.source_view.add_context_actions([self.action_add_to_list,
                                              self.action_remove_from_list,
                                              self.action_set_watch,
                                              self.action_open_in_browser,
                                              self.action_open_camel3,
                                              self.action_open_in_google,
                                              self.action_lookup_upc])

        self.product_links.double_clicked.connect(self.action_open_in_browser.trigger)
        self.product_links.add_context_actions([self.action_unlink_products,
                                                self.action_open_in_browser,
                                                self.action_open_in_google,
                                                self.action_lookup_upc])

        self.product_details.openUrlBtn.clicked.connect(self.action_open_in_browser.trigger)
        self.product_details.openGoogleBtn.clicked.connect(self.action_open_in_google.trigger)
        self.product_details.openUPCLookupBtn.clicked.connect(self.action_lookup_upc.trigger)
        self.product_details.openCamelBtn.clicked.connect(self.action_open_camel3.trigger)

        self.history_table.add_context_action(self.action_show_hist_chart)
        self.history_chart.add_context_action(self.action_show_hist_table)

        # Connect to selection change on the product links widget
        self.product_links.selection_changed.connect(self.on_link_selection_changed)

        # Populate and go
        self.on_show_hist_chart()
        self.populate_source_box()
        self.reload()

    def setup_ui(self):
        """Initialize the view's UI elements."""
        # Set the main layout
        self.setLayout(QVBoxLayout(self))

        # Create toolbar actions
        self.action_search_amazon = QAction(QIcon('icons/searchamazon.gif'), 'Search Amazon...', self)
        self.add_toolbar_action(self.action_search_amazon)

        # Create the source view table (the main table)
        self.source_view = AmzSourceViewWidget(self)
        self.layout().addWidget(self.source_view)

        # Create the tab section
        self.tabs = QTabWidget(self)
        self.layout().addWidget(self.tabs)

        #
        # Build the 'Product Details' tab
        #

        details_layout = QHBoxLayout()
        details_layout.setContentsMargins(5, 0, 5, 5)

        # Product details widget
        self.product_details = AmzProductDetailsWidget(self)
        details_layout.addWidget(self.product_details)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        details_layout.addWidget(line)

        # Product history stack
        self.history_table = AmzHistoryTableWidget(self)
        self.history_chart = AmzHistoryChart(self)

        self.history_stack = QStackedWidget(self)
        self.history_stack.addWidget(self.history_table)
        self.history_stack.addWidget(self.history_chart)

        details_layout.addWidget(self.history_stack)

        # Add the tab
        details_widget = QWidget()
        details_widget.setLayout(details_layout)
        self.tabs.addTab(details_widget, 'Product Details')

        #
        # Build the 'Sourcing' tab
        #

        sourcing_layout = QHBoxLayout()
        sourcing_layout.setContentsMargins(0, 0, 0, 0)

        # Product links widget
        self.product_links = AmzProductLinksWidget(self)
        sourcing_layout.addWidget(self.product_links)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        sourcing_layout.addWidget(line)

        # Sourcing widget
        self.product_pricing = AmzPricingWidget(self)
        sourcing_layout.addWidget(self.product_pricing)

        # Add the tab
        sourcing_widget = QWidget()
        sourcing_widget.setLayout(sourcing_layout)
        self.tabs.addTab(sourcing_widget, 'Sourcing')

    def on_main_selection_changed(self):
        """Update child widgets when the selection in the main table changes."""
        super(AmazonView, self).on_main_selection_changed()

        selection = self.dbsession.query(AmazonListing).filter_by(id=self.get_selected_id()).first()

        self.history_table.set_source(selection)
        self.history_chart.set_source(selection)
        self.product_pricing.set_source(selection)

        # Select the first linked vendor by default
        self.product_links.table.selectRow(0)

    def on_link_selection_changed(self):
        """Update the pricing widget when a vendor source is selected."""
        selection = self.dbsession.query(VendorListing).filter_by(id=self.product_links.get_selected_id()).first()
        self.product_pricing.set_vnd_source(selection)

    def on_show_hist_table(self):
        """Show the product history table."""
        self.history_stack.setCurrentWidget(self.history_table)

    def on_show_hist_chart(self):
        """Show the product history chart."""
        self.history_stack.setCurrentWidget(self.history_chart)

    def on_search_amazon(self):
        """Create a SearchAmazon operation."""
        dialog = SearchAmazonDialog(self)
        ok = dialog.exec_()

        if not ok:
            return

        terms = dialog.search_terms
        list_name = dialog.list_name

        op = Operation.SearchAmazon(params={'terms': terms, 'addtolist': list_name},
                                    priority=10)

        opsman = OperationsManager.get_instance()
        opsman.register_callback(op, self.search_amazon_callback)

        self.dbsession.add(op)
        self.dbsession.commit()

    def search_amazon_callback(self, op):
        """Re-populate the source box when a SearchAmazon operation has finished. Refresh the source view if
        search results were added.
        """
        self.populate_source_box()

        if self.selected_source and op.params['addtolist'] == self.selected_source.name:
            self.reload()

    def on_open_camel3(self):
        """Open the selected listing in CamelCamelCamel."""
        sku = self.dbsession.query(Listing.sku).filter_by(id=self.get_selected_id()).scalar()
        webbrowser.open('http://camelcamelcamel.com/search?sq=%s' % sku)

    def on_set_watch(self):
        """Modify the watch(es) on the listings selected in the source view."""
        dialog = SetWatchDialog(self)
        ok = dialog.exec_()
        if not ok:
            return

        time = dialog.period * 60 if dialog.has_watch else None

        for listing_id in self.source_view.selected_ids:
            dbhelpers.set_watch(self.dbsession, listing_id, time)

        self.dbsession.commit()



