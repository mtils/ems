'''
Created on 25.07.2012

@author: michi
'''
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, QVariant, Qt
from ems.qt4.util import variant_to_pyobject

class SummaryModel(QAbstractItemModel):

    def __init__(self, parent=None):
        QAbstractItemModel.__init__(self, parent)
        self._sourceModel = None
        self._resultCache = {}

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            return self._sourceModel.headerData(section, orientation, role)
        if role == Qt.DisplayRole:
            return QVariant('Sum')
        return QVariant()

    def onSourceModelDataChanged(self, topLeft, bottomRight):
        cols = []
        for col in range(topLeft.column(), bottomRight.column()+1):
            cols.append(col)
        self.recalculate(cols)

    def getMaxValue(self, col):
        maxVal = 0.0
        for row in range(self._sourceModel.rowCount()):
            index = self._sourceModel.index(row, col)
            value = variant_to_pyobject(self._sourceModel.data(index))
            if isinstance(value, (int,float)):
                maxVal = max(maxVal, value)
        return maxVal

    def recalculateAll(self):
        self.recalculate(range(self._sourceModel.columnCount()))

    def recalculate(self, columns):
        if not self._sourceModel or not len(columns):
            return

        for col in columns:
            colSum = 0.0
            for row in range(self._sourceModel.rowCount()):
                index = self._sourceModel.index(row, col)
                value = variant_to_pyobject(self._sourceModel.data(index))
                if isinstance(value, (int,float)):
                    colSum += value
            self._resultCache[col] = QVariant(colSum)

        self.dataChanged.emit(self.index(0,columns[0]),
                              self.index(0,col))

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()

        if role in (Qt.DisplayRole, Qt.EditRole):
            try:
                return self._resultCache[index.column()]
            except KeyError:
                return QVariant()
            except AttributeError:
                return QVariant()

        return QVariant()

    def parent(self, *args, **kwargs):
        return QModelIndex()

    def columnCount(self, parentIndex=QModelIndex()):
        if self._sourceModel:
            return self._sourceModel.columnCount(parentIndex)
        return 0

    def rowCount(self, parentIndex=QModelIndex()):
        return 1

    def index(self, row, col, parentIndex=QModelIndex()):
        return self.createIndex(row, col, parentIndex)

    def sourceModel(self):
        return self._sourceModel

    def setSourceModel(self, sourceModel):
        if isinstance(self._sourceModel, QAbstractItemModel):
            self._sourceModel.dataChanged.disconnect(self.onSourceModelDataChanged)
        self._sourceModel = sourceModel
        self._sourceModel.dataChanged.connect(self.onSourceModelDataChanged)
        self._sourceModel.modelReset.connect(self.recalculateAll)
        self.recalculateAll()
        return self
