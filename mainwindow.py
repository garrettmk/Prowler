from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import QMainWindow, QTabWidget

from database import *

from mainwindow_ui import Ui_MainWindow
from operations import OperationsManager
from amazonview import AmazonView
from vendorview import VendorView
from operationsview import OperationsView


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
        self.dbengine = create_engine('sqlite:///prowler.db')
        self.dbsession = Session(bind=self.dbengine)

        Base.metadata.create_all(self.dbengine)

        amazon = Vendor(id=0, name='Amazon', url='www.amazon.com')
        self.dbsession.add(self.dbsession.merge(amazon))
        self.dbsession.commit()

        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setConnectOptions('QSQLITE_OPEN_READONLY')
        db.setDatabaseName('prowler.db')
        db.open()

        # Set up the operations manager
        self.opsman = OperationsManager.get_instance(self)

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
        idx = self.tabs.addTab(view, 'Amazon')
        self.tabs.setCurrentIndex(idx)

    def open_vendor(self):
        view = VendorView(self)
        idx = self.tabs.addTab(view, 'Sources')
        self.tabs.setCurrentIndex(idx)

    def open_operations(self):
        # We only want one operations view open at a time
        for i in range(self.tabs.count()):
            if isinstance(self.tabs.widget(i), OperationsView):
                self.tabs.setCurrentIndex(i)
                return

        view = OperationsView(self)
        idx = self.tabs.addTab(view, 'Operations')
        self.tabs.setCurrentIndex(idx)

    def close_tab(self, index):
        self.tabs.removeTab(index)

    def tab_changed(self, index):
        if self.current_tab:
            for action in self.current_tab.toolbar_actions:
                self.toolBar.removeAction(action)

        self.current_tab = self.tabs.currentWidget()

        if self.current_tab:
            for action in self.current_tab.toolbar_actions:
                self.toolBar.addAction(action)
