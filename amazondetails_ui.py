# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'amazondetails.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_amazonViewDetails(object):
    def setupUi(self, amazonViewDetails):
        amazonViewDetails.setObjectName("amazonViewDetails")
        amazonViewDetails.resize(1220, 323)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(amazonViewDetails.sizePolicy().hasHeightForWidth())
        amazonViewDetails.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(amazonViewDetails)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.tabs = QtWidgets.QTabWidget(amazonViewDetails)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabs.sizePolicy().hasHeightForWidth())
        self.tabs.setSizePolicy(sizePolicy)
        self.tabs.setMinimumSize(QtCore.QSize(1150, 0))
        self.tabs.setObjectName("tabs")
        self.detailsTab = QtWidgets.QWidget()
        self.detailsTab.setObjectName("detailsTab")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.detailsTab)
        self.gridLayout_4.setContentsMargins(5, 5, 5, 5)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self.detailsTab)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.titleLine = QtWidgets.QLineEdit(self.detailsTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titleLine.sizePolicy().hasHeightForWidth())
        self.titleLine.setSizePolicy(sizePolicy)
        self.titleLine.setReadOnly(True)
        self.titleLine.setObjectName("titleLine")
        self.gridLayout_2.addWidget(self.titleLine, 0, 1, 1, 2)
        self.label_2 = QtWidgets.QLabel(self.detailsTab)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.brandLine = QtWidgets.QLineEdit(self.detailsTab)
        self.brandLine.setObjectName("brandLine")
        self.gridLayout_2.addWidget(self.brandLine, 1, 1, 1, 1)
        self.openAmazonBtn = QtWidgets.QPushButton(self.detailsTab)
        self.openAmazonBtn.setObjectName("openAmazonBtn")
        self.gridLayout_2.addWidget(self.openAmazonBtn, 1, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.detailsTab)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        self.modelLine = QtWidgets.QLineEdit(self.detailsTab)
        self.modelLine.setObjectName("modelLine")
        self.gridLayout_2.addWidget(self.modelLine, 2, 1, 1, 1)
        self.openGoogleBtn = QtWidgets.QPushButton(self.detailsTab)
        self.openGoogleBtn.setObjectName("openGoogleBtn")
        self.gridLayout_2.addWidget(self.openGoogleBtn, 2, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.detailsTab)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 3, 0, 1, 1)
        self.asinLine = QtWidgets.QLineEdit(self.detailsTab)
        self.asinLine.setObjectName("asinLine")
        self.gridLayout_2.addWidget(self.asinLine, 3, 1, 1, 1)
        self.openCamelBtn = QtWidgets.QPushButton(self.detailsTab)
        self.openCamelBtn.setObjectName("openCamelBtn")
        self.gridLayout_2.addWidget(self.openCamelBtn, 3, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.detailsTab)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 4, 0, 1, 1)
        self.upcLine = QtWidgets.QLineEdit(self.detailsTab)
        self.upcLine.setObjectName("upcLine")
        self.gridLayout_2.addWidget(self.upcLine, 4, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.detailsTab)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 5, 0, 1, 1)
        self.categoryLine = QtWidgets.QLineEdit(self.detailsTab)
        self.categoryLine.setObjectName("categoryLine")
        self.gridLayout_2.addWidget(self.categoryLine, 5, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.detailsTab)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 6, 0, 1, 1)
        self.salesRankLine = QtWidgets.QSpinBox(self.detailsTab)
        self.salesRankLine.setReadOnly(True)
        self.salesRankLine.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.salesRankLine.setProperty("showGroupSeparator", True)
        self.salesRankLine.setMaximum(999999999)
        self.salesRankLine.setProperty("value", 0)
        self.salesRankLine.setObjectName("salesRankLine")
        self.gridLayout_2.addWidget(self.salesRankLine, 6, 1, 1, 1)
        self.openUPCLookupBtn = QtWidgets.QPushButton(self.detailsTab)
        self.openUPCLookupBtn.setObjectName("openUPCLookupBtn")
        self.gridLayout_2.addWidget(self.openUPCLookupBtn, 4, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.line = QtWidgets.QFrame(self.detailsTab)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_2.addWidget(self.line)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.stackedWidget = QtWidgets.QStackedWidget(self.detailsTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.page)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.graphicsView = QtWidgets.QGraphicsView(self.page)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout_3.addWidget(self.graphicsView, 0, 0, 1, 1)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.page_2)
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.historyTable = QtWidgets.QTableView(self.page_2)
        self.historyTable.setObjectName("historyTable")
        self.gridLayout_5.addWidget(self.historyTable, 0, 0, 1, 1)
        self.stackedWidget.addWidget(self.page_2)
        self.verticalLayout_2.addWidget(self.stackedWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_8 = QtWidgets.QLabel(self.detailsTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout.addWidget(self.label_8)
        self.priceBox = QtWidgets.QDoubleSpinBox(self.detailsTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.priceBox.sizePolicy().hasHeightForWidth())
        self.priceBox.setSizePolicy(sizePolicy)
        self.priceBox.setMaximumSize(QtCore.QSize(80, 16777215))
        self.priceBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.priceBox.setReadOnly(True)
        self.priceBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.priceBox.setProperty("showGroupSeparator", True)
        self.priceBox.setMaximum(9999.0)
        self.priceBox.setProperty("value", 9999.0)
        self.priceBox.setObjectName("priceBox")
        self.horizontalLayout.addWidget(self.priceBox)
        self.label_11 = QtWidgets.QLabel(self.detailsTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout.addWidget(self.label_11)
        self.merchantLine = QtWidgets.QLineEdit(self.detailsTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.merchantLine.sizePolicy().hasHeightForWidth())
        self.merchantLine.setSizePolicy(sizePolicy)
        self.merchantLine.setObjectName("merchantLine")
        self.horizontalLayout.addWidget(self.merchantLine)
        self.label_9 = QtWidgets.QLabel(self.detailsTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout.addWidget(self.label_9)
        self.offersBox = QtWidgets.QSpinBox(self.detailsTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.offersBox.sizePolicy().hasHeightForWidth())
        self.offersBox.setSizePolicy(sizePolicy)
        self.offersBox.setMaximumSize(QtCore.QSize(40, 16777215))
        self.offersBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.offersBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.offersBox.setMaximum(999)
        self.offersBox.setProperty("value", 999)
        self.offersBox.setObjectName("offersBox")
        self.horizontalLayout.addWidget(self.offersBox)
        self.label_10 = QtWidgets.QLabel(self.detailsTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout.addWidget(self.label_10)
        self.primeLine = QtWidgets.QLineEdit(self.detailsTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.primeLine.sizePolicy().hasHeightForWidth())
        self.primeLine.setSizePolicy(sizePolicy)
        self.primeLine.setMaximumSize(QtCore.QSize(45, 16777215))
        self.primeLine.setMaxLength(5)
        self.primeLine.setReadOnly(True)
        self.primeLine.setObjectName("primeLine")
        self.horizontalLayout.addWidget(self.primeLine)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(2, 1)
        self.gridLayout_4.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.tabs.addTab(self.detailsTab, "")
        self.sourcingTab = QtWidgets.QWidget()
        self.sourcingTab.setObjectName("sourcingTab")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.sourcingTab)
        self.gridLayout_8.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.groupBox = QtWidgets.QGroupBox(self.sourcingTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.sourcesTable = QtWidgets.QTableView(self.groupBox)
        self.sourcesTable.setObjectName("sourcesTable")
        self.gridLayout_6.addWidget(self.sourcesTable, 0, 0, 1, 1)
        self.gridLayout_8.addWidget(self.groupBox, 0, 0, 2, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(self.sourcingTab)
        self.groupBox_3.setObjectName("groupBox_3")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox_3)
        self.formLayout.setContentsMargins(12, 12, -1, -1)
        self.formLayout.setObjectName("formLayout")
        self.label_16 = QtWidgets.QLabel(self.groupBox_3)
        self.label_16.setObjectName("label_16")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_16)
        self.amzQuantityBox = QtWidgets.QSpinBox(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.amzQuantityBox.sizePolicy().hasHeightForWidth())
        self.amzQuantityBox.setSizePolicy(sizePolicy)
        self.amzQuantityBox.setMaximumSize(QtCore.QSize(77, 16777215))
        self.amzQuantityBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.amzQuantityBox.setReadOnly(True)
        self.amzQuantityBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.amzQuantityBox.setMaximum(999999)
        self.amzQuantityBox.setObjectName("amzQuantityBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.amzQuantityBox)
        self.label_12 = QtWidgets.QLabel(self.groupBox_3)
        self.label_12.setObjectName("label_12")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_12)
        self.packagingBox = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.packagingBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.packagingBox.setMaximum(999.0)
        self.packagingBox.setProperty("value", 0.1)
        self.packagingBox.setObjectName("packagingBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.packagingBox)
        self.label_13 = QtWidgets.QLabel(self.groupBox_3)
        self.label_13.setObjectName("label_13")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_13)
        self.shippingBox = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.shippingBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.shippingBox.setMaximum(999.0)
        self.shippingBox.setProperty("value", 1.0)
        self.shippingBox.setObjectName("shippingBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.shippingBox)
        self.line_2 = QtWidgets.QFrame(self.groupBox_3)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.SpanningRole, self.line_2)
        self.label_14 = QtWidgets.QLabel(self.groupBox_3)
        self.label_14.setObjectName("label_14")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_14)
        self.costEachBox = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.costEachBox.sizePolicy().hasHeightForWidth())
        self.costEachBox.setSizePolicy(sizePolicy)
        self.costEachBox.setMaximumSize(QtCore.QSize(77, 16777215))
        self.costEachBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.costEachBox.setReadOnly(True)
        self.costEachBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.costEachBox.setMaximum(999.0)
        self.costEachBox.setObjectName("costEachBox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.costEachBox)
        self.gridLayout_8.addWidget(self.groupBox_3, 0, 1, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.sourcingTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.pricePointsTable = QtWidgets.QTableView(self.groupBox_2)
        self.pricePointsTable.setObjectName("pricePointsTable")
        self.gridLayout_7.addWidget(self.pricePointsTable, 0, 0, 1, 1)
        self.gridLayout_8.addWidget(self.groupBox_2, 0, 2, 2, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(self.sourcingTab)
        self.groupBox_4.setObjectName("groupBox_4")
        self.formLayout_2 = QtWidgets.QFormLayout(self.groupBox_4)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_15 = QtWidgets.QLabel(self.groupBox_4)
        self.label_15.setObjectName("label_15")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_15)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.volumeBox = QtWidgets.QSpinBox(self.groupBox_4)
        self.volumeBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.volumeBox.setMaximum(9999)
        self.volumeBox.setProperty("value", 1)
        self.volumeBox.setObjectName("volumeBox")
        self.horizontalLayout_3.addWidget(self.volumeBox)
        self.estVolumeBtn = QtWidgets.QToolButton(self.groupBox_4)
        self.estVolumeBtn.setObjectName("estVolumeBtn")
        self.horizontalLayout_3.addWidget(self.estVolumeBtn)
        self.formLayout_2.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.gridLayout_8.addWidget(self.groupBox_4, 1, 1, 1, 1)
        self.groupBox_5 = QtWidgets.QGroupBox(self.sourcingTab)
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.trackProductBtn = QtWidgets.QPushButton(self.groupBox_5)
        self.trackProductBtn.setObjectName("trackProductBtn")
        self.verticalLayout_4.addWidget(self.trackProductBtn)
        self.addToOrderBtn = QtWidgets.QPushButton(self.groupBox_5)
        self.addToOrderBtn.setObjectName("addToOrderBtn")
        self.verticalLayout_4.addWidget(self.addToOrderBtn)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem1)
        self.gridLayout_8.addWidget(self.groupBox_5, 0, 3, 2, 1)
        self.tabs.addTab(self.sourcingTab, "")
        self.gridLayout.addWidget(self.tabs, 0, 0, 1, 1)

        self.retranslateUi(amazonViewDetails)
        self.tabs.setCurrentIndex(1)
        self.stackedWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(amazonViewDetails)

    def retranslateUi(self, amazonViewDetails):
        _translate = QtCore.QCoreApplication.translate
        amazonViewDetails.setWindowTitle(_translate("amazonViewDetails", "Form"))
        self.label.setText(_translate("amazonViewDetails", "Title:"))
        self.label_2.setText(_translate("amazonViewDetails", "Brand:"))
        self.openAmazonBtn.setText(_translate("amazonViewDetails", "Amazon..."))
        self.label_3.setText(_translate("amazonViewDetails", "Model:"))
        self.openGoogleBtn.setText(_translate("amazonViewDetails", "Google..."))
        self.label_4.setText(_translate("amazonViewDetails", "ASIN:"))
        self.openCamelBtn.setText(_translate("amazonViewDetails", "CamelCamelCamel..."))
        self.label_5.setText(_translate("amazonViewDetails", "UPC:"))
        self.label_6.setText(_translate("amazonViewDetails", "Category:"))
        self.label_7.setText(_translate("amazonViewDetails", "Sales rank:"))
        self.openUPCLookupBtn.setText(_translate("amazonViewDetails", "UPC Lookup..."))
        self.label_8.setText(_translate("amazonViewDetails", "Price:"))
        self.priceBox.setPrefix(_translate("amazonViewDetails", "$"))
        self.label_11.setText(_translate("amazonViewDetails", "Merchant:"))
        self.label_9.setText(_translate("amazonViewDetails", "Offers:"))
        self.label_10.setText(_translate("amazonViewDetails", "Prime:"))
        self.primeLine.setPlaceholderText(_translate("amazonViewDetails", "False"))
        self.tabs.setTabText(self.tabs.indexOf(self.detailsTab), _translate("amazonViewDetails", "Product Details"))
        self.groupBox.setTitle(_translate("amazonViewDetails", "Vendor sources:"))
        self.groupBox_3.setTitle(_translate("amazonViewDetails", "Outbound costs:"))
        self.label_16.setText(_translate("amazonViewDetails", "Quantity"))
        self.label_12.setText(_translate("amazonViewDetails", "Packaging:"))
        self.packagingBox.setPrefix(_translate("amazonViewDetails", "$"))
        self.label_13.setText(_translate("amazonViewDetails", "Shipping:"))
        self.shippingBox.setPrefix(_translate("amazonViewDetails", "$"))
        self.label_14.setText(_translate("amazonViewDetails", "Total cost:"))
        self.costEachBox.setPrefix(_translate("amazonViewDetails", "$"))
        self.groupBox_2.setTitle(_translate("amazonViewDetails", "Price points:"))
        self.groupBox_4.setTitle(_translate("amazonViewDetails", "Volume:"))
        self.label_15.setText(_translate("amazonViewDetails", "Volume:"))
        self.estVolumeBtn.setText(_translate("amazonViewDetails", "Est."))
        self.groupBox_5.setTitle(_translate("amazonViewDetails", "Options:"))
        self.trackProductBtn.setText(_translate("amazonViewDetails", "Track this product"))
        self.addToOrderBtn.setText(_translate("amazonViewDetails", "Add to order..."))
        self.tabs.setTabText(self.tabs.indexOf(self.sourcingTab), _translate("amazonViewDetails", "Sourcing"))
