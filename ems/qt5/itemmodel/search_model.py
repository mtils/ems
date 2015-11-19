
from datetime import datetime

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, pyqtSlot, QByteArray
from PyQt5.QtCore import pyqtSignal, QDateTime, QDate, pyqtProperty

from ems.typehint import accepts
from ems.search.base import Search
from ems.qt.identifiers import ItemData, RoleOffset
from ems.resource.repository import Repository

class SearchModel(QAbstractTableModel):

    dirtyStateChanged = pyqtSignal(bool)

    error = pyqtSignal(Exception)

    @accepts(Search, Repository)
    def __init__(self, search, repository=None, namer=None, readOnlyKeys=None, parent=None):

        super().__init__(parent)

        self._search = search
        self._repository = repository
        self._readOnlyKeys = readOnlyKeys if readOnlyKeys is not None else ('id')
        self._namer = namer
        self._query = None
        self._objectCache = []
        self._valueCache = {}
        self._editBuffer = {}
        self._unsubmittedObjectIds = set()
        self._needsRefill = True
        self._isDirty = False
        self._roleNames = None

        # Needs to ne done first, even if no one asks because qml asks rowCount
        # before its ready
        self.refillIfNeeded()

    def data(self, index, role=Qt.DisplayRole):

        self.refillIfNeeded()

        row = index.row()
        column = index.column()

        if role >= RoleOffset:
            column = role - RoleOffset
            #print('Asking for row', row, 'role:', role, 'column:', column)
            role = Qt.DisplayRole

        if not index.isValid() or \
           not (0 <= row < self.rowCount()):
            return None

        if role == ItemData.ColumnNameRole:
            return self._nameOfColumn(column)

        try:
            obj = self._objectCache[row]
        except IndexError:
            return None

        if role == ItemData.RowObjectRole:
            return obj

        if role not in (Qt.DisplayRole, Qt.EditRole):
            return None

        objectId = self._objectId(obj)
        key = self._nameOfColumn(column)

        if self._isInBuffer(objectId, key):
            return self._getFromBuffer(objectId, key)

        try:

            # Cache Entry found
            return self._valueCache[objectId][key]

        # No Cache Entry found
        except KeyError:

            objCache = self._valueCache.setdefault(objectId, {})
            objCache[key] = self._castToQt(self._extractValue(obj, key))

            return objCache[key]

        return None

    def setData(self, index, value, role=Qt.EditRole):

        self.refillIfNeeded()

        row = index.row()
        column = index.column()

        if role >= RoleOffset:
            column = role - RoleOffset
            role = Qt.EditRole

        if role != Qt.EditRole:
            return False

        try:
            obj = self._objectCache[row]
        except IndexError:
            return False

        #value = self._castToPython(value)

        key = self._nameOfColumn(column)
        originalValue = self._extractValue(obj, key)
        objectId = self._objectId(obj)

        if originalValue == value:
            return False

        buffer = self._editBuffer.setdefault(objectId, {})
        buffer[key] = value

        self.dataChanged.emit(index, index)
        self._setDirty(True)

        return True

    def rowCount(self, index=QModelIndex()):
        self.refillIfNeeded()
        return len(self._objectCache)

    def columnCount(self, index=QModelIndex()):
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

        key = self._nameOfColumn(index.column())

        if key in self._readOnlyKeys:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled

        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def refillIfNeeded(self):

        if not self._needsRefill:
            return

        self._needsRefill = False

        self.beginResetModel()

        self._objectCache = []
        self._valueCache.clear()
        self._editBuffer.clear()
        self._unsubmittedObjectIds.clear()


        self._objectCache = [obj for obj in self._getFromSearch()]

        self.endResetModel()
        self.layoutChanged.emit()
        #self.headerDataChanged.emit(Qt.Vertical, 0, self.columnCount())
        self._setDirty(False)

    @pyqtSlot()
    def refill(self):
        self._needsRefill = True
        self.refillIfNeeded()

    @pyqtSlot()
    def submit(self):

        if not self._isDirty:
            return False

        if not self._repository:
            self.error.emit(AttributeError("No repository setted"))
            return False

        createdRows = set()

        for objectId in self._unsubmittedObjectIds:

            data = {}

            if objectId not in self._editBuffer:
                continue

            for key in self._editBuffer[objectId]:
                value = self._castToPython(self._editBuffer[objectId][key])

                if value is None:
                    continue

                data[key] = value

            if not len(data):
                continue

            try:
                self._repository.store(data, self._objectById(objectId))
            except Exception as e:
                print(e)
                self.error.emit(e)
                return False
            createdRows.add(objectId)

        self._unsubmittedObjectIds.clear()

        for objectId in createdRows:
            del self._editBuffer[objectId]

        for objectId in self._editBuffer:

            data = {}

            try:
                obj = self._objectById(objectId)
            except LookupError:
                continue

            for key in self._editBuffer[objectId]:
                data[key] = self._castToPython(self._editBuffer[objectId][key])

            self._repository.update(obj, data)

        self._editBuffer.clear()
        self._valueCache.clear()
        self._setDirty(False)

        return True

    @pyqtSlot()
    def revert(self):
        self.beginResetModel()
        self._editBuffer.clear()
        self._removeUnsubmitted()
        self.endResetModel()

    def insertRows(self, row, count, parent=QModelIndex()):

        self.beginInsertRows(parent, row, row+count-1)

        for i in range(count):
            newObj = self._repository.new()
            self._objectCache.insert(row, newObj)
            self._unsubmittedObjectIds.add(self._objectId(newObj))

        self.endInsertRows()

        return True

    def removeRows(self, row, count, parentIndex=QModelIndex()):

        self.beginRemoveRows(parentIndex, row, row+count-1)

        objects = []

        for i in range(row, row+count):
            objects.append(self._objectCache[i])

        for obj in objects:
            objectId = self._objectId(obj)
            if objectId in self._unsubmittedObjectIds:
                self._objectCache.remove(obj)
                self._unsubmittedObjectIds.remove(objectId)
                continue

            self._repository.delete(obj)
            self._objectCache.remove(obj)

        self.endRemoveRows()
        self._setDirty(True)
        return True

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column, object=0)

    def parent(self, index):
        return QModelIndex()

    def hasChildren(self, parent):
        return False

    def roleNames(self):

        if self._roleNames is not None:
            return self._roleNames

        self._roleNames = {}

        for column in range(self.columnCount()):
            targetRole = RoleOffset + column
            columnName = self._nameOfColumn(column)
            columnName = columnName if columnName != 'id' else 'ID'
            self._roleNames[targetRole] = bytearray(columnName, encoding='ascii')

        return self._roleNames

    @pyqtSlot(int, result='QVariantMap')
    def get(self, row):

        res = {}

        roleNames = self.roleNames()

        for targetRole in roleNames:
            roleName = roleNames[targetRole]
            res[roleName.decode()] = self.index(row, 0).data(targetRole)

        #print(res)
        return res

    @pyqtSlot(int, "QJSValue")
    def set(self, row, jsValue):
        data = jsValue.toVariant()

        roleNames = self.roleNames()

        for key in data:
            try:
                targetRole = [role for role, value in roleNames.items() if value.decode() == key][0]
                self.setData(self.index(row, 0), data[key], targetRole)
            except IndexError:
                pass

        self.submit()

    @pyqtSlot("QJSValue")
    def append(self, jsValue):
        data = jsValue.toVariant()

        roleNames = self.roleNames()

        nextRow = self.rowCount()

        self.insertRows(nextRow, 1)

        for key in data:
            try:
                targetRole = [role for role, value in roleNames.items() if value.decode() == key][0]
                self.setData(self.index(nextRow, 0), data[key], targetRole)
            except IndexError:
                pass

        #self.submit()

    def isDirty(self):
        return self._isDirty

    @pyqtSlot()
    def appendNew(self):
        return self.insertRows(self.rowCount(), 1)


    @pyqtProperty(int)
    def count(self):
        return self.rowCount()

    def _removeUnsubmitted(self):
        for objectId in self._unsubmittedObjectIds:
            self._objectCache.remove(self._objectById(objectId))
        self._unsubmittedObjectIds.clear()

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

    def _isInBuffer(self, objectId, key):
        return (objectId in self._editBuffer and
                key in self._editBuffer[objectId])

    def _getFromBuffer(self, objectId, key):
        return self._editBuffer[objectId][key]

    def _setDirty(self, dirty):
        if self._isDirty == dirty:
            return

        self._isDirty = dirty
        self.dirtyStateChanged.emit(self._isDirty)

    def _objectId(self, obj):
        return id(obj)

    def _objectById(self, objectId):
        for obj in self._objectCache:
            if self._objectId(obj) == objectId:
                return obj
        raise LookupError()

    def _castToPython(self, value):
        if isinstance(value, QDateTime):
            return value.toPyDateTime()
        return value

    def _castToQt(self, value):
        if isinstance(value, datetime):
            return QDateTime.fromString(value.isoformat(), Qt.ISODate)
        return value