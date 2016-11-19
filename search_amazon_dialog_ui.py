# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'search_amazon_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_searchAmazonDialog(object):
    def setupUi(self, searchAmazonDialog):
        searchAmazonDialog.setObjectName("searchAmazonDialog")
        searchAmazonDialog.resize(412, 125)
        self.formLayout = QtWidgets.QFormLayout(searchAmazonDialog)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(searchAmazonDialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.searchLine = QtWidgets.QLineEdit(searchAmazonDialog)
        self.searchLine.setObjectName("searchLine")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.searchLine)
        self.label_2 = QtWidgets.QLabel(searchAmazonDialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.listBox = QtWidgets.QComboBox(searchAmazonDialog)
        self.listBox.setEditable(True)
        self.listBox.setObjectName("listBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.listBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(searchAmazonDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi(searchAmazonDialog)
        self.buttonBox.accepted.connect(searchAmazonDialog.accept)
        self.buttonBox.rejected.connect(searchAmazonDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(searchAmazonDialog)

    def retranslateUi(self, searchAmazonDialog):
        _translate = QtCore.QCoreApplication.translate
        searchAmazonDialog.setWindowTitle(_translate("searchAmazonDialog", "Dialog"))
        self.label.setText(_translate("searchAmazonDialog", "Search terms:"))
        self.label_2.setText(_translate("searchAmazonDialog", "Add results to list:"))

