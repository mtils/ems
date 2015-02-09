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
    def setupUi(self, ListDragSelection, srcWidget=None, trgWidget=None):
        ListDragSelection.setObjectName(_fromUtf8("ListDragSelection"))
        ListDragSelection.resize(588, 329)
        self.gridLayout = QtGui.QGridLayout(ListDragSelection)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.shownItemsLabel = QtGui.QLabel(ListDragSelection)
        self.shownItemsLabel.setObjectName(_fromUtf8("shownItemsLabel"))
        self.gridLayout.addWidget(self.shownItemsLabel, 0, 0, 1, 1)
        self.trgLabel = QtGui.QLabel(ListDragSelection)
        self.trgLabel.setObjectName(_fromUtf8("trgLabel"))
        self.gridLayout.addWidget(self.trgLabel, 0, 2, 1, 1)
        self.srcFilterInput = QtGui.QLineEdit(ListDragSelection)
        self.srcFilterInput.setObjectName(_fromUtf8("srcFilterInput"))
        self.gridLayout.addWidget(self.srcFilterInput, 1, 0, 1, 1)
        self.trgFilterInput = QtGui.QLineEdit(ListDragSelection)
        self.trgFilterInput.setObjectName(_fromUtf8("trgFilterInput"))
        self.gridLayout.addWidget(self.trgFilterInput, 1, 2, 1, 1)
        if srcWidget is None:
            self.srcInput = QtGui.QListWidget(ListDragSelection)
        else:
            self.srcInput = srcWidget
        self.srcInput.setDragEnabled(True)
        self.srcInput.setDragDropOverwriteMode(False)
        self.srcInput.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        #self.srcInput.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.srcInput.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        #self.srcInput.setUniformItemSizes(True)
        self.srcInput.setObjectName(_fromUtf8("srcInput"))
        self.gridLayout.addWidget(self.srcInput, 3, 0, 1, 1)
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
        self.trgInput = QtGui.QListWidget(ListDragSelection)
        self.trgInput.setDragEnabled(True)
        self.trgInput.setDragDropOverwriteMode(False)
        self.trgInput.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.trgInput.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.trgInput.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.trgInput.setUniformItemSizes(True)
        self.trgInput.setObjectName(_fromUtf8("trgInput"))
        self.gridLayout.addWidget(self.trgInput, 3, 2, 1, 1)

        self.retranslateUi(ListDragSelection)
        QtCore.QMetaObject.connectSlotsByName(ListDragSelection)

    def retranslateUi(self, ListDragSelection):
        ListDragSelection.setWindowTitle(QtGui.QApplication.translate("ListDragSelection", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.shownItemsLabel.setText(QtGui.QApplication.translate("ListDragSelection", "Verfügbare Felder:", None, QtGui.QApplication.UnicodeUTF8))
        self.trgLabel.setText(QtGui.QApplication.translate("ListDragSelection", "Angezeigte Felder", None, QtGui.QApplication.UnicodeUTF8))
        self.srcFilterInput.setPlaceholderText(QtGui.QApplication.translate("ListDragSelection", "Filter", None, QtGui.QApplication.UnicodeUTF8))
        self.trgFilterInput.setPlaceholderText(QtGui.QApplication.translate("ListDragSelection", "Filter", None, QtGui.QApplication.UnicodeUTF8))
        self.srcInput.setSortingEnabled(False)
        self.addAllInput.setText(QtGui.QApplication.translate("ListDragSelection", "Alle hinzufügen", None, QtGui.QApplication.UnicodeUTF8))
        self.removeAllInput.setText(QtGui.QApplication.translate("ListDragSelection", "Alle entfernen", None, QtGui.QApplication.UnicodeUTF8))

