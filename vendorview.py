import arrow
import csv

from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QAction, QHeaderView, QDialog, QAbstractItemView, QDataWidgetMapper
from PyQt5.QtWidgets import QHBoxLayout, QTabWidget, QFrame
from PyQt5.QtSql import QSqlTableModel

from database import *

from abstractview import saquery_to_qtquery
from productview import ProductView, ProductDetailsWidget, ProductLinksWidget
from vnd_listing_details_ui import Ui_vendorListingDetails
from vnd_listing_links_ui import Ui_vndListingLinks

from dialogs import ImportCSVDialog, ProgressDialog


class VndProductDetailsWidget(ProductDetailsWidget, Ui_vendorListingDetails):

    def __init__(self, parent=None):
        super(VndProductDetailsWidget, self).__init__(parent=parent)
        # setupUi() is called by the base class

        self.mapper.addMapping(self.urlLine, self.productModel.fieldIndex('url'))
        self.mapper.addMapping(self.updatedLine, self.productModel.fieldIndex('updated'))

    def set_listing(self, listing):
        super(VndProductDetailsWidget, self).set_listing(listing)

        vnd_name = self.sel_listing.vendor.name if self.sel_listing else ''
        self.vendorLine.setText(vnd_name)

    def lines_home(self):
        super(VndProductDetailsWidget, self).lines_home()
        self.updatedLine.home(False)
        self.urlLine.home(False)


class VndProductLinksWidget(ProductLinksWidget):

    def __init__(self, parent=None):
        super(VndProductLinksWidget, self).__init__(parent=parent)
        # setupUi() is called by the parent class

    def set_listing(self, listing):
        super(VndProductLinksWidget, self).set_listing(listing)

        listing_id = listing.id if listing else None

        stmt = self.dbsession.query(LinkedProducts.confidence,
                                    AmazonListing).\
                              filter(LinkedProducts.vnd_listing_id == listing_id,
                                     LinkedProducts.amz_listing_id == AmazonListing.id).\
                              subquery()

        query = self.dbsession.query(stmt.c.id.label('id'),
                                     func.printf('%.1f%%', stmt.c.confidence).label('Conf.'),
                                     stmt.c.sku.label('ASIN'),
                                     stmt.c.title.label('Title'),
                                     stmt.c.price.label('Price'),
                                     stmt.c.quantity.label('Quantity'))

        qt_query = saquery_to_qtquery(query)
        qt_query.exec_()
        self.linksModel.setQuery(qt_query)
        self.linksModel.select()


class VendorView(ProductView):

    def __init__(self, parent=None):
        super(VendorView, self).__init__(parent=parent)

        self.vnd_listing = None

        # Create the details section
        self.details = VndProductDetailsWidget(self)
        self.links = VndProductLinksWidget(self)
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)

        details_layout = QHBoxLayout()
        details_layout.setContentsMargins(5, 0, 5, 5)
        details_layout.addWidget(self.details)
        details_layout.addWidget(line)
        details_layout.addWidget(self.links)

        details_widget = QWidget()
        details_widget.setLayout(details_layout)

        # Create tabs
        self.tabs = QTabWidget(self)
        self.tabs.addTab(details_widget, 'Product Details')

        self.layout().addWidget(self.tabs)

        # Connections
        self.mainTable.selectionModel().currentRowChanged.connect(self.on_selection_change)

        # Populate the table
        self.populate_source_box()
        self.show_listings()

        # Set up the toolbar actions
        self.actionImport_CSV = QAction(self)
        icon = QIcon()
        icon.addPixmap(QPixmap("148705-essential-collection/png/folder-14.png"), QIcon.Normal, QIcon.On)
        self.actionImport_CSV.setIcon(icon)

        self.tool_buttons.append(self.actionImport_CSV)

        # Make connections
        self.actionImport_CSV.triggered.connect(self.import_csv)

    def is_amazon(self):
        return False

    def on_selection_change(self, current, previous):
        src_idx = self.mainTable.model().mapToSource(current)
        id_idx = self.mainModel.index(src_idx.row(), self.mainModel.fieldIndex('id'))
        vnd_id = id_idx.data(Qt.DisplayRole)

        self.vnd_listing = self.dbsession.query(VendorListing).filter_by(id=vnd_id).one()
        self.details.set_listing(self.vnd_listing)
        self.links.set_listing(self.vnd_listing)

    def show_listings(self, source=None):
        query = self.dbsession.query(VendorListing.id,
                                     Vendor.name.label('Vendor'),
                                     VendorListing.sku.label('SKU'),
                                     VendorListing.brand.label('Brand'),
                                     VendorListing.model.label('Model'),
                                     VendorListing.quantity.label('Quantity'),
                                     VendorListing.price.label('Price'),
                                     VendorListing.title.label('Description'),
                                     VendorListing.updated.label('Updated'),
                                     VendorListing.url.label('URL')
                                     ).filter(Vendor.id == VendorListing.vendor_id)

        if source and source != 'All Vendor products':
            # Is it a vendor name?
            vendor_id = self.dbsession.query(Vendor.id).filter_by(name=source).scalar()
            if vendor_id:
                query = query.filter_by(vendor_id=vendor_id)
            else:
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

    def import_csv(self):
        """Opens the 'Import CSV' dialog, imports the contents into the database."""
        # Show the dialog
        sources = [result.name for result in self.dbsession.query(Vendor.name) if result.name != 'Amazon']
        dialog = ImportCSVDialog(self, sources)
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

                    sku = row.get('SKU') or vendorname[:10].replace(' ', '') + str(reader.line_num)
                    product = self.dbsession.query(VendorListing).filter_by(vendor_id=vendor.id, sku=sku).first()
                    if product is None:
                        product = VendorListing(vendor=vendor, sku=sku)
                        self.dbsession.add(product)

                    product.title = row.get('Title') or row.get('title')
                    product.brand = row.get('Brand') or row.get('brand')
                    product.model = row.get('Model') or row.get('model')
                    product.upc = row.get('UPC') or row.get('upc')
                    product.quantity = row.get('Quantity') or row.get('quantity')
                    product.price = row.get('Price') or row.get('price')
                    product.url = row.get('URL') or row.get('url')

                    ts = row.get('Timestamp') or row.get('timestamp')
                    if ts:
                        product.updated = arrow.get(ts).datetime
                    else:
                        product.updated = arrow.utcnow().datetime

            self.dbsession.commit()

            dialog.close()
            self.populate_source_box()
            self.sourceBox.setCurrentText(vendorname)
