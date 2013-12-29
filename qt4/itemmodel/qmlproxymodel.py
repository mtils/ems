
from PyQt4.QtCore import QModelIndex, Qt, QVariant
from editable_proxymodel import EditableProxyModel

class QmlProxyModel(EditableProxyModel):

    RoleOffset = 1024

    def __init__(self, parent=None):
        super(QmlProxyModel, self).__init__(parent)
        self._column2RoleName = {}
        self._role2RoleName = {}
        self._roleSrcColumns = {}

    def mapFromSource(self, sourceIndex):
        if not self.sourceModel():
            return QModelIndex()
        if sourceIndex.parent().isValid():
            return QModelIndex()
        return self.index(sourceIndex.row(), 0)

    def mapToSource(self, proxyIndex, column=0):
        if not self.sourceModel():
            return QModelIndex()
        if proxyIndex.parent().isValid():
            return QModelIndex()
        return self.sourceModel().index(proxyIndex.row(), column)

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

    def mapColumnToRoleName(self, column, roleName):
        self._column2RoleName[column] = roleName
        self._updateRoleMappings()

    def unMapColumnToRoleName(self, colOrRole):
        if isinstance(colOrRole, int):
            del self._column2RoleName[colOrRole]
        else:
            for key in self._column2RoleName:
                if self._column2RoleName[key] == colOrRole:
                    del self._column2RoleName[key]
                    break

    def mapRoleToRoleName(self, role, roleName, srcColumn=None):
        self._role2RoleName[role] = roleName
        if srcColumn is not None:
            self.setRoleSourceColumn(role, srcColumn)
        self._updateRoleMappings()

    def unMapRoleToRoleName(self, roleOrRoleName):
        if isinstance(roleOrRoleName, int):
            del self._role2RoleName[roleOrRoleName]
        else:
            for key in self._role2RoleName:
                if self._role2RoleName[key] == roleOrRoleName:
                    del self._role2RoleName[key]
                    break

    def setRoleSourceColumn(self, role, column):
        self._roleSrcColumns[role] = column

    def _updateRoleMappings(self):
        roleNames = {}
        for col in self._column2RoleName:
            roleNames[QmlProxyModel.RoleOffset+col] = self._column2RoleName[col]
        for role in self._role2RoleName:
            roleNames[role] = self._role2RoleName[role]
        self.setRoleNames(roleNames)

    def data(self, proxyIndex, role=Qt.DisplayRole):
        if not self.sourceModel():
            return QVariant()
        if role >= QmlProxyModel.RoleOffset:
            return self.sourceModel().data(self._mapWithRole(proxyIndex, role), Qt.DisplayRole)

        column = 0
        if role in self._roleSrcColumns:
            column = self._roleSrcColumns[role]

        return self.sourceModel().data(self.mapToSource(proxyIndex, column), role)

    def setData(self, index, value, role=Qt.EditRole):
        if not self.sourceModel():
            return False
        if role >= QmlProxyModel.RoleOffset:
            return self.sourceModel().setData(self._mapWithRole(index, role), value, Qt.EditRole)

        column = 0
        if role in self._roleSrcColumns:
            column = self._roleSrcColumns[role]
        return self.sourceModel().setData(self.mapToSource(index, column), value, role)

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