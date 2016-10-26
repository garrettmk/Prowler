import amazonmws, mwskeys
import arrow

from PyQt5.QtWidgets import QMainWindow, QTabWidget, QAction
from PyQt5.QtSql import QSqlDatabase

from database import *
from operations import OperationsManager

from mainwindow_ui import Ui_MainWindow
from views import AmazonView, VendorView, OperationsView
from dialogs import OperationDialog


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # UI connections
        self.actionOpen_Amazon_view.triggered.connect(self.open_amazon)
        self.actionOpen_Vendor_view.triggered.connect(self.open_vendor)
        self.actionOpen_Operations_view.triggered.connect(self.open_operations)

        # Set up the database connections
        # TODO: Add some error checking
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('prowler.db')
        db.open()

        self.dbengine = create_engine('sqlite:///prowler.db')
        self.dbsession = Session(bind=self.dbengine)

        Base.metadata.create_all(self.dbengine)

        # Set up the operations manager
        self.opsman = OperationsManager(self)

        # Set up the toolbar
        self.toolBar.addAction(self.actionOpen_Amazon_view)
        self.toolBar.addAction(self.actionOpen_Vendor_view)
        self.toolBar.addAction(self.actionOpen_Operations_view)
        self.toolBar.addSeparator()

        # Set up the tab widget
        self.tabs = QTabWidget(self)
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.setCentralWidget(self.tabs)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.current_tab = None

    def open_amazon(self):
        view = AmazonView(self)
        self.tabs.addTab(view, 'Amazon')

    def open_vendor(self):
        view = VendorView(self)
        self.tabs.addTab(view, 'Sources')

    def open_operations(self):
        view = OperationsView(self)
        self.tabs.addTab(view, 'Operations')

    def close_tab(self, index):
        self.tabs.removeTab(index)

    def tab_changed(self, index):
        if self.current_tab:
            for action in self.current_tab.toolbuttons:
                self.toolBar.removeAction(action)

        self.current_tab = self.tabs.currentWidget()

        if self.current_tab:
            for action in self.current_tab.toolbuttons:
                self.toolBar.addAction(action)
