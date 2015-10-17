
from PyQt4.QtCore import QModelIndex, Qt, QVariant

from ems.qt4.itemmodel.editable_proxymodel import EditableProxyModel


class OrientationSwapModel(EditableProxyModel):

    def __init__(self, parent=None):
        super(OrientationSwapModel, self).__init__(parent)

    def mapToSource(self, proxyIndex):

        if not self.sourceModel():
            return QModelIndex()

        return self.sourceModel().index(proxyIndex.column(), proxyIndex.row())

    def mapFromSource(self, sourceIndex):
        return self.index(sourceIndex.column(), sourceIndex.row())

    def index(self, row, column, parentIndex=QModelIndex()):
        return self.createIndex(row, column, parentIndex)

    def parent(self, index):
        return QModelIndex()

    def rowCount(self, parentIndex=QModelIndex()):
        return 0 if not self.sourceModel() else self.sourceModel().columnCount()

    def columnCount(self, parentIndex=QModelIndex()):
        return 0 if not self.sourceModel() else self.sourceModel().rowCount()

    def headerData(self, section, orientation, role=Qt.DisplayRole):

        if not self.sourceModel():
            return QVariant()

        orientation = Qt.Vertical if orientation == Qt.Horizontal else Qt.Horizontal

        return self.sourceModel().headerData(section, orientation, role)