# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dragdroplists.ui'
#
# Created by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ListDragSelection(object):
    def setupUi(self, ListDragSelection):
        ListDragSelection.setObjectName(_fromUtf8("ListDragSelection"))
        ListDragSelection.resize(588, 329)
        self.gridLayout = QtGui.QGridLayout(ListDragSelection)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.shownItemsLabel = QtGui.QLabel(ListDragSelection)
        self.shownItemsLabel.setObjectName(_fromUtf8("shownItemsLabel"))
        self.gridLayout.addWidget(self.shownItemsLabel, 0, 0, 1, 1)
        self.choosedLabel = QtGui.QLabel(ListDragSelection)
        self.choosedLabel.setObjectName(_fromUtf8("choosedLabel"))
        self.gridLayout.addWidget(self.choosedLabel, 0, 2, 1, 1)
        self.availableFilterInput = QtGui.QLineEdit(ListDragSelection)
        self.availableFilterInput.setObjectName(_fromUtf8("availableFilterInput"))
        self.gridLayout.addWidget(self.availableFilterInput, 1, 0, 1, 1)
        self.choosedFilterInput = QtGui.QLineEdit(ListDragSelection)
        self.choosedFilterInput.setObjectName(_fromUtf8("choosedFilterInput"))
        self.gridLayout.addWidget(self.choosedFilterInput, 1, 2, 1, 1)
        self.availableView = QtGui.QListWidget(ListDragSelection)
        self.availableView.setDragEnabled(True)
        self.availableView.setDragDropOverwriteMode(False)
        self.availableView.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.availableView.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.availableView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.availableView.setUniformItemSizes(True)
        self.availableView.setObjectName(_fromUtf8("availableView"))
        self.gridLayout.addWidget(self.availableView, 3, 0, 1, 1)
        self.allGroup = QtGui.QWidget(ListDragSelection)
        self.allGroup.setObjectName(_fromUtf8("allGroup"))
        self.verticalLayout = QtGui.QVBoxLayout(self.allGroup)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.addAllInput = QtGui.QPushButton(self.allGroup)
        self.addAllInput.setObjectName(_fromUtf8("addAllInput"))
        self.verticalLayout.addWidget(self.addAllInput)
        self.removeAllInput = QtGui.QPushButton(self.allGroup)
        self.removeAllInput.setObjectName(_fromUtf8("removeAllInput"))
        self.verticalLayout.addWidget(self.removeAllInput)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.gridLayout.addWidget(self.allGroup, 3, 1, 1, 1)
        self.choosedView = QtGui.QListWidget(ListDragSelection)
        self.choosedView.setDragEnabled(True)
        self.choosedView.setDragDropOverwriteMode(False)
        self.choosedView.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.choosedView.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.choosedView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.choosedView.setUniformItemSizes(True)
        self.choosedView.setObjectName(_fromUtf8("choosedView"))
        self.gridLayout.addWidget(self.choosedView, 3, 2, 1, 1)

        self.retranslateUi(ListDragSelection)
        QtCore.QMetaObject.connectSlotsByName(ListDragSelection)

    def retranslateUi(self, ListDragSelection):
        ListDragSelection.setWindowTitle(QtGui.QApplication.translate("ListDragSelection", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.shownItemsLabel.setText(QtGui.QApplication.translate("ListDragSelection", "Verfügbare Felder:", None, QtGui.QApplication.UnicodeUTF8))
        self.choosedLabel.setText(QtGui.QApplication.translate("ListDragSelection", "Angezeigte Felder", None, QtGui.QApplication.UnicodeUTF8))
        self.availableFilterInput.setPlaceholderText(QtGui.QApplication.translate("ListDragSelection", "Filter", None, QtGui.QApplication.UnicodeUTF8))
        self.choosedFilterInput.setPlaceholderText(QtGui.QApplication.translate("ListDragSelection", "Filter", None, QtGui.QApplication.UnicodeUTF8))
        self.availableView.setSortingEnabled(False)
        self.addAllInput.setText(QtGui.QApplication.translate("ListDragSelection", "Alle hinzufügen", None, QtGui.QApplication.UnicodeUTF8))
        self.removeAllInput.setText(QtGui.QApplication.translate("ListDragSelection", "Alle entfernen", None, QtGui.QApplication.UnicodeUTF8))

