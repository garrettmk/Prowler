# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'productview.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_productView(object):
    def setupUi(self, productView):
        productView.setObjectName("productView")
        productView.resize(983, 693)
        self.verticalLayout = QtWidgets.QVBoxLayout(productView)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainTable = QtWidgets.QTableView(productView)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.mainTable.sizePolicy().hasHeightForWidth())
        self.mainTable.setSizePolicy(sizePolicy)
        self.mainTable.setObjectName("mainTable")
        self.verticalLayout.addWidget(self.mainTable)
        self.actionAdd_to_list = QtWidgets.QAction(productView)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/list-1.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionAdd_to_list.setIcon(icon)
        self.actionAdd_to_list.setObjectName("actionAdd_to_list")
        self.actionReload = QtWidgets.QAction(productView)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/repeat.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionReload.setIcon(icon1)
        self.actionReload.setObjectName("actionReload")

        self.retranslateUi(productView)
        QtCore.QMetaObject.connectSlotsByName(productView)

    def retranslateUi(self, productView):
        _translate = QtCore.QCoreApplication.translate
        productView.setWindowTitle(_translate("productView", "Form"))
        self.actionAdd_to_list.setText(_translate("productView", "Add to list..."))
        self.actionAdd_to_list.setToolTip(_translate("productView", "Add to list"))
        self.actionReload.setText(_translate("productView", "Reload"))
        self.actionReload.setToolTip(_translate("productView", "Reload"))

