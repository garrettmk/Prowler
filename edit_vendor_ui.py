# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edit_vendor.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_editVendorDialog(object):
    def setupUi(self, editVendorDialog):
        editVendorDialog.setObjectName("editVendorDialog")
        editVendorDialog.resize(366, 216)
        self.verticalLayout = QtWidgets.QVBoxLayout(editVendorDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(editVendorDialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.vendorBox = QtWidgets.QComboBox(editVendorDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.vendorBox.sizePolicy().hasHeightForWidth())
        self.vendorBox.setSizePolicy(sizePolicy)
        self.vendorBox.setObjectName("vendorBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.vendorBox)
        self.label_2 = QtWidgets.QLabel(editVendorDialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.nameLine = QtWidgets.QLineEdit(editVendorDialog)
        self.nameLine.setObjectName("nameLine")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.nameLine)
        self.label_3 = QtWidgets.QLabel(editVendorDialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.urlLine = QtWidgets.QLineEdit(editVendorDialog)
        self.urlLine.setObjectName("urlLine")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.urlLine)
        self.label_4 = QtWidgets.QLabel(editVendorDialog)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.taxBox = QtWidgets.QSpinBox(editVendorDialog)
        self.taxBox.setObjectName("taxBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.taxBox)
        self.label_5 = QtWidgets.QLabel(editVendorDialog)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.shippingBox = QtWidgets.QSpinBox(editVendorDialog)
        self.shippingBox.setObjectName("shippingBox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.shippingBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(editVendorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(editVendorDialog)
        self.buttonBox.accepted.connect(editVendorDialog.accept)
        self.buttonBox.rejected.connect(editVendorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(editVendorDialog)

    def retranslateUi(self, editVendorDialog):
        _translate = QtCore.QCoreApplication.translate
        editVendorDialog.setWindowTitle(_translate("editVendorDialog", "Edit Vendor"))
        self.label.setText(_translate("editVendorDialog", "Vendor:"))
        self.label_2.setText(_translate("editVendorDialog", "Name:"))
        self.label_3.setText(_translate("editVendorDialog", "URL:"))
        self.label_4.setText(_translate("editVendorDialog", "Tax rate:"))
        self.taxBox.setSuffix(_translate("editVendorDialog", "%"))
        self.label_5.setText(_translate("editVendorDialog", "Shipping rate:"))
        self.shippingBox.setSuffix(_translate("editVendorDialog", "%"))

