import webbrowser

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QComboBox, QWidgetAction, QMessageBox, QAction

from database import *
import dbhelpers

from dialogs import SelectListDialog


class BaseView(QWidget):
    """Base class for all main views. Provides a database session object, and toolbar actions."""

    def __init__(self, parent=None):
        super(BaseView, self).__init__(parent=parent)

        self.dbsession = Session()
        self.toolbar_actions = []

    def add_toolbar_action(self, action):
        """Add a custom toolbar action."""
        self.toolbar_actions.append(action)

    def add_toolbar_actions(self, actions):
        """Adds all actions in an iterable."""
        self.toolbar_actions.extend(actions)

    def remove_toolbar_action(self, action):
        """Remove a custom toolbar action."""
        self.toolbar_actions.remove(action)


class BaseSourceView(BaseView):
    """Base class for the AmazonView and VendorView classes."""

    def __init__(self, parent=None):
        super(BaseSourceView, self).__init__(parent=parent)

        self._shows_amazon = False
        self._source_table_widget = None
        self._product_details_widget = None
        self._product_links_widget = None
        self._selected_source = None

        # Set up the source selector
        self.sourceBox = QComboBox(self)
        source_box_action = QWidgetAction(self)
        source_box_action.setDefaultWidget(self.sourceBox)

        self.sourceBox.activated.connect(self.on_source_selection_changed)

        self.add_toolbar_action(source_box_action)

        # Create the other toolbar actions
        self.action_reload_source = QAction(QIcon('icons/reload.png'), 'Reload', self)
        self.action_delete_source = QAction(QIcon('icons/delete.png'), 'Delete', self)

        self.action_reload_source.triggered.connect(self.reload)
        self.action_delete_source.triggered.connect(self.delete_source)

        self.add_toolbar_actions([self.action_reload_source, self.action_delete_source])

        # Create some common context menu actions
        self.action_add_to_list = QAction(QIcon('icons/list.png'), 'Add to list...', self)
        self.action_remove_from_list = QAction(QIcon('icons/delete.png'), 'Remove from list...', self)
        self.action_open_in_browser = QAction(QIcon('icons/internet.png'), 'Open in browser...', self)
        self.action_open_in_google = QAction(QIcon('icons/search_google.png'), 'Open in Google...', self)
        self.action_lookup_upc = QAction(QIcon('icons/barcode.png'), 'Look up UPC...', self)
        self.action_unlink_products = QAction(QIcon('icons/unlink.png'), 'Unlink', self)

        # Context menu connections
        self.action_add_to_list.triggered.connect(self.on_add_to_list)
        self.action_remove_from_list.triggered.connect(self.on_remove_from_list)
        self.action_unlink_products.triggered.connect(self.on_unlink_products)
        self.action_open_in_browser.triggered.connect(self.on_open_in_browser)
        self.action_open_in_google.triggered.connect(self.on_open_in_google)
        self.action_lookup_upc.triggered.connect(self.on_lookup_upc)

    @property
    def source_table_widget(self):
        return self._source_table_widget

    @source_table_widget.setter
    def source_table_widget(self, widget):
        if self._source_table_widget:
            self._source_table_widget.selection_changed.disconnect(self.on_main_selection_changed)

        self._source_table_widget = widget
        self._source_table_widget.selection_changed.connect(self.on_main_selection_changed)

    @property
    def product_details_widget(self):
        return self._product_details_widget

    @product_details_widget.setter
    def product_details_widget(self, widget):
        self._product_details_widget = widget

    @property
    def product_links_widget(self):
        return self._product_links_widget

    @product_links_widget.setter
    def product_links_widget(self, widget):
        self._product_links_widget = widget

    @property
    def shows_amazon(self):
        """True if the view is designed to show Amazon listings."""
        return self._shows_amazon

    @shows_amazon.setter
    def shows_amazon(self, value):
        self._shows_amazon = bool(value)

    @property
    def selected_source(self):
        """Return the currently selected source object (Vendor or List)."""
        return self._selected_source

    def populate_source_box(self):
        """Populate the source combo box with appropriate vendor and list names."""
        # Build a list of vendor names
        condition = Vendor.name == 'Amazon' if self.shows_amazon else Vendor.name != 'Amazon'
        vendornames = [result.name for result in self.dbsession.query(Vendor.name).filter(condition)]
        if not self.shows_amazon:
            vendornames.insert(0, 'All vendor products')

        # Get all the appropriate list names
        listnames = [result.name for result in self.dbsession.query(List.name).filter_by(is_amazon=self.shows_amazon)]

        self.sourceBox.clear()
        self.sourceBox.addItems(vendornames)
        self.sourceBox.addItems(listnames)

    def on_source_selection_changed(self):
        """Respond to a change in the source selector combo box."""
        # Update the selected source
        sel_text = self.sourceBox.currentText()
        self.load_source(sel_text)

    def load_source(self, name):
        """Load the source with the provided name."""
        source = self.dbsession.query(Vendor).filter_by(name=name).first() \
                 or self.dbsession.query(List).filter_by(name=name).first()

        self._selected_source = source

        # Update the widgets
        if self._source_table_widget:
            self._source_table_widget.set_source(self._selected_source)

        if self._product_details_widget:
            self._product_details_widget.set_source(None)

        if self._product_links_widget:
            self._product_links_widget.set_source(None)

    def reload(self):
        """Reloads the currently selected source."""
        self.load_source(self._selected_source.name if self._selected_source else None)

    def on_main_selection_changed(self):
        """Respond to a change of selection in the main table view."""
        selection = self.dbsession.query(Listing).filter_by(id=self.get_selected_id()).first()

        if self._product_details_widget:
            self._product_details_widget.set_source(selection)

        if self._product_links_widget:
            self._product_links_widget.set_source(selection)

    def get_selected_ids(self):
        """Return the id's of the selected listing in the focused widget."""
        if self._product_links_widget and self._product_links_widget.hasFocus():
            return self._product_links_widget.selected_ids
        elif self._source_table_widget:
            return self._source_table_widget.selected_ids
        else:
            return []

    def get_selected_id(self):
        """Return the last item in the selection, or None."""
        selection = self.get_selected_ids()
        return selection[-1] if len(selection) else None

    def on_open_in_browser(self):
        """Open the selected listing in the browser."""
        listing = self.dbsession.query(Listing).filter_by(id=self.get_selected_id()).first()
        if listing is None:
            return

        url = listing.url
        if url is None and isinstance(listing, AmazonListing):
            url = 'http://www.amazon.com/dp/%s' % listing.sku
        elif url is None:
            QMessageBox.information(self, '', 'The selected listing does not have a URL.')
            return

        webbrowser.open(url)

    def on_open_in_google(self):
        """Open a google search of the selected listing."""
        listing = self.dbsession.query(Listing).filter_by(id=self.get_selected_id()).first()
        if listing is None:
            return

        if not listing or not listing.brand or not listing.model:
            QMessageBox.information(self, '', 'Listing, brand, or model missing.')
            return

        q = '{} {}'.format(listing.brand, listing.model).replace(' ', '+')
        url = 'http://www.google.com/?gws_rd=ssl#q={}'.format(q)

        webbrowser.open(url)

    def on_lookup_upc(self):
        """Open a UPC lookup website with the currently selected listing's UPC."""
        listing = self.dbsession.query(Listing).filter_by(id=self.get_selected_id()).first()

        if not listing or not listing.upc:
            QMessageBox.information(self, 'Error', 'No listing selected, or no UPC code available.')
            return

        url = 'http://www.upcitemdb.com/upc/%s' % listing.upc
        webbrowser.open(url)

    def delete_source(self):
        """Delete the currently selected list or vendor."""
        source_name = self.sourceBox.currentText()

        sel_source = self.dbsession.query(Vendor).filter_by(name=source_name).first() \
                        or self.dbsession.query(List).filter_by(name=source_name).first()

        if sel_source is None or source_name == 'Amazon':
            QMessageBox.information(self, 'Error', '\'%s\' cannot be deleted.' % source_name)
            return

        # Get confirmation
        if isinstance(sel_source, Vendor):
            question = 'Delete all products from vendor \'%s\'?' % sel_source.name
        elif isinstance(sel_source, List):
            question = 'Delete list \'%s\'?' % sel_source.name

        answer = QMessageBox.question(self, 'Confirm', question)

        if answer == QMessageBox.Yes:
            self.dbsession.delete(sel_source)
            self.dbsession.commit()
            self.populate_source_box()
            self.load_source(None)

    def on_add_to_list(self):
        """Add the selected listings to a list."""
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            return

        first = self.dbsession.query(Listing).filter_by(id=selected_ids[0]).first()
        is_amz = isinstance(first, AmazonListing)

        dialog = SelectListDialog(show_amazon=is_amz, readonly=False, parent=self)
        ok = dialog.exec_()
        if not ok:
            return

        dbhelpers.add_ids_to_list(self.dbsession, selected_ids, dialog.list_name)
        self.dbsession.commit()
        self.populate_source_box()

    def on_remove_from_list(self):
        """Removes the selected listings from a list."""
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            return

        first = self.dbsession.query(Listing).filter_by(id=selected_ids[0]).first()
        is_amz = isinstance(first, AmazonListing)

        dialog = SelectListDialog(show_amazon=is_amz, readonly=True, parent=self)
        ok = dialog.exec_()
        if not ok:
            return

        dbhelpers.remove_ids_from_list(self.dbsession, selected_ids, dialog.list_name)
        self.dbsession.commit()

        if self.selected_source and self.selected_source.name == dialog.list_name:
            self.reload()

    def on_unlink_products(self):
        """Unlink products selected from self.product_links_widget from the listing selected in the source table."""
        if not self._source_table_widget or not self._source_table_widget.selected_ids \
            or not self._product_links_widget or not self._product_links_widget.selected_ids:
            return

        if self.shows_amazon:
            amz_id = self._source_table_widget.selected_ids[-1]
            vnd_ids = self._product_links_widget.selected_ids

            for vnd_id in vnd_ids:
                dbhelpers.unlink_products(self.dbsession, amz_id, vnd_id)
        else:
            vnd_id = self._source_table_widget.selected_ids[-1]
            amz_ids = self._product_links_widget.selected_ids

            for amz_id in amz_ids:
                dbhelpers.unlink_products(self.dbsession, amz_id, vnd_id)

        self.dbsession.commit()
        self._product_links_widget.reload()



