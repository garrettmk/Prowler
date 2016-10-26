# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'amazonview.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_amazonView(object):
    def setupUi(self, amazonView):
        amazonView.setObjectName("amazonView")
        amazonView.resize(925, 687)
        self.verticalLayout = QtWidgets.QVBoxLayout(amazonView)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textView = QtWidgets.QPlainTextEdit(amazonView)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.textView.sizePolicy().hasHeightForWidth())
        self.textView.setSizePolicy(sizePolicy)
        self.textView.setReadOnly(True)
        self.textView.setObjectName("textView")
        self.verticalLayout.addWidget(self.textView)
        self.tabs = QtWidgets.QTabWidget(amazonView)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.tabs.sizePolicy().hasHeightForWidth())
        self.tabs.setSizePolicy(sizePolicy)
        self.tabs.setObjectName("tabs")
        self.detailTab = QtWidgets.QWidget()
        self.detailTab.setObjectName("detailTab")
        self.searchLine = QtWidgets.QLineEdit(self.detailTab)
        self.searchLine.setGeometry(QtCore.QRect(80, 70, 113, 21))
        self.searchLine.setObjectName("searchLine")
        self.searchButton = QtWidgets.QPushButton(self.detailTab)
        self.searchButton.setGeometry(QtCore.QRect(210, 70, 113, 32))
        self.searchButton.setObjectName("searchButton")
        self.tabs.addTab(self.detailTab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabs.addTab(self.tab_2, "")
        self.verticalLayout.addWidget(self.tabs)
        self.actionSearch_Amazon = QtWidgets.QAction(amazonView)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("resources/icon256.gif"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSearch_Amazon.setIcon(icon)
        self.actionSearch_Amazon.setObjectName("actionSearch_Amazon")

        self.retranslateUi(amazonView)
        QtCore.QMetaObject.connectSlotsByName(amazonView)

    def retranslateUi(self, amazonView):
        _translate = QtCore.QCoreApplication.translate
        amazonView.setWindowTitle(_translate("amazonView", "Form"))
        self.searchButton.setText(_translate("amazonView", "Search"))
        self.tabs.setTabText(self.tabs.indexOf(self.detailTab), _translate("amazonView", "Product Details"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_2), _translate("amazonView", "Tab 2"))
        self.actionSearch_Amazon.setText(_translate("amazonView", "Search Amazon..."))
        self.actionSearch_Amazon.setToolTip(_translate("amazonView", "Search Amazon"))

