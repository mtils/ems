
from PyQt4.QtCore import QModelIndex, QVariant
from PyQt4.QtGui import QSortFilterProxyModel

class HideRowColumnModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)
        self.hiddenColumns = set()
        self.hiddenRows = set()

    def hideRow(self, row):
        self.hiddenRows.add(row)

    def showRow(self, row):
        self.hiddenRows.remove(row)

    def hideColumn(self, column):
        self.hiddenColumns.add(column)

    def showColumn(self, column):
        self.hiddenColumns.remove(column)

    def resetHiddenColumns(self):
        self.beginResetModel()
        self.hiddenColumns.clear()
        self.endResetModel()

    def resetHiddenRows(self):
        self.beginResetModel()
        self.hiddenRows.clear()
        self.endResetModel()

    def setHiddenColumns(self, columns):
        self.beginResetModel()
        self.blockSignals(True)
        self.resetHiddenColumns()
        self.blockSignals(False)
        for col in columns:
            self.hiddenColumns.add(col)
        self.endResetModel()

    def setHiddenRows(self, rows):
        self.beginResetModel()
        self.blockSignals(True)
        self.resetHiddenRows()
        self.blockSignals(False)
        for row in rows:
            self.hiddenRows.add(row)
        self.endResetModel()

    def filterAcceptsColumn(self, sourceColumn, sourceParent):
        return not (sourceColumn in self.hiddenColumns)

    def filterAcceptsRow(self, sourceRow, sourceParent):
        return not (sourceRow in self.hiddenRows)