import csv

from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QAction, QHeaderView, QDialog, QAbstractItemView, QDataWidgetMapper
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QTabWidget, QFrame, QMessageBox

from database import *
import dbhelpers

from prowlerwidgets import ProwlerTableWidget, ProductDetailsWidget
from baseview import BaseSourceView
from dialogs import ImportCSVDialog, ProgressDialog, EditVendorDialog

from vnd_listing_details_ui import Ui_vendorListingDetails


class VndProductDetailsWidget(ProductDetailsWidget, Ui_vendorListingDetails):
    """A subclass of ProductDetailsWidget, specialize to show VendorListing details."""

    def __init__(self, parent=None):
        super(VndProductDetailsWidget, self).__init__(parent=parent)
        # setupUi() is called by the base class

        self.mapper.addMapping(self.urlLine, self.model.fieldIndex('url'))
        self.mapper.addMapping(self.updatedLine, self.model.fieldIndex('updated'))

        # Update other fields
        self.mapper.currentIndexChanged.connect(self.update_vendor)

        # Edit vendor
        self.openVendorBtn.clicked.connect(self.on_edit_vendor)

    def generate_query(self, source):
        """Build a query object to use for populating the data mapper."""
        vnd_id = getattr(source, 'id', None)
        return self.dbsession.query(VendorListing.title, VendorListing.brand, VendorListing.model,
                                    VendorListing.sku, VendorListing.upc, VendorListing.price,
                                    VendorListing.quantity, VendorListing.url, VendorListing.updated).\
                              filter_by(id=vnd_id)

    def update_vendor(self):
        """Manually update the vendor name field. It isn't covered by the data mapper."""
        vnd_name = self.source.vendor.name if self.source else ''
        self.vendorLine.setText(vnd_name)

    def rewind_lines(self):
        super(VndProductDetailsWidget, self).rewind_lines()
        self.updatedLine.home(False)
        self.urlLine.home(False)

    def on_edit_vendor(self):
        if self.source is None:
            QMessageBox.information(self, 'Error', 'No product selected.')
            return

        dialog = EditVendorDialog(default=self.source.vendor.name, parent=self)
        dialog.exec()


class VndProductLinksWidget(ProwlerTableWidget):
    """A subclass of ProductLinksWidget, specialized to show AmazonListings linked to a parent VendorListing"""

    def __init__(self, parent=None):
        super(VndProductLinksWidget, self).__init__(parent=parent)
        # setupUi() is called by the parent class

        # Populate the columns
        self.set_source(None)

        # Table setup
        self.table.horizontalHeader().setSectionResizeMode(self.model.fieldIndex('Title'), QHeaderView.Stretch)
        self.table.verticalHeader().hide()

    def generate_query(self, source):
        """Return the SQLAlchemy query used to populate the table."""
        source_id = getattr(source, 'id', None)

        stmt = self.dbsession.query(LinkedProducts.confidence,
                                    AmazonListing).\
                              filter(LinkedProducts.vnd_listing_id == source_id,
                                     LinkedProducts.amz_listing_id == AmazonListing.id).\
                              subquery()

        query = self.dbsession.query(stmt.c.id.label('id'),
                                     func.printf('%.1f%%', stmt.c.confidence).label('Conf.'),
                                     stmt.c.sku.label('ASIN'),
                                     stmt.c.title.label('Title'),
                                     stmt.c.price.label('Price'),
                                     stmt.c.quantity.label('Quantity'))
        return query


class VndSourceViewWidget(ProwlerTableWidget):
    """Shows listings belonging to a vendor or vendor-product list."""

    def __init__(self, parent=None):
        super(VndSourceViewWidget, self).__init__(parent=parent)

        # Populate table columns
        self.set_source(None)

        # Table setup
        self.table.horizontalHeader().setSectionResizeMode(self.model.fieldIndex('Title'), QHeaderView.Stretch)

    def generate_query(self, source):
        query = self.dbsession.query(VendorListing.id.label('id'),
                                     Vendor.name.label('Vendor'),
                                     VendorListing.sku.label('SKU'),
                                     VendorListing.brand.label('Brand'),
                                     VendorListing.model.label('Model'),
                                     VendorListing.quantity.label('Quantity'),
                                     VendorListing.price.label('Price'),
                                     VendorListing.title.label('Title'),
                                     VendorListing.updated.label('Updated'),
                                     VendorListing.url.label('URL')
                                     ).filter(Vendor.id == VendorListing.vendor_id)

        if isinstance(source, Vendor):
            query = query.filter_by(vendor_id=source.id)
        if isinstance(source, List):
            query = query.join(ListMembership).filter_by(list_id=source.id)

        return query


class VendorView(BaseSourceView):
    """View of a vendor-based source, with product details and linked listings widgets."""
    def __init__(self, parent=None):
        super(VendorView, self).__init__(parent=parent)
        self.shows_amazon = False

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Create the main table
        self.source_view = VndSourceViewWidget(self)
        self.layout().addWidget(self.source_view)

        # Create the tab section
        self.tabs = QTabWidget(self)
        self.layout().addWidget(self.tabs)

        # Create the 'Product Details' tab
        details_layout = QHBoxLayout()
        details_layout.setContentsMargins(5, 0, 5, 5)

        self.product_details = VndProductDetailsWidget(self)
        details_layout.addWidget(self.product_details)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        details_layout.addWidget(line)

        self.product_links = VndProductLinksWidget(self)
        details_layout.addWidget(self.product_links)

        details_widget = QWidget()
        details_widget.setLayout(details_layout)

        self.tabs.addTab(details_widget, 'Product Details')

        # Tell the parent class which widgets to use
        self.source_table_widget = self.source_view
        self.product_details_widget = self.product_details
        self.product_links_widget = self.product_links

        # Set up the context actions
        self.source_view.double_clicked.connect(self.action_open_in_browser.trigger)
        self.source_view.add_context_actions([self.action_add_to_list,
                                              self.action_remove_from_list,
                                              self.action_open_in_browser,
                                              self.action_open_in_google,
                                              self.action_lookup_upc])

        self.product_links.double_clicked.connect(self.action_open_in_browser.trigger)
        self.product_links.add_context_actions([self.action_unlink_products,
                                                self.action_open_in_browser,
                                                self.action_open_in_google,
                                                self.action_lookup_upc])

        self.product_details.openGoogleBtn.clicked.connect(self.action_open_in_google.trigger)
        self.product_details.openUPCLookupBtn.clicked.connect(self.action_lookup_upc.trigger)

        # Set up custom toolbar actions
        self.action_import_csv = QAction(QIcon('icons/open.png'), 'Import from CSV...', self)
        self.action_import_csv.triggered.connect(self.on_import_csv)

        self.add_toolbar_action(self.action_import_csv)

        # Populate the sources list
        self.populate_source_box()

    def on_import_csv(self):
        """Opens the 'Import CSV' dialog, imports the contents into the database."""
        # Show the dialog
        dialog = ImportCSVDialog(self)
        ok = dialog.exec()
        if not ok:
            return

        file_name = dialog.filename
        vendor_name = dialog.vendorname
        start_row = dialog.startrow
        end_row = dialog.endrow

        vendor = dbhelpers.get_or_create(self.dbsession, Vendor, name=vendor_name)
        self.dbsession.flush()

        add_list = dbhelpers.get_or_create(self.dbsession, List, name=dialog.list_name) if dialog.list_name else None

        with open(file_name) as file:
            dialog = ProgressDialog(minimum=start_row, maximum=end_row, parent=self)
            dialog.setModal(True)
            dialog.show()

            reader = csv.DictReader(file)

            for row in reader:
                if reader.line_num < start_row:
                    continue
                elif reader.line_num > end_row:
                    break

                if dialog.result() == QDialog.Rejected:
                    dialog.close()
                    self.dbsession.rollback()
                    return

                dialog.progress_value = reader.line_num
                dialog.status_text = 'Importing row {} of {}...'.format(reader.line_num - start_row, end_row - start_row)
                QCoreApplication.processEvents()

                sku = row.get('sku')

                product = dbhelpers.get_or_create(self.dbsession, VendorListing, vendor_id=vendor.id, sku=sku)

                product.title = row.get('title')
                product.brand = row.get('brand')
                product.model = row.get('model')
                product.upc = row.get('upc')
                product.quantity = row.get('quantity')
                product.price = row.get('price')
                product.url = row.get('url')
                product.updated = func.now()

                if add_list:
                    dbhelpers.get_or_create(self.dbsession, ListMembership, list=add_list, listing=product)

        self.dbsession.commit()

        dialog.close()
        self.populate_source_box()
        self.sourceBox.setCurrentText(vendor_name)
        self.sourceBox.activated.emit(0)
