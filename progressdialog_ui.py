# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'progressdialog.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_progressDialog(object):
    def setupUi(self, progressDialog):
        progressDialog.setObjectName("progressDialog")
        progressDialog.resize(400, 104)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(progressDialog.sizePolicy().hasHeightForWidth())
        progressDialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(progressDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.statusLabel = QtWidgets.QLabel(progressDialog)
        self.statusLabel.setObjectName("statusLabel")
        self.verticalLayout.addWidget(self.statusLabel)
        self.progressBar = QtWidgets.QProgressBar(progressDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.buttonBox = QtWidgets.QDialogButtonBox(progressDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(progressDialog)
        self.buttonBox.accepted.connect(progressDialog.accept)
        self.buttonBox.rejected.connect(progressDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(progressDialog)

    def retranslateUi(self, progressDialog):
        _translate = QtCore.QCoreApplication.translate
        progressDialog.setWindowTitle(_translate("progressDialog", "Dialog"))
        self.statusLabel.setText(_translate("progressDialog", "(Status)"))

