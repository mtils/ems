from copy import copy

from PyQt4.QtCore import QModelIndex, Qt, QVariant
from PyQt4.QtGui import QPixmap
from PyQt4.QtDeclarative import QDeclarativeImageProvider

from ems.registry import Registry
from ems.qt4.util import variant_to_pyobject as py

from editable_proxymodel import EditableProxyModel

class QmlProxyModelImageProvider(QDeclarativeImageProvider):
    def __init__(self, qmlModel):
        self.qmlModel = qmlModel
        QDeclarativeImageProvider.__init__(self, QDeclarativeImageProvider.Pixmap)
        self._prefix = None

    def prefix(self):
        return self._prefix

    def setPrefix(self, prefix):
        if self._prefix != prefix:
            self._prefix = prefix

    def requestPixmap(self, pixmapId, size, requestedSize):
        image = self.qmlModel._getImage(pixmapId)
        if isinstance(image, QPixmap):
            return image
        return QPixmap()


class QmlProxyModel(EditableProxyModel):

    RoleOffset = 1024
    InstanceCount = 0

    def __init__(self, parent=None):
        super(QmlProxyModel, self).__init__(parent)
        self._column2RoleName = {}
        self._role2RoleName = {}
        self._roleSrcColumns = {}
        self._roleMappings = {}
        self._imageProvider = None
        self._imageUpdateCount = 0
        QmlProxyModel.InstanceCount += 1
        self._imageProviderPrefix = 'qmlproxy{0}'.format(QmlProxyModel.InstanceCount)
        self._connectedToSourceModel = False

    def columnMapCount(self):
        return len(self._column2RoleName)

    def columnOfRoleName(self, roleName):
        for col, srcRole in self._column2RoleName.iteritems():
            if srcRole == roleName:
                return col

    def _imageUpdateCounter(self, roleName, row):
        # TODO This should work for more than one image column
        return self._imageUpdateCount

    def imageProvider(self):
        if not self._imageProvider:
            self._imageProvider = self.newImageProvider()
        return self._imageProvider

    def newImageProvider(self):
        return QmlProxyModelImageProvider(self)

    def imageProviderPrefix(self):
        return self._imageProviderPrefix

    def roleOfColumn(self, column):
        return self._column2RoleName[column]

    def roleOfRoleName(self, roleName):
        for role, srcRoleName in self._roleMappings.iteritems():
            if srcRoleName == roleName:
                return role

    def column2RoleNameMap(self):
        return copy(self._column2RoleName)

    def roleMappings(self):
        return copy(self._roleMappings)

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
        if role == Qt.DecorationRole:
            self._connectToSourceModel()
        self._role2RoleName[role] = roleName
        if srcColumn is not None:
            self.setRoleSourceColumn(role, srcColumn)
        self._updateRoleMappings()

    def _connectToSourceModel(self):
        if  self._connectedToSourceModel:
            return
        src = self.sourceModel()
        src.dataChanged.connect(self._onSourceModelDataChanged)
        src.modelAboutToBeReset.connect(self._onSourceModelReset)
        self._connectedToSourceModel = True

    def _onSourceModelDataChanged(self, topLeft, bottomRight):
        if Qt.DecorationRole not in self._roleSrcColumns:
            return False

        imageCol = self._roleSrcColumns[Qt.DecorationRole]

        if imageCol not in range(topLeft.column(), bottomRight.column()+1):
            return

        self._imageUpdateCount += 1
        for row in range(topLeft.row(), bottomRight.row()+1):
            self.dataChanged.emit(self.index(row,0), self.index(row,0))

    def _onSourceModelReset(self):
        self._imageUpdateCount += 1

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

    def _createRoleMappings(self):
        roleNames = {}
        for col in self._column2RoleName:
            roleNames[QmlProxyModel.RoleOffset+col] = self._column2RoleName[col]
        for role in self._role2RoleName:
            roleNames[role] = self._role2RoleName[role]
        return roleNames

    def _updateRoleMappings(self):
        self._roleMappings = self._createRoleMappings()
        self.setRoleNames(self._roleMappings)

    def data(self, proxyIndex, role=Qt.DisplayRole):
        if not self.sourceModel():
            return QVariant()
        if role >= QmlProxyModel.RoleOffset:
            return self.sourceModel().data(self._mapWithRole(proxyIndex, role), Qt.DisplayRole)

        column = 0
        if role in self._roleSrcColumns:
            column = self._roleSrcColumns[role]
            if role == Qt.DecorationRole:
                roleName = self._role2RoleName[role]
                url = "image://{0}/{1}/{2}/{3}".format(self._imageProviderPrefix,
                                                    roleName, proxyIndex.row(),
                                                    self._imageUpdateCounter(roleName,
                                                                                proxyIndex.row()))
                return QVariant(url)

        return self.sourceModel().data(self.mapToSource(proxyIndex, column), role)


    def _getImage(self, pixmapPath):
        roleName,row, updateCounter = str(pixmapPath).split('/')
        row = int(row)
        srcRole = None
        for role in self._role2RoleName:
            if self._role2RoleName[role] == roleName:
                srcRole = role
                break
        if srcRole is None:
            return
        if not srcRole in self._roleSrcColumns:
            print self._roleSrcColumns
            return 
        column = self._roleSrcColumns[srcRole]

        return py(self.sourceModel().index(row, column).data(srcRole))

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