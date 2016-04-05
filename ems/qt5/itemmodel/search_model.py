
from datetime import datetime
from decimal import Decimal

from PyQt5.QtCore import Qt, QModelIndex, pyqtSlot, QByteArray
from PyQt5.QtCore import pyqtSignal, QDateTime, QDate, pyqtProperty

from ems.qt5.util import QError
from ems.typehint import accepts
from ems.search.base import Search
from ems.qt.identifiers import ItemData, RoleOffset
from ems.resource.repository import Repository
from ems.qt5.itemmodel.qml_basemodel import QmlTableModel

class SearchModel(QmlTableModel):

    dirtyStateChanged = pyqtSignal(bool)

    error = pyqtSignal(QError, arguments=('error',))

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
        self._isInSubmit = False
        self._isInRefill = False
        self.storeEmptyObjects = False

        # Needs to ne done first, even if no one asks because qml asks rowCount
        # before its ready
        self.refillIfNeeded()

    def data(self, index, role=Qt.DisplayRole):

        row = index.row()
        column = index.column()

        #if self._isInRefill:
            #return None

        self.refillIfNeeded()

        if role >= RoleOffset:
            column = role - RoleOffset
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

        originalRole = int(role)

        if self._isInRefill:
            return False

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
        objectId = self._objectId(obj)

        if self._isInBuffer(objectId, key):
            originalValue = self._getFromBuffer(objectId, key)
        else:
            originalValue = self._extractValue(obj, key)


        # Comparing lists is tricky with a few item types, if one item in the list
        # was changed 
        if originalValue == value and not isinstance(value, list):
            return False

        buffer = self._editBuffer.setdefault(objectId, {})
        buffer[key] = value

        self._setDirty(True)

        # QML creates indexes with column 0. We have to create the right index
        emitIndex = self.createIndex(row, column)
        self.dataChanged.emit(emitIndex, emitIndex)

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

        if role == ItemData.ColumnNameRole:
            return self._nameOfColumn(section)

        if role != Qt.DisplayRole:
            return super().headerData(section, orientation, role)


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

        if not self._needsRefill or self._isInRefill:
            return

        self._isInRefill = True

        self._needsRefill = False

        self.beginResetModel()
        self._setBusy(True)
        self._objectCache = []
        self._valueCache.clear()
        self._editBuffer.clear()
        self._unsubmittedObjectIds.clear()

        self._objectCache = [obj for obj in self._getFromSearch()]

        self.endResetModel()
        self.layoutChanged.emit()
        self._setBusy(False)
        self._setDirty(False)
        self._isInRefill = False

    @pyqtSlot()
    def refill(self):
        self._needsRefill = True
        self.refillIfNeeded()

    @pyqtSlot()
    def submit(self):

        if not self._isDirty or self._isInRefill:
            return False

        if not self._repository:
            self.error.emit(QError(AttributeError("No repository setted")))
            return False

        self._isInSubmit = True

        createdRows = set()

        changedIds = set()

        for objectId in self._unsubmittedObjectIds:

            data = {}

            if not self.storeEmptyObjects and objectId not in self._editBuffer:
                continue

            try:
                for key in self._editBuffer[objectId]:
                    value = self._castToPython(self._editBuffer[objectId][key])

                    if value is None:
                        continue

                    data[key] = value
            except KeyError as e:
                if not self.storeEmptyObjects:
                    self._isInSubmit = False
                    raise e

            if not len(data) and not self.storeEmptyObjects:
                continue

            try:
                self._repository.store(data, self._objectById(objectId))
                changedIds.add(objectId)
            except Exception as e:
                self.error.emit(QError(e))
                self._isInSubmit = False
                return False
            createdRows.add(objectId)

        self._unsubmittedObjectIds.clear()

        for objectId in createdRows:
            try:
                del self._editBuffer[objectId]
            except KeyError:
                pass

        for objectId in self._editBuffer:

            data = {}

            try:
                obj = self._objectById(objectId)
            except LookupError:
                continue

            for key in self._editBuffer[objectId]:
                data[key] = self._castToPython(self._editBuffer[objectId][key])

            self._repository.update(obj, data)
            changedIds.add(objectId)

        self._editBuffer.clear()
        self._valueCache.clear()
        self._setDirty(False)

        self._emitDataChangedForObjectIdsAfterSubmit(changedIds)
        self._isInSubmit = False

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
            insertAt = row + i
            newObj = self._repository.new()
            self._objectCache.insert(insertAt, newObj)
            self._unsubmittedObjectIds.add(self._objectId(newObj))

        self.endInsertRows()

        return True

    def removeRows(self, row, count, parentIndex=QModelIndex()):

        self.beginRemoveRows(parentIndex, row, row+count-1)

        objects = []

        for i in range(row, row+count):
            obj = self._objectCache[i]
            objects.append(obj)


        for obj in objects:
            objectId = self._objectId(obj)

            if objectId in self._unsubmittedObjectIds:

                self._objectCache.remove(obj)
                self._unsubmittedObjectIds.remove(objectId)
                continue

            self._repository.delete(obj)


        for obj in objects:
            try:
                self._objectCache.remove(obj)
            except ValueError:
                pass

        self.endRemoveRows()

        # This method writes live into the repository
        #self._setDirty(True)
        return True

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column, object=0)

    def parent(self, index):
        return QModelIndex()

    def hasChildren(self, parent):
        return False

    def isDirty(self):
        return self._isDirty

    @pyqtSlot()
    def appendNew(self):
        return self.insertRows(self.rowCount(), 1)


    def _removeUnsubmitted(self):
        for objectId in self._unsubmittedObjectIds:
            self._objectCache.remove(self._objectById(objectId))
        self._unsubmittedObjectIds.clear()

    def _getFromSearch(self):
        return self._search.all()

    def _nameOfColumn(self, column):
        return self._search.keys[column]

    def _extractValue(self, currentObj, key):

        key.replace('__', '.')

        if hasattr(currentObj, key):
            return getattr(currentObj, key)
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

    def _rowByObjectId(self, objectId):
        for i, obj in enumerate(self._objectCache):
            if self._objectId(obj) == objectId:
                return i
        raise LookupError()

    def _castToPython(self, value):
        if isinstance(value, QDateTime):
            return value.toPyDateTime()
        return value

    def _castToQt(self, value):
        if isinstance(value, datetime):
            return QDateTime.fromString(value.isoformat(), Qt.ISODate)
        if isinstance(value, Decimal):
            return float(value)
        return value

    def _emitDataChangedForObjectIdsAfterSubmit(self, objectIds):

        lastColumn = self.columnCount()-1

        for objectId in objectIds:

            try:
                row = self._rowByObjectId(objectId)
            except LookupError:
                continue

            topLeft = self.index(row, 0)
            bottomRight = self.index(row, lastColumn)
            self.dataChanged.emit(topLeft, bottomRight)

    def _invalidateValueCaches(self):
        pass
