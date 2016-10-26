import csv
import arrow

from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtWidgets import QWidget, QDialog, QComboBox, QWidgetAction, QAbstractItemView
from PyQt5.QtSql import QSqlTableModel, QSqlQuery

from amazonview_ui import Ui_amazonView
from sourceview_ui import Ui_sourceView
from operationsview_ui import Ui_operationsView
from dialogs import ImportCSVDialog, ProgressDialog, OperationDialog

from database import *
from operations import OperationsManager


# Helper function to convert SQLAlchemy queries into QSqlQuery objects
def to_qsqlquery(sa_query):
    statement = sa_query.statement.compile()
    qtquery = QSqlQuery()
    qtquery.prepare(str(statement))
    for name, value in statement.params.items():
        qtquery.bindValue(':' + name, value)
    return qtquery


class ViewBase(QWidget):

    def __init__(self, parent=None):
        super(ViewBase, self).__init__(parent=parent)

        self.toolbuttons = []
        self._dbsession = None

    @property
    def dbsession(self):
        if self._dbsession is None:
            self._dbsession = Session()
        return self._dbsession


class AmazonView(ViewBase, Ui_amazonView):

    def __init__(self, parent=None):
        super(AmazonView, self).__init__(parent=parent)
        self.setupUi(self)

        self.toolbuttons = [self.actionSearch_Amazon]

        self.searchButton.clicked.connect(self.search)

    def search(self):
        pass

    def post_response(self):
        pass
        # reply = self.sender()
        # data = reply.readAll().data()
        # tree = etree.fromstring(data)
        #
        # self.textView.clear()
        # self.textView.setPlainText(etree.tostring(tree, pretty_print=True).decode())


class VendorView(ViewBase, Ui_sourceView):

    def __init__(self, parent=None):
        super(VendorView, self).__init__(parent=parent)
        self.setupUi(self)

        self.vendorBox = QComboBox(self)
        self.populate_vendor_box()

        # Set up the main model and table
        self.mainModel = QSqlTableModel(self)
        self.table.setModel(self.mainModel)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Set up the toolbar actions
        vendorBoxAction = QWidgetAction(self)
        vendorBoxAction.setDefaultWidget(self.vendorBox)

        self.toolbuttons = [self.actionImport_CSV, vendorBoxAction]

        # Make connections
        self.actionImport_CSV.triggered.connect(self.import_csv)
        self.vendorBox.currentTextChanged.connect(self.show_listings)

        # Final setup
        self.show_listings()

    def populate_vendor_box(self):
        vendornames = [result.name for result in self.dbsession.query(Vendor.name)]
        vendornames.insert(0, 'All')
        self.vendorBox.clear()
        self.vendorBox.addItems(vendornames)

    def show_listings(self, vendorname=None):
        query = self.dbsession.query(Vendor.name.label('Source'),
                                     VendorListing.sku.label('SKU'),
                                     VendorListing.brand.label('Brand'),
                                     VendorListing.model.label('Model'),
                                     VendorListing.quantity.label('Quantity'),
                                     VendorListing.price.label('Price'),
                                     VendorListing.title.label('Description'),
                                     VendorListing.lastupdate.label('Last Update')
                                     ).filter(Vendor.id == VendorListing.vendor_id)
        if vendorname and vendorname != 'All':
            query = query.filter(Vendor.name == vendorname)

        qtquery = to_qsqlquery(query)
        qtquery.exec_()
        self.mainModel.setQuery(qtquery)
        self.mainModel.select()

    def import_csv(self):
        """Opens the 'Import CSV' dialog, imports the contents into the database."""
        # Show the dialog
        dialog = ImportCSVDialog(self, [result.name for result in self.dbsession.query(Vendor.name)])
        ok = dialog.exec()

        if ok:
            filename = dialog.filename
            vendorname = dialog.vendorname
            startrow = dialog.startrow
            endrow = dialog.endrow

            try:
                vendor = self.dbsession.query(Vendor).filter_by(name=vendorname).one()
            except NoResultFound:
                vendor = Vendor(name=vendorname)
                vendor.id = self.dbsession.query(func.count(Vendor.id)).scalar() + 1
                self.dbsession.add(vendor)

            with open(filename) as file:
                dialog = ProgressDialog(minimum=startrow, maximum=endrow, parent=self)
                dialog.setModal(True)
                dialog.show()

                reader = csv.DictReader(file)

                for row in reader:
                    if reader.line_num < startrow:
                        continue
                    elif reader.line_num > endrow:
                        break

                    if dialog.result() == QDialog.Rejected:
                        dialog.close()
                        self.dbsession.rollback()
                        return

                    dialog.progress_value = reader.line_num
                    dialog.status_text = 'Importing row {} of {}...'.format(reader.line_num - startrow, endrow - startrow)
                    QCoreApplication.processEvents()

                    product = VendorListing()
                    product.vendor_id = vendor.id
                    product.sku = row.get('SKU') or vendorname[:10].replace(' ', '') + str(reader.line_num)
                    product.title = row.get('Title') or row.get('title')
                    product.brand = row.get('Brand') or row.get('brand')
                    product.model = row.get('Model') or row.get('model')
                    product.upc = row.get('UPC') or row.get('upc')
                    product.quantity = row.get('Quantity') or row.get('quantity')
                    product.price = row.get('Price') or row.get('price')
                    product.url = row.get('URL') or row.get('url')

                    ts = row.get('Timestamp') or row.get('timestamp')
                    if ts:
                        product.lastupdate = arrow.get(ts).datetime
                    else:
                        product.lastupdate = arrow.utcnow().datetime

                    self.dbsession.add(self.dbsession.merge(product))

            dialog.close()
            self.dbsession.commit()

            self.populate_vendor_box()
            self.vendorBox.setCurrentText(vendorname)


class OperationsView(ViewBase, Ui_operationsView):

    def __init__(self, parent=None):
        super(OperationsView, self).__init__(parent=parent)
        self.setupUi(self)
        self.toolbuttons = [self.actionStart, self.actionPause, self.actionNew_batch]

        self.opsman = OperationsManager()
        self.opsman.status_message.connect(self.statusMsgList.addItem)
        self.opsman.status_message.connect(self.statusMsgList.scrollToBottom)

        self.actionStart.triggered.connect(self.opsman.start)
        self.actionPause.triggered.connect(self.opsman.stop)
        self.actionNew_batch.triggered.connect(self.new_batch)

        self.update_counts()

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_counts)
        self.update_timer.start(5000)

    def update_counts(self):
        pending = self.dbsession.query(Operation).filter(Operation.complete==False).count()
        completed = self.dbsession.query(Operation).filter(Operation.complete==True).count()
        total = pending + completed

        est_time = 0
        for op_name in self.opsman.supported_ops:
            num = self.dbsession.query(Operation).\
                                 filter(Operation.complete == False).\
                                 filter(Operation.operation.like('%s%%' % op_name)).\
                                 count()

            est_time += num * self.opsman.mwsapi.throttle_limits(op_name).restore_rate

        self.pendingBox.setValue(pending)
        self.completedBox.setValue(completed)
        self.totalBox.setValue(total)

        m, s = divmod(est_time, 60)
        h, m = divmod(m, 60)

        self.timeRemaining.setText('%d hr %d min %d sec' % (h, m, s))

    def new_batch(self):
        amz_srcs = ['All']
        vnd_srcs = [result.name for result in self.dbsession.query(Vendor.name).all()]

        amz_ops = ['Update pricing']
        vnd_ops = ['ListMatchingProducts']

        dialog = OperationDialog(amz_sources=amz_srcs, vnd_sources=vnd_srcs,
                                 amz_ops=amz_ops, vnd_ops=vnd_ops, parent=self)
        ok = dialog.exec_()
        if not ok:
            return

        # Build the query
        src_type, src_list = dialog.source
        if src_type == 'Amazon':
            query = self.dbsession.query(AmazonListing)
        elif src_type == 'Vendor':
            query = self.dbsession.query(VendorListing)

        if dialog.no_linked_products and src_type == 'Amazon':
            query = query.filter(~AmazonListing.linked_products.any())
        elif dialog.no_linked_products and src_type == 'Vendor':
            query = query.filter(~VendorListing.linked_products.any())

        if dialog.filter_price and src_type == 'Amazon':
            query = query.filter(AmazonListing.price.between(dialog.min_price, dialog.max_price))
        elif dialog.filter_price and src_type == 'Vendor':
            query = query.filter(VendorListing.price.between(dialog.min_price, dialog.max_price))

        if src_type == 'Vendor':
            vid = self.dbsession.query(Vendor.id).filter_by(name=src_list).scalar()
            query = query.filter(VendorListing.vendor_id == vid)

        # Add to the operation table
        for row in query:
            op = Operation(operation=dialog.operation)
            op.scheduled = arrow.utcnow().datetime

            if src_type == 'Amazon':
                op.asin = row.asin
            elif src_type == 'Vendor':
                op.vendor_id = row.vendor_id
                op.sku = row.sku

            self.dbsession.add(op)

        self.dbsession.commit()
