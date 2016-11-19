# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'watch_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_setWatchDialog(object):
    def setupUi(self, setWatchDialog):
        setWatchDialog.setObjectName("setWatchDialog")
        setWatchDialog.resize(259, 118)
        self.verticalLayout = QtWidgets.QVBoxLayout(setWatchDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.noWatchBtn = QtWidgets.QRadioButton(setWatchDialog)
        self.noWatchBtn.setObjectName("noWatchBtn")
        self.gridLayout.addWidget(self.noWatchBtn, 0, 0, 1, 1)
        self.watchBtn = QtWidgets.QRadioButton(setWatchDialog)
        self.watchBtn.setChecked(True)
        self.watchBtn.setObjectName("watchBtn")
        self.gridLayout.addWidget(self.watchBtn, 1, 0, 1, 1)
        self.periodBox = QtWidgets.QDoubleSpinBox(setWatchDialog)
        self.periodBox.setDecimals(1)
        self.periodBox.setMinimum(0.5)
        self.periodBox.setMaximum(24.0)
        self.periodBox.setSingleStep(0.5)
        self.periodBox.setObjectName("periodBox")
        self.gridLayout.addWidget(self.periodBox, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(setWatchDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(setWatchDialog)
        self.buttonBox.accepted.connect(setWatchDialog.accept)
        self.buttonBox.rejected.connect(setWatchDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(setWatchDialog)

    def retranslateUi(self, setWatchDialog):
        _translate = QtCore.QCoreApplication.translate
        setWatchDialog.setWindowTitle(_translate("setWatchDialog", "Set Watch"))
        self.noWatchBtn.setText(_translate("setWatchDialog", "No watch"))
        self.watchBtn.setText(_translate("setWatchDialog", "Update every:"))
        self.periodBox.setSuffix(_translate("setWatchDialog", " hr"))

