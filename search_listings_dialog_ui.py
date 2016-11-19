# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'search_listings_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_searchListingsDialog(object):
    def setupUi(self, searchListingsDialog):
        searchListingsDialog.setObjectName("searchListingsDialog")
        searchListingsDialog.resize(864, 451)
        self.gridLayout = QtWidgets.QGridLayout(searchListingsDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(searchListingsDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.sourceBox = QtWidgets.QComboBox(searchListingsDialog)
        self.sourceBox.setMinimumSize(QtCore.QSize(200, 0))
        self.sourceBox.setObjectName("sourceBox")
        self.gridLayout.addWidget(self.sourceBox, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(searchListingsDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)
        self.keywordsLine = QtWidgets.QLineEdit(searchListingsDialog)
        self.keywordsLine.setObjectName("keywordsLine")
        self.gridLayout.addWidget(self.keywordsLine, 0, 3, 1, 1)
        self.searchButton = QtWidgets.QPushButton(searchListingsDialog)
        self.searchButton.setObjectName("searchButton")
        self.gridLayout.addWidget(self.searchButton, 0, 4, 1, 1)
        self.resultsTable = QtWidgets.QTableView(searchListingsDialog)
        self.resultsTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.resultsTable.setAlternatingRowColors(True)
        self.resultsTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.resultsTable.setSortingEnabled(True)
        self.resultsTable.setObjectName("resultsTable")
        self.gridLayout.addWidget(self.resultsTable, 1, 0, 1, 5)
        self.buttonBox = QtWidgets.QDialogButtonBox(searchListingsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 3, 1, 2)

        self.retranslateUi(searchListingsDialog)
        self.buttonBox.accepted.connect(searchListingsDialog.accept)
        self.buttonBox.rejected.connect(searchListingsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(searchListingsDialog)

    def retranslateUi(self, searchListingsDialog):
        _translate = QtCore.QCoreApplication.translate
        searchListingsDialog.setWindowTitle(_translate("searchListingsDialog", "Dialog"))
        self.label.setText(_translate("searchListingsDialog", "Select from:"))
        self.label_2.setText(_translate("searchListingsDialog", "Keywords:"))
        self.searchButton.setText(_translate("searchListingsDialog", "Search"))

