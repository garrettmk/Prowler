# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sourceview.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_sourceView(object):
    def setupUi(self, sourceView):
        sourceView.setObjectName("sourceView")
        sourceView.resize(983, 693)
        self.verticalLayout = QtWidgets.QVBoxLayout(sourceView)
        self.verticalLayout.setObjectName("verticalLayout")
        self.table = QtWidgets.QTableView(sourceView)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.table.sizePolicy().hasHeightForWidth())
        self.table.setSizePolicy(sizePolicy)
        self.table.setObjectName("table")
        self.verticalLayout.addWidget(self.table)
        self.tabs = QtWidgets.QTabWidget(sourceView)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.tabs.sizePolicy().hasHeightForWidth())
        self.tabs.setSizePolicy(sizePolicy)
        self.tabs.setObjectName("tabs")
        self.detailTab = QtWidgets.QWidget()
        self.detailTab.setObjectName("detailTab")
        self.tabs.addTab(self.detailTab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabs.addTab(self.tab_2, "")
        self.verticalLayout.addWidget(self.tabs)
        self.actionImport_CSV = QtWidgets.QAction(sourceView)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("148705-essential-collection/png/folder-14.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionImport_CSV.setIcon(icon)
        self.actionImport_CSV.setObjectName("actionImport_CSV")

        self.retranslateUi(sourceView)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(sourceView)

    def retranslateUi(self, sourceView):
        _translate = QtCore.QCoreApplication.translate
        sourceView.setWindowTitle(_translate("sourceView", "Form"))
        self.tabs.setTabText(self.tabs.indexOf(self.detailTab), _translate("sourceView", "Product Details"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_2), _translate("sourceView", "Tab 2"))
        self.actionImport_CSV.setText(_translate("sourceView", "Import CSV..."))
        self.actionImport_CSV.setToolTip(_translate("sourceView", "Import from CSV"))

