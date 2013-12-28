
from PyQt4.QtCore import QModelIndex, Qt, QVariant
from editable_proxymodel import EditableProxyModel

class QmlProxyModel(EditableProxyModel):

    RoleOffset = 1024

    def __init__(self, parent=None):
        super(QmlProxyModel, self).__init__(parent)
        self._mappings = {}

    def mapFromSource(self, sourceIndex):
        if not self.sourceModel():
            return QModelIndex()
        if sourceIndex.parent().isValid():
            return QModelIndex()
        return self.index(sourceIndex.row(), 0)

    def mapToSource(self, proxyIndex):
        if not self.sourceModel():
            return QModelIndex()
        if proxyIndex.parent().isValid():
            return QModelIndex()
        return self.sourceModel().index(proxyIndex.row(), 0)

    def columnCount(self, parentIndex=QModelIndex()):
        if not self.sourceModel():
            return 0
        if parentIndex.isValid():
            return 0
        return 1

    def rowCount(self, parentIndex=QModelIndex()):
        if not self.sourceModel():
            return 0
        if parentIndex.isValid():
            return 0
        return self.sourceModel().rowCount()
    
    def addMapping(self, column, roleName):
        self._mappings[column] = roleName
        self._updateRoleMappings()

    def removeMapping(self, colOrRole):
        if isinstance(colOrRole, int):
            del self._mappings[colOrRole]
        else:
            for key in self._mappings:
                if self._mappings[key] == colOrRole:
                    del self._mappings[key]
                    break

    def _updateRoleMappings(self):
        roleNames = {}
        for col in self._mappings:
            roleNames[QmlProxyModel.RoleOffset+col] = self._mappings[col]
        self.setRoleNames(roleNames)

    def data(self, proxyIndex, role=Qt.DisplayRole):
        if not self.sourceModel():
            return QVariant()
        if role >= QmlProxyModel.RoleOffset:
            return self.sourceModel().data(self._mapWithRole(proxyIndex, role), Qt.DisplayRole)
        return self.sourceModel().data(self.mapToSource(proxyIndex), role)

    def setData(self, index, value, role=Qt.EditRole):
        if not self.sourceModel():
            return False
        if role >= QmlProxyModel.RoleOffset:
            return self.sourceModel().setData(self._mapWithRole(index, role), value, Qt.EditRole)
        return self.sourceModel().setData(self.mapToSource(index), value, role)

    def _mapWithRole(self, index, role):
        if role >= QmlProxyModel.RoleOffset:
            return self.sourceModel().index(index.row(), role-QmlProxyModel.RoleOffset)
        return self.mapToSource(index)
    
    def parent(self, index=QModelIndex()):
        return QModelIndex()
    
    def index(self, row, column, parent=QModelIndex()):
        if not self.sourceModel() or parent.isValid():
            return QModelIndex()
        return self.createIndex(row, column)