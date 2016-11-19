# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'testmargins_params.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_testMarginsParams(object):
    def setupUi(self, testMarginsParams):
        testMarginsParams.setObjectName("testMarginsParams")
        testMarginsParams.resize(400, 127)
        self.verticalLayout = QtWidgets.QVBoxLayout(testMarginsParams)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(testMarginsParams)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.confidenceBox = QtWidgets.QSpinBox(testMarginsParams)
        self.confidenceBox.setMinimum(80)
        self.confidenceBox.setMaximum(100)
        self.confidenceBox.setObjectName("confidenceBox")
        self.gridLayout.addWidget(self.confidenceBox, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(testMarginsParams)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(testMarginsParams)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.listBox = QtWidgets.QComboBox(testMarginsParams)
        self.listBox.setEditable(True)
        self.listBox.setObjectName("listBox")
        self.gridLayout.addWidget(self.listBox, 2, 1, 1, 1)
        self.marginBox = QtWidgets.QSpinBox(testMarginsParams)
        self.marginBox.setMaximum(9999)
        self.marginBox.setProperty("value", 50)
        self.marginBox.setObjectName("marginBox")
        self.gridLayout.addWidget(self.marginBox, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 67, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(testMarginsParams)
        QtCore.QMetaObject.connectSlotsByName(testMarginsParams)

    def retranslateUi(self, testMarginsParams):
        _translate = QtCore.QCoreApplication.translate
        testMarginsParams.setWindowTitle(_translate("testMarginsParams", "Form"))
        self.label.setText(_translate("testMarginsParams", "Min. match confidence:"))
        self.confidenceBox.setSuffix(_translate("testMarginsParams", "%"))
        self.label_2.setText(_translate("testMarginsParams", "Min. profit margin:"))
        self.label_3.setText(_translate("testMarginsParams", "Add results to list:"))
        self.marginBox.setSuffix(_translate("testMarginsParams", "%"))

