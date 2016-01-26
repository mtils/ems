
from PyQt5.QtCore import QModelIndex, Qt, QAbstractProxyModel, pyqtSlot
from PyQt5.QtCore import pyqtProperty, QAbstractItemModel


class FullProxyModel(QAbstractProxyModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._insertQueue = None
        self._removeQueue = None

    def index(self, row, column, parentIndex=QModelIndex()):
        return self.createIndex(row, column, parentIndex)


    def roleNames(self):
        sourceModel = self.sourceModel()
        if sourceModel:
            return sourceModel.roleNames()
        return {}

    def setSourceModel(self, sourceModel):
        self.beginResetModel()
        if not isinstance(sourceModel, QAbstractItemModel):
            raise TypeError("setSourceModel only accepts QAbstractItemModel")

        sourceModel.rowsInserted.connect(self.onSourceModelRowsInserted)
        sourceModel.rowsRemoved.connect(self.onSourceModelRowsDeleted)

        sourceModel.dataChanged.connect(self.onDataChanged)
        sourceModel.modelReset.connect(self.modelReset)
        sourceModel.layoutChanged.connect(self.layoutChanged)
        sourceModel.headerDataChanged.connect(self.headerDataChanged)
        result = super().setSourceModel(sourceModel)
        self.endResetModel()
        return result

    def _onSourceModelRowsAboutToBeInserted(self, parentIndex, start, end):
        self._insertQueue = {
            'parentIndex': parentIndex,
            'start': start,
            'end': end
        }

    def onSourceModelRowsInserted(self, parentIndex, start, end):
        self.beginInsertRows(parentIndex, start, end)
        self.endInsertRows()

    def insertRows(self, row, count, parentIndex=QModelIndex()):
        return self.sourceModel().insertRows(row, count, parentIndex)

    def onSourceModelRowsDeleted(self, parentIndex, start, end):
        self.beginRemoveRows(parentIndex, start, end)
        self.endRemoveRows()

    def removeRows(self, row, count, parentIndex=QModelIndex()):
        return self.sourceModel().removeRows(row, count, parentIndex)

    def parent(self, index):
        return QModelIndex()

    def flags(self, index):
        return self.sourceModel().flags(self.mapToSource(index))

    def mapFromSource(self, sourceIndex):
        return self.index(sourceIndex.row(), sourceIndex.column())

    def mapToSource(self, proxyIndex):
        return self.sourceModel().index(proxyIndex.row(), proxyIndex.column())

    def rowCount(self, parentIndex=QModelIndex()):
        return self.sourceModel().rowCount(parentIndex)

    def columnCount(self, parentIndex=QModelIndex()):
        return self.sourceModel().columnCount(parentIndex)

    def setData(self, index, value, role=Qt.EditRole):
        return super().setData(index, value, role)

    def onDataChanged(self, fromIndex, toIndex):
        self.dataChanged.emit(self.mapFromSource(fromIndex),
                              self.mapFromSource(toIndex))

    @pyqtSlot(int, result='QVariantMap')
    def get(self, row):

        res = {}

        roleNames = self.roleNames()

        for targetRole in roleNames:
            roleName = roleNames[targetRole]
            res[roleName.decode()] = self.index(row, 0).data(targetRole)

        return res

    @pyqtSlot(int, "QJSValue")
    def set(self, row, jsValue):
        data = jsValue.toVariant()

        roleNames = self.roleNames()

        for key in data:
            try:
                targetRole = self._roleOfName(key)
                self.setData(self.index(row, 0), data[key], targetRole)
            except IndexError:
                pass

        self.submit()

    @pyqtSlot(int, 'QString', 'QVariant')
    def setProperty(self, row, roleName, value):
        targetRole = self._roleOfName(roleName)
        self.setData(self.index(row, 0), value, targetRole)

    @pyqtSlot("QJSValue")
    def append(self, jsValue):
        return self.insert(self.rowCount(), jsValue)

    @pyqtSlot(int, "QJSValue")
    def insert(self, row, jsValue):

        data = jsValue if isinstance(jsValue, dict) else jsValue.toVariant()
        roleNames = self.roleNames()

        self.insertRows(row, 1)

        if data is None:
            return

        for key in data:
            try:
                targetRole = self._roleOfName(key)
                self.setData(self.index(row, 0), data[key], targetRole)
            except IndexError:
                pass

    @pyqtSlot(int, int)
    def remove(self, row, count):
        self.removeRows(row, count)

    @pyqtProperty(int)
    def count(self):
        return self.rowCount()

    def _roleOfName(self, name):
        roleNames = self.roleNames()
        try:
            return [role for role, value in roleNames.items() if value.decode() == name][0]
        except IndexError:
            raise KeyError("cannot find roleOfName {0}".format(name))

    def __getattr__(self, name):
        return self.sourceModel().__getattribute__(name)