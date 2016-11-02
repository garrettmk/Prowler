from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import QAbstractItemView, QComboBox, QWidgetAction, QMenu
from PyQt5.QtSql import QSqlTableModel

from database import *

from abstractview import AbstractView
from productview_ui import Ui_productView
from dialogs import SelectListDialog


class ProductView(AbstractView, Ui_productView):

    def __init__(self, parent=None):
        super(ProductView, self).__init__(parent=parent)
        self.setupUi(self)

        # Set up the main model and table
        self.mainModel = QSqlTableModel(self)
        sort_model = QSortFilterProxyModel(self)
        sort_model.setSourceModel(self.mainModel)

        self.mainTable.setModel(sort_model)
        self.mainTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.mainTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.mainTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.mainTable.setSortingEnabled(True)
        self.mainTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mainTable.customContextMenuRequested.connect(self.mainTable_context_menu)

        # Set up common toolbar actions
        self.sourceBox = QComboBox(self)
        sourceBoxAction = QWidgetAction(self)
        sourceBoxAction.setDefaultWidget(self.sourceBox)

        self.tool_buttons = [sourceBoxAction, self.actionReload]

        # Set up common context menu actions
        self.mainTable_context_actions = [self.actionAdd_to_list]

        # Default UI connections
        self.sourceBox.currentTextChanged.connect(self.show_listings)
        self.actionAdd_to_list.triggered.connect(self.action_add_to_list)
        self.actionReload.triggered.connect(self.show_listings)

    def is_amazon(self):
        """Helper method, returns True if this view shows Amazon products, False if vendor products."""
        return False

    def show_listings(self):
        """Overridden in subclasses: generates a query and populates the main table."""
        pass

    def populate_source_box(self):
        """Populate the source combo box with appropriate vendor and list names."""
        if self.is_amazon():
            vendornames = ['All Amazon products']
        else:
            vendornames = ['All Vendor products']
            vendornames.extend([result.name for result in self.dbsession.query(Vendor.name) if result.name != 'Amazon'])

        listnames = [result.name for result in self.dbsession.query(List.name).filter_by(is_amazon=self.is_amazon())]

        self.sourceBox.clear()
        self.sourceBox.addItems(vendornames)
        self.sourceBox.addItems(listnames)

    def mainTable_context_menu(self, point):
        """Popup a context menu on the main table, using the actions in self.mainTable_context_actions."""
        menu = QMenu(self)
        menu.addActions(self.mainTable_context_actions)

        point = self.mainTable.viewport().mapToGlobal(point)
        menu.popup(point)

    def action_add_to_list(self):
        """Respond to the 'Add to List' menu action."""
        # Get the selected id's
        selection = self.mainTable.selectionModel().selectedRows()

        if not selection:
            return

        # Get the names of the lists already in the db
        list_names = [result.name for result in self.dbsession.query(List.name). \
            filter_by(is_amazon=self.is_amazon()). \
            all()]

        # Show the selection dialog
        dialog = SelectListDialog(list_names, self)
        ok = dialog.exec()
        if not ok:
            return

        # Get the selected list, or create a new list
        sel_list = self.dbsession.query(List).filter_by(name=dialog.list_name).scalar()
        if sel_list is None:
            sel_list = List(name=dialog.list_name, is_amazon=self.is_amazon())
            self.dbsession.add(sel_list)

        # Add the selected id's to the selected list
        listing_ids = [index.data() for index in selection]
        for listing_id in listing_ids:
            membership = self.dbsession.query(ListMembership). \
                filter_by(list_id=sel_list.id, listing_id=listing_id). \
                first()
            if membership:
                continue
            else:
                membership = ListMembership(list=sel_list, listing_id=listing_id)
                self.dbsession.add(membership)

        self.dbsession.commit()
        self.populate_source_box()
