# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1078, 735)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1078, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionOpen_Amazon_view = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("resources/Amazon-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionOpen_Amazon_view.setIcon(icon)
        self.actionOpen_Amazon_view.setObjectName("actionOpen_Amazon_view")
        self.actionOpen_Vendor_view = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("148705-essential-collection/png/list-1.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionOpen_Vendor_view.setIcon(icon1)
        self.actionOpen_Vendor_view.setObjectName("actionOpen_Vendor_view")
        self.actionOpen_Operations_view = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("148705-essential-collection/png/settings-2.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionOpen_Operations_view.setIcon(icon2)
        self.actionOpen_Operations_view.setObjectName("actionOpen_Operations_view")
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Prowler"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionOpen_Amazon_view.setText(_translate("MainWindow", "Open Amazon view..."))
        self.actionOpen_Amazon_view.setToolTip(_translate("MainWindow", "Open Amazon view"))
        self.actionOpen_Vendor_view.setText(_translate("MainWindow", "Open Vendor view..."))
        self.actionOpen_Vendor_view.setToolTip(_translate("MainWindow", "Open Vendor view"))
        self.actionOpen_Operations_view.setText(_translate("MainWindow", "Open Operations view..."))
        self.actionOpen_Operations_view.setToolTip(_translate("MainWindow", "Open Operations view"))

