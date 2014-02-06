
from PyQt4.QtCore import QModelIndex, QVariant, Qt
from PyQt4.QtGui import QSortFilterProxyModel
from ems.qt4.util import variant_to_pyobject

class SortFilterProxyModel(QSortFilterProxyModel):

    def pyData(self, index, role=Qt.DisplayRole):
        return variant_to_pyobject(self.data(index, role))

    def columnType(self, column):
        srcColumn = self.mapToSource(self.index(0, column)).column()
        return self.sourceModel().columnType(srcColumn)

    def nameOfColumn(self, column):
        srcColumn = self.mapToSource(self.index(0, column)).column()
        return self.sourceModel().nameOfColumn(srcColumn)

    def columnOfName(self, name):
        col = self.sourceModel().columnOfName(name)
        #Take my first Index, it could be row 0 is sorted out
        sourceIndex = self.mapToSource(self.index(0,0))
        return self.mapFromSource(self.sourceModel().index(sourceIndex.row(), col)).column()

    def childModel(self, index):
        srcIndex = self.mapToSource(index)
        return self.sourceModel().childModel(srcIndex)

    def getRowAsDict(self, row):
        sourceIndex = self.mapFromSource(self.createIndex(row,0))
        return self.sourceModel().getRowAsDict(sourceIndex.row())

class HideRowColumnModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)
        self.hiddenColumns = set()
        self.hiddenRows = set()

    def hideRow(self, row):
        self.hiddenRows.add(row)
        self.invalidateFilter()

    def showRow(self, row):
        self.hiddenRows.remove(row)
        self.invalidateFilter()

    def hideColumn(self, column):
        self.hiddenColumns.add(column)
        self.invalidateFilter()

    def showColumn(self, column):
        self.hiddenColumns.remove(column)
        self.invalidateFilter()

    def resetHiddenColumns(self):
        self.beginResetModel()
        self.hiddenColumns.clear()
        self.invalidateFilter()
        self.endResetModel()

    def resetHiddenRows(self):
        self.beginResetModel()
        self.hiddenRows.clear()
        self.invalidateFilter()
        self.endResetModel()

    def setHiddenColumns(self, columns):
        self.beginResetModel()
        self.blockSignals(True)
        self.resetHiddenColumns()
        self.blockSignals(False)
        for col in columns:
            self.hiddenColumns.add(col)
        self.invalidateFilter()
        self.endResetModel()

    def setHiddenRows(self, rows):
        self.beginResetModel()
        self.blockSignals(True)
        self.resetHiddenRows()
        self.blockSignals(False)
        for row in rows:
            self.hiddenRows.add(row)
        self.invalidateFilter()
        self.endResetModel()

    def setVisibleColumns(self, columns):
        if not self.sourceModel():
            return
        self.beginResetModel()
        self.blockSignals(True)
        self.resetHiddenColumns()
        self.blockSignals(False)
        for col in range(self.sourceModel().columnCount()):
            if col not in columns:
                self.hiddenColumns.add(col)
        self.invalidateFilter()
        self.endResetModel()

    def setVisibleRows(self, rows):
        if not self.sourceModel():
            return
        self.beginResetModel()
        self.blockSignals(True)
        self.resetHiddenRows()
        self.blockSignals(False)
        for row in range(self.sourceModel().rowCount()):
            if row not in rows:
                self.hiddenRows.add(row)
        self.invalidateFilter()
        self.endResetModel()

    def setVisibleColumnNames(self, names):
        columns = []
        for name in names:
            columns.append(self.columnOfName(name))
        return self.setVisibleColumns(columns)

    def setVisibleRowNames(self, names):
        rows = []
        for name in names:
            rows.append(self.rowOfName(name))
        return self.setVisibleRows(rows)

    def filterAcceptsColumn(self, sourceColumn, sourceParent):
        return not (sourceColumn in self.hiddenColumns)

    def filterAcceptsRow(self, sourceRow, sourceParent):
        return not (sourceRow in self.hiddenRows)

    def columnOfName(self, name):
        if self.sourceModel():
            return self.sourceModel().columnOfName(name)
        return -1

    def rowOfName(self, name):
        if self.sourceModel():
            return self.sourceModel().rowOfName(name)
        return -1

    def rowsOfName(self, name):
        if self.sourceModel():
            return self.sourceModel().rowsOfName(name)
        return []