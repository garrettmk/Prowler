import arrow
import csv

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QAction, QHeaderView, QDialog, QAbstractItemView, QDataWidgetMapper

from database import *

from abstractview import saquery_to_qtquery
from productview import ProductView
from vnd_listing_details_ui import Ui_vendorListingDetails

from dialogs import ImportCSVDialog, ProgressDialog


class VendorListingDetails(QWidget, Ui_vendorListingDetails):

    def __init__(self, parent=None):
        super(VendorListingDetails, self).__init__(parent=parent)
        self.setupUi(self)

        self.titleLine.textChanged.connect(lambda: self.titleLine.home(False))

        # Set up the amazon links table
        self.amzLinksTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.amzLinksTable.setSelectionMode(QAbstractItemView.SingleSelection)


class VendorView(ProductView):

    def __init__(self, parent=None):
        super(VendorView, self).__init__(parent=parent)

        # Create the details section
        self.details = VendorListingDetails(self)
        self.layout().addWidget(self.details)

        # Set up the toolbar actions
        self.actionImport_CSV = QAction(self)
        icon = QIcon()
        icon.addPixmap(QPixmap("148705-essential-collection/png/folder-14.png"), QIcon.Normal, QIcon.On)
        self.actionImport_CSV.setIcon(icon)

        self.tool_buttons.append(self.actionImport_CSV)

        # Make connections
        self.actionImport_CSV.triggered.connect(self.import_csv)

        # Populate the table
        self.populate_source_box()
        self.show_listings()

        # Set up the data widget mapper
        mapper = QDataWidgetMapper(self)
        mapper.setModel(self.mainTable.model())
        self.mainTable.selectionModel().currentRowChanged.connect(mapper.setCurrentModelIndex)

        mapper.addMapping(self.details.titleLine, self.mainModel.fieldIndex('Description'))
        mapper.addMapping(self.details.brandLine, self.mainModel.fieldIndex('Brand'))
        mapper.addMapping(self.details.modelLine, self.mainModel.fieldIndex('Model'))
        mapper.addMapping(self.details.skuLine, self.mainModel.fieldIndex('SKU'))
        mapper.addMapping(self.details.upcLine, self.mainModel.fieldIndex('UPC'))
        mapper.addMapping(self.details.vendorLine, self.mainModel.fieldIndex('Vendor'))
        mapper.addMapping(self.details.priceBox, self.mainModel.fieldIndex('Price'))
        mapper.addMapping(self.details.urlLine, self.mainModel.fieldIndex('URL'))
        mapper.addMapping(self.details.quantityBox, self.mainModel.fieldIndex('Quantity'))
        mapper.addMapping(self.details.updatedLine, self.mainModel.fieldIndex('Updated'))

    def is_amazon(self):
        return False

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
