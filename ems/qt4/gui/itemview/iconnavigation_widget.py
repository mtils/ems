from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ems.qt4.util import variant_to_pyobject
from ems.qt4.gui.widgets.graphical import ColorButton #@UnresolvedImport
from ems.qt4.gui.itemdelegate.iconview import IconViewDelegate #@UnresolvedImport
from ems.qt4.gui.itemview.iconnavigation import IconNavigationView

class IconNavigationWidget(IconNavigationView):
    def __init__(self, parent=None):
        IconNavigationView.__init__(self, parent)
        self.setModel(QStandardItemModel(self))

    def addItem(self, icon, title=None):
        return self.insertItem(self.count(), icon, title)

    def count(self):
        return self.model().rowCount()

    def currentIndex(self):
        return IconNavigationView.currentIndex()

    def setCurrentIndex(self, index):
        return IconNavigationView.setCurrentIndex(self, index)

    def insertItem(self, index, icon, title=None):
        if title is None:
            title = QString()
        if not isinstance(title, QString):
            title = QString.fromUtf8(title)

        item = QStandardItem(icon, title)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.model().insertRow(index, item)

    def itemData(self, index, role=Qt.UserRole):
        return self.model().index(index,0).data(role)

    def setItemData(self, index, value, role=Qt.UserRole):
        index = self.model().index(index,0)
        self.model().setData(index, value, role)

    def moveItem(self, fromIndex, toIndex):
        raise NotImplementedError()

    def isItemEnabled(self, index):
        index = self.model().index(index,0)
        return bool(int(self.model().flags(index)) & int(Qt.ItemIsEnabled))

    def setItemEnabled(self, index, enabled):
        index = self.model().index(index,0)
        item = self.model().item(index)
        if enabled:
            item.setFlags(item.flags() | Qt.ItemIsEnabled)
        else:
            item.setFlags(item.flags() ^ Qt.ItemIsEnabled)

    def itemIcon(self, index):
        return variant_to_pyobject(self.itemData(index, Qt.DecorationRole))

    def setItemIcon(self, index, icon):
        return self.setItemData(index, QVariant(icon), Qt.DecorationRole)

    def itemText(self, index):
        return variant_to_pyobject(self.itemData(index, Qt.DisplayRole))

    def setItemText(self, index, text):
        return self.setItemData(index, QVariant(text), Qt.DisplayRole)

    def itemTextColor(self, index):
        return variant_to_pyobject(self.itemData(index, Qt.ForegroundRole))

    def setItemTextColor(self, index, color):
        return self.setItemData(index, QVariant(color), Qt.ForegroundRole)

    def itemToolTip(self, index):
        return variant_to_pyobject(self.itemData(index, Qt.ToolTipRole))

    def setItemToolTip(self, index, tip):
        return self.setItemData(index, QVariant(tip), Qt.ToolTipRole)

    def itemWhatsThis(self, index):
        return variant_to_pyobject(self.itemData(index, Qt.WhatsThisRole))

    def setItemWhatsThis(self, index, whatsThis):
        return self.setItemData(index, QVariant(whatsThis), Qt.WhatsThisRole)

    def itemAt(self, pos):
        return self.indexAt(pos).row()