
from __future__ import print_function

from PyQt4.QtCore import pyqtSignal, Qt, QVariant, QString, QModelIndex
import uuid

from ems.typehint import accepts
from ems.validation.abstract import ValidationError
from ems.qt4 import ColumnNameRole
from ems.qt4.util import variant_to_pyobject as py, cast_to_variant as variant
from ems.qt4.itemmodel.editable_proxymodel import EditableProxyModel

class BufferedModel(EditableProxyModel):

    dirtyStateChanged = pyqtSignal([bool],[int, bool])

    def __init__(self, parent=None):

        super(BufferedModel, self).__init__(parent)

        self._buffer = {}
        self._insertedId = ''

    def data(self, proxyIndex, role=Qt.DisplayRole):

        if role not in (Qt.EditRole, Qt.DisplayRole):
            return super(BufferedModel, self).data(proxyIndex, role)

        try:
            return self._buffer[proxyIndex.row()][proxyIndex.column()]
        except KeyError:
            pass

        if not self.isUninsertedRow(proxyIndex.row()):
            return super(BufferedModel, self).data(proxyIndex, role)

        try:
            return self._buffer[self._insertedId][proxyIndex.column()]
        except KeyError:
            return QVariant()


    def setData(self, index, value, role=Qt.EditRole):

        if role != Qt.EditRole:
            return False

        if self.isUninsertedRow(index.row()):
            return self._writeToUninsertedRow(index, value)

        if index.row() not in self._buffer:
            self._buffer[index.row()] = {}
            self.dirtyStateChanged[int, bool].emit(index.row(), True)

        self._buffer[index.row()][index.column()] = value

        self.dataChanged.emit(index, index)

        return True

    def submitRow(self, row):

        isUninserted = self.isUninsertedRow(row)

        if not row in self._buffer and not isUninserted:
            return False

        bufferIndex = row

        source = self.sourceModel()

        if isUninserted:
            bufferIndex = self._insertedId
            self.blockSignals(True)
            source.insertRow(row)
            self.blockSignals(False)

        for column in self._buffer[bufferIndex]:
            index = source.createIndex(row, column)
            source.setData(index, self._buffer[bufferIndex][column])

        if isUninserted:
            self._insertedId = ''

        self._emptyBuffer(row, bufferIndex)

        return True

    def revertRow(self, row):

        if not self.isUninsertedRow(row):
            return self._emptyBuffer(row)

        self.beginRemoveRows(QModelIndex(), row, row)

        try:
            del self._buffer[self._insertedId]
        except KeyError:
            pass

        self._insertedId = ''

        self.endRemoveRows()

    def isDirty(self, row=None):

        if row is None:
            return bool(self._buffer)

        if self.isUninsertedRow(row):
            return self._insertedId in self._buffer

        return row in self._buffer

    def insertRows(self, row, count, parentIndex=QModelIndex()):

        if count > 1:
            return False

        if self.hasUninsertedRows():
            return False

        if row < self.sourceModel().rowCount():
            return False

        self.rowsAboutToBeInserted.emit(parentIndex, row, row)

        self._insertedId = str(uuid.uuid1())

        self._buffer[self._insertedId] = {}

        self.rowsInserted.emit(parentIndex, row, row)

        return True

    def submit(self):

        for key in self._buffer:
            if key == self._insertedId:
                continue
            self.submitRow(key)

        if self.hasUninsertedRows():
            self.submitRow(self.sourceModel().rowCount())

        return self.sourceModel().submit()

    def rowCount(self, parentIndex=QModelIndex()):

        sourceCount = self.sourceModel().rowCount(parentIndex)
        val = sourceCount + 1 if self.hasUninsertedRows() else sourceCount
        return val

    def isUninsertedRow(self, row):

        if not self.hasUninsertedRows():
            return False

        return row == self.sourceModel().rowCount()

    def hasUninsertedRows(self):
        return bool(self._insertedId)

    def _emptyBuffer(self, row, bufferIndex=None):

        bufferIndex = row if bufferIndex is None else bufferIndex

        try:

            del self._buffer[bufferIndex]

            self.dirtyStateChanged[int, bool].emit(row, False)

            return True

        except KeyError:
            return False

    def _writeToUninsertedRow(self, index, value):
        self._buffer[self._insertedId][index.column()] = value
        self.dataChanged.emit(index, index)
        self.dirtyStateChanged[int, bool].emit(index.row(), True)
        return True

    def __getitem__(self, row):

        if hasattr(self.sourceModel(), '__getitem__'):
            return self.sourceModel().__getitem__(row)

        data = {}

        for col in range(self.columnCount()):
            index = self.index(row, col)
            colName = py(index.data(ColumnNameRole))

            data[colName] = py(index.data(Qt.EditRole))

        return data