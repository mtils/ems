
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, pyqtSlot
from PyQt5.QtCore import pyqtSignal

from ems.typehint import accepts
from ems.search.base import Search
from ems.qt.identifiers import ItemData
from ems.resource.repository import Repository

class SearchModel(QAbstractTableModel):

    dirtyStateChanged = pyqtSignal(bool)

    @accepts(Search, Repository)
    def __init__(self, search, repository=None, namer=None, parent=None):

        self._search = search
        self._repository = repository
        self._namer = namer
        self._query = None
        self._objectCache = []
        self._rowColumnCache = {}
        self._editBuffer = {}
        self._unsubmittedRows = set()
        self._needsRefill = True
        self._isDirty = False
        super().__init__(parent)

    def data(self, index, role=Qt.DisplayRole):

        self.refillIfNeeded()

        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return None

        if role in (Qt.DisplayRole, Qt.EditRole):

            if self._isInBuffer(index):
                return self._getFromBuffer(index)

            # Object found
            try:
                obj = self._objectCache[index.row()]

                # Cache Entry found
                try:
                    return self._rowColumnCache[index.row()][index.column()]

                # No Cache Entry found
                except KeyError:
                    columnName = self._nameOfColumn(index.column())
                    value = self._extractValue(obj, columnName)
                    try:
                        self._rowColumnCache[index.row()][index.column()] = value
                    except KeyError:
                        self._rowColumnCache[index.row()] = {index.column():value}
                    return self._rowColumnCache[index.row()][index.column()]

            # No Object found
            except IndexError:
                return None

        if role == ItemData.ColumnNameRole:
            return self._nameOfColumn(index.column())
        if role == ItemData.RowObjectRole:
            return self.getObject(index.row())

        return None

    def setData(self, index, value, role=Qt.EditRole):

        if role != Qt.EditRole:
            return False

        self.refillIfNeeded()

        try: 
            obj = self._objectCache[index.row()]
            columnName = self._nameOfColumn(index.column())
            originalValue = self._extractValue(obj, columnName)
            if originalValue == value:
                return False
        except IndexError:
            pass

        buffer = self._editBuffer.setdefault(index.row(), {})
        buffer[index.column()] = value

        self._setDirty(True)

        return True

    def rowCount(self, index=QModelIndex()):
        self.refillIfNeeded()
        return len(self._objectCache) + len(self._unsubmittedRows)

    def columnCount(self, index=QModelIndex()):
        self.refillIfNeeded()
        return len(self._search.keys)

    def headerData(self, section, orientation, role=Qt.DisplayRole):

        if orientation == Qt.Vertical:
            return super().headerData(section, orientation, role)

        #if role == Qt.TextAlignmentRole:
            #return int(Qt.AlignLeft|Qt.AlignVCenter)

        if role != Qt.DisplayRole:
            return super().headerData(section, orientation, role)

        if role == ItemData.ColumnNameRole:
            return self._nameOfColumn(section)

        if role != Qt.DisplayRole:
            return None

        colName = self._nameOfColumn(section)

        if not self._namer:
            return colName

        return self._namer.columnName(self._search.modelClass, colName)

        if self.sectionFriendlyNames.has_key(section):
            return self.sectionFriendlyNames[section]
        columnName = unicode(self.nameOfColumn(section))
        name = self.getPropertyFriendlyName(columnName)

        return name

    def flags(self, index):

        if not self._repository:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled

        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

        if index.column() not in self._flagsCache:
            propertyName = self.nameOfColumn(index.column())
            if self._queryBuilder.isAutoProperty(propertyName):
                flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
            else:
                flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
            self._flagsCache[index.column()] = flags
        return self._flagsCache[index.column()]

    def refillIfNeeded(self):

        if not self._needsRefill:
            return

        self._needsRefill = False

        self.beginResetModel()

        self._objectCache = []
        self._rowColumnCache.clear()
        self._editBuffer.clear()
        self._unsubmittedRows = set()

        for i, obj in enumerate(self._getFromSearch()):
            self._objectCache.append(obj)
            self._rowColumnCache[i] = {}

        self.endResetModel()
        self.layoutChanged.emit()
        self.headerDataChanged.emit(Qt.Vertical, 0, self.rowCount(QModelIndex()))
        self._setDirty(False)

    @pyqtSlot()
    def refill(self):
        self._needsRefill = True
        self.refillIfNeeded()

    @pyqtSlot()
    def submit(self):

        if not self._isDirty:
            return False

        createdRows = set()

        for row in self._unsubmittedRows:
            data = {}
            for col in self._editBuffer[row]:
                value = self._editBuffer[row][col]
                if value is None:
                    continue

                colName = self._nameOfColumn(col)
                data[colName] = self._editBuffer[row][col]

            if not len(data):
                continue

            self._objectCache.append(self._repository.store(data))
            createdRows.add(row)

        for row in createdRows:
            del self._editBuffer[row]

        for row in self._editBuffer:

            data = {}

            try:
                obj = self._objectCache[row]
            except IndexError:
                continue

            for col in self._editBuffer[row]:
                colName = self._nameOfColumn(col)
                data[colName] = self._editBuffer[row][col]

            self._repository.update(obj, data)

        self._setDirty(False)

        return True

    @pyqtSlot()
    def revert(self):
        self.beginResetModel()
        self._editBuffer.clear()
        self._unsubmittedRows.clear()
        self.endResetModel()
        return True

    def insertRows(self, row, count, parent=QModelIndex()):

        if count > 1:
            raise NotImplementedError("Currently only one row can be inserted")

        rowCount = self.rowCount(parent)

        if row != rowCount:
            raise NotImplementedError("Currently the row can be inserted at the end")

        newObj = self._repository.new()

        rowData = {}
        for i in range(self.columnCount()):
            columnName = self._nameOfColumn(i)
            rowData[i] = getattr(newObj, columnName)

        self.beginInsertRows(parent, row, row)
        self._editBuffer[row] = rowData
        self._unsubmittedRows.add(row)
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parentIndex=QModelIndex()):

        if count > 1:
            raise NotImplementedError("Currently only one row can be removed")

        self.beginRemoveRows(parentIndex, row, row)

        if row in self._unsubmittedRows:
            self._unsubmittedRows.remove(row)
            del self._editBuffer[row]
            self._resultCache.clear()
            return True

        try:
            obj = self._objectCache[row]
        except IndexError:
            return False

        del self._objectCache[row]

        if row in self._unsubmittedRows:
            self._unsubmittedRows.remove(row)
        else:
            self._deletedObjects.append(obj)

        self._resultCache.clear()

        self.endRemoveRows()
        self._setDirty(True)
        return True

    def isDirty(self):
        return self._isDirty

    @pyqtSlot()
    def appendNew(self):
        return self.insertRows(self.rowCount(), 1)

    def _getFromSearch(self):
        return self._search.all()

    def _nameOfColumn(self, column):
        return self._search.keys[column]

    def _extractValue(self, currentObj, key):

        if hasattr(currentObj, key):
            return currentObj.__getattribute__(key)

        elif key.find('.'):
            stack = key.split('.')
            value = self._extractValueRecursive(currentObj, stack)
            if value is not None:
                return value

        return None

    def _extractValueRecursive(self, obj, pathStack):

        if not hasattr(obj, pathStack[0]):
            return

        if len(pathStack) < 2:
            return obj.__getattribute__(pathStack[0])

        nextObj = obj.__getattribute__(pathStack[0])
        pathStack.pop(0)
        return self._extractValueRecursive(nextObj, pathStack)

    def _isInBuffer(self, index):
        return (index.row() in self._editBuffer and
                index.column() in self._editBuffer[index.row()])

    def _getFromBuffer(self, index):
        return self._editBuffer[index.row()][index.column()]

    def _setDirty(self, dirty):
        if self._isDirty == dirty:
            return

        self._isDirty = dirty
        self.dirtyStateChanged.emit(self._isDirty)

    def _objectId(self, obj):
        return id(obj)