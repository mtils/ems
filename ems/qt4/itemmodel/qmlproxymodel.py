from copy import copy

from PyQt4.QtCore import QModelIndex, Qt, QVariant, pyqtSlot, QString, QObject
from PyQt4.QtCore import pyqtProperty, QSize, pyqtSignal
from PyQt4.QtGui import QPixmap, QIcon
from PyQt4.QtDeclarative import QDeclarativeImageProvider

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
        if isinstance(image, QIcon):
            size = size if size.isValid() else image.availableSizes()[0]
            return image.pixmap(size)
        return QPixmap()


class QmlProxyModel(EditableProxyModel):

    RoleOffset = 1024
    InstanceCount = 0

    countChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super(QmlProxyModel, self).__init__(parent)
        self._roleSrcColumns = {}
        self._roleMappings = {}
        self._mappings = {}
        self._mapCount = QmlProxyModel.RoleOffset
        self._imageProvider = None
        self._imageUpdateCount = 0
        self.__lastEmittedCount = -1
        QmlProxyModel.InstanceCount += 1
        self._imageProviderPrefix = 'qmlproxy{0}'.format(QmlProxyModel.InstanceCount)
        self._connectedToSourceModel = False
        self.defaultSrcRole=Qt.DisplayRole

    def columnMapCount(self):
        return len(self._mappings)

    def columnOfRoleName(self, roleName):
        for targetRole in self._mappings:
            if self._mappings[targetRole]['roleName'] == roleName:
                return self._mappings[targetRole]['column']

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
        for targetRole in self._mappings:
            if self._mappings[targetRole]['column'] == column:
                return self._mappings[targetRole]['roleName']

    def roleOfRoleName(self, roleName):
        for targetRole in self._mappings:
            if self._mappings[targetRole]['roleName'] == roleName:
                return targetRole

    def column2RoleNameMap(self):
        colRoleMap = {}
        for targetRole in self._mappings:
            colRoleMap[self._mappings[targetRole]['column']] = self._mappings[targetRole]['roleName']

        return colRoleMap

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

    @pyqtProperty(int, notify=countChanged)
    def count(self):
        return self.rowCount()

    def mapColumnToRoleName(self, column, roleName, srcRole=None):

        srcRole = self.defaultSrcRole if srcRole is None else srcRole

        targetRole = self._nextMappingId()

        self._mappings[targetRole] = {
            'column': column,
            'sourceRole': srcRole,
            'targetRole': targetRole,
            'roleName': roleName
        }

        if srcRole == Qt.DecorationRole:
            self._connectToSourceModel()
            self._roleSrcColumns[srcRole] = column

        self._updateRoleMappings()

        self._mapCount += 1

    def mapRoleToRoleName(self, role, roleName, srcColumn=None):
        srcColumn = 0 if srcColumn is None else srcColumn
        return self.mapColumnToRoleName(srcColumn, roleName, role)

    def _connectToSourceModel(self):
        if  self._connectedToSourceModel:
            return
        src = self.sourceModel()
        src.dataChanged.connect(self._onSourceModelDataChanged)
        src.modelAboutToBeReset.connect(self._onSourceModelReset)

        src.layoutChanged.connect(self._emitCount)
        src.modelReset.connect(self._emitCount)
        src.rowsInserted.connect(self._emitCount)
        src.rowsRemoved.connect(self._emitCount)

        self._connectedToSourceModel = True

    def _onSourceModelDataChanged(self, topLeft, bottomRight):

        if Qt.DecorationRole not in self._roleSrcColumns:
            return False

        imageCol = self._roleSrcColumns[Qt.DecorationRole]

        # I got some bottomRight.column() values from QSortFilterProxyModel
        # Sometimes the values are below zero, sometimes they are the max
        # integer on the system.
        # The sourceModel of it didnt emit these values. But the changed
        # behaviour here should fix the Memory Error caused by
        # bottomRight.row()+1
        if not topLeft.isValid() or not bottomRight.isValid():
            return

        if imageCol < topLeft.column() or imageCol > bottomRight.column():
            return

        self._imageUpdateCount += 1
        for row in range(topLeft.row(), bottomRight.row()+1):
            self.dataChanged.emit(self.index(row,0), self.index(row,0))

    def _onSourceModelReset(self):
        self._imageUpdateCount += 1

    def _createRoleMappings(self):

        roleNames = {}

        for targetRole in self._mappings:
            roleNames[targetRole] = self._mappings[targetRole]['roleName']

        return roleNames

    def _updateRoleMappings(self):
        self._roleMappings = self._createRoleMappings()
        self.setRoleNames(self._roleMappings)


    def _emitCount(self, *args):
        count = self.rowCount()
        if count == self.__lastEmittedCount:
            return
        self.countChanged.emit(count)
        self.__lastEmittedCount = count

    def data(self, proxyIndex, role=Qt.DisplayRole):

        if not self.sourceModel():
            return QVariant()

        if role < QmlProxyModel.RoleOffset:
            return self.sourceModel().data(self.mapToSource(proxyIndex), role)

        srcRole = self._mappings[role]['sourceRole']

        if srcRole != Qt.DecorationRole:
            return self.sourceModel().data(self._mapWithRole(proxyIndex, role), srcRole)


        roleName = self._mappings[role]['roleName']

        url = self._imageUrl(roleName, proxyIndex.row())

        return QVariant(url)

    def _getImage(self, pixmapPath):

        #if self.sourceModel().__class__.__name__ == 'AvailableHeizungenModel':
            #print "_getImage", pixmapPath

        roleName, row, updateCounter = str(pixmapPath).split('/')
        row = int(row)

        for targetRole in self._mappings:
            if self._mappings[targetRole]['roleName'] == roleName:
                column = self._mappings[targetRole]['column']
                srcRole = self._mappings[targetRole]['sourceRole']
                break

        return py(self.sourceModel().index(row, column).data(srcRole))

    def setData(self, index, value, role=Qt.EditRole):

        if not self.sourceModel():
            return False

        if role < QmlProxyModel.RoleOffset:
            return self.sourceModel().setData(self.mapToSource(index), value, role)

        srcRole = self._mappings[role]['sourceRole']

        return self.sourceModel().setData(self._mapWithRole(index, role), value, srcRole)

        column = 0
        if role in self._roleSrcColumns:
            column = self._roleSrcColumns[role]
        return self.sourceModel().setData(self.mapToSource(index, column), value, role)

    def _mapWithRole(self, index, role):
        if role >= QmlProxyModel.RoleOffset:
            return self.sourceModel().index(index.row(), self._mappings[role]['column'])
        return self.mapToSource(index)

    def _imageUrl(self, roleName, row, column=0):
        return "image://{0}/{1}/{2}/{3}".format(self._imageProviderPrefix,
                                                roleName,
                                                row,
                                                self._imageUpdateCounter(roleName, row))

    def parent(self, index=QModelIndex()):
        return QModelIndex()

    def index(self, row, column, parent=QModelIndex()):
        if not self.sourceModel() or parent.isValid():
            return QModelIndex()
        return self.createIndex(row, column)

    @pyqtSlot(int, result='QVariantMap')
    def get(self, row):

        res = {}

        src = self.sourceModel()

        for targetRole in self._mappings:
            roleName = self._mappings[targetRole]['roleName']
            col = self._mappings[targetRole]['column']
            srcRole = self._mappings[targetRole]['sourceRole']
            if srcRole == Qt.DecorationRole:
                res[roleName] = self._imageUrl(roleName, row)
            else:
                res[roleName] = src.index(row, col).data(srcRole)

        return res

    @pyqtSlot(int, QString, QVariant)
    def setProperty(self, row, roleName, value):
        col = self.columnOfRoleName(roleName)
        self.sourceModel().setData(self.sourceModel().index(row, col), value, Qt.EditRole)

    def _nextMappingId(self):
        return QmlProxyModel.RoleOffset + self._mapCount