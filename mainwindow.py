from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QAction, QToolBar, QApplication
from PyQt5.QtSql import QSqlDatabase

from database import *

from amazonview import AmazonView
from vendorview import VendorView
from operationsview import OperationsView

from dialogs import EditVendorDialog


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setup_ui()

        # UI connections
        self.action_open_amazon_view.triggered.connect(self.open_amazon)
        self.action_open_vendor_view.triggered.connect(self.open_vendor)
        self.action_open_operations.triggered.connect(self.open_operations)
        self.action_edit_vendors.triggered.connect(self.on_edit_vendors)

        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)

        self.current_tab = None

        # Set up the database connection.
        self.dbengine = create_engine('sqlite:///prowler.db')
        self.dbsession = Session(bind=self.dbengine)

        Base.metadata.create_all(self.dbengine)

        amazon = Vendor(id=0, name='Amazon', url='www.amazon.com')
        self.dbsession.add(self.dbsession.merge(amazon))
        self.dbsession.commit()

    def setup_ui(self):
        """Initialize the main window's UI components"""
        # Scale the window to the size of the screen
        desktop = QApplication.desktop()
        size = desktop.availableGeometry()

        self.resize(size.width() * .9, size.height() * .9)

        # Set up the toolbar
        self.toolBar = QToolBar(self)
        self.addToolBar(self.toolBar)

        # Create toolbar actions
        self.action_open_amazon_view = QAction(QIcon('icons/amazon.png'), 'Open Amazon view', self)
        self.action_open_vendor_view = QAction(QIcon('icons/folder.png'), 'Open Vendor view', self)
        self.action_open_operations = QAction(QIcon('icons/ops_view.png'), 'Open Operations', self)
        self.action_edit_vendors = QAction(QIcon('icons/vendor.png'), 'Edit vendors', self)

        # Add actions and separators to the toolbar
        self.toolBar.addActions([self.action_open_amazon_view,
                                self.action_open_vendor_view,
                                self.action_open_operations])

        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_edit_vendors)
        self.toolBar.addSeparator()

        # Create the central tab widget
        self.tabs = QTabWidget(self)
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)

        self.setCentralWidget(self.tabs)

    def on_edit_vendors(self):
        """Show the Edit Vendors dialog."""
        dialog = EditVendorDialog(parent=self)
        dialog.exec()

    def open_amazon(self):
        """Open a new AmazonView."""
        view = AmazonView(self)
        idx = self.tabs.addTab(view, 'Amazon')
        self.tabs.setCurrentIndex(idx)

    def open_vendor(self):
        """Open a new VendorView."""
        view = VendorView(self)
        idx = self.tabs.addTab(view, 'Sources')
        self.tabs.setCurrentIndex(idx)

    def open_operations(self):
        """Open, or re-focus, the Operations view."""
        # We only want one operations view open at a time
        for i in range(self.tabs.count()):
            if isinstance(self.tabs.widget(i), OperationsView):
                self.tabs.setCurrentIndex(i)
                return

        view = OperationsView(self)
        idx = self.tabs.addTab(view, 'Operations')
        self.tabs.setCurrentIndex(idx)

    def close_tab(self, index):
        """Respond to a tabCloseRequested signal."""
        self.tabs.removeTab(index)

    def tab_changed(self, index):
        """Re-populate the toolbar with the actions specific to the new tab."""
        if self.current_tab:
            for action in self.current_tab.toolbar_actions:
                self.toolBar.removeAction(action)

        self.current_tab = self.tabs.currentWidget()

        if self.current_tab:
            for action in self.current_tab.toolbar_actions:
                self.toolBar.addAction(action)