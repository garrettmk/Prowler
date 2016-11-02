# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'selectlist.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_selectListDialog(object):
    def setupUi(self, selectListDialog):
        selectListDialog.setObjectName("selectListDialog")
        selectListDialog.resize(400, 86)
        selectListDialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(selectListDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.listNameBox = QtWidgets.QComboBox(selectListDialog)
        self.listNameBox.setEditable(True)
        self.listNameBox.setObjectName("listNameBox")
        self.gridLayout.addWidget(self.listNameBox, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(selectListDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(selectListDialog)
        self.buttonBox.accepted.connect(selectListDialog.accept)
        self.buttonBox.rejected.connect(selectListDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(selectListDialog)

    def retranslateUi(self, selectListDialog):
        _translate = QtCore.QCoreApplication.translate
        selectListDialog.setWindowTitle(_translate("selectListDialog", "Select List"))

