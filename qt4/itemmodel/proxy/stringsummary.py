#coding=utf-8
'''
Created on 25.07.2012

@author: michi
'''
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, QVariant, Qt, QString
from PyQt4.QtGui import QAbstractProxyModel
from ems.qt4.util import variant_to_pyobject

class StringSummaryProxyModel(QAbstractProxyModel):
    
    def __init__(self, parent=None):
        QAbstractItemModel.__init__(self, parent)
        self._resultCache = {}
        self._columnName = QVariant('Title')
        self._formatStrings = {
            Qt.DisplayRole:u"{0}",
            Qt.EditRole:u"{0}",
            Qt.ToolTipRole:u"{0}",
            Qt.StatusTipRole:u"{0}"
        }

    def onSourceModelDataChanged(self, topLeft, bottomRight):
        for row in range(topLeft.row(), bottomRight.row()+1):
            try:
                del self._resultCache['{0}-0'.format(row)]
            except KeyError:
                pass
        self.dataChanged.emit(self.index(topLeft.row(),0), self.index(bottomRight.row(), 0))

    def formatString(self, role=Qt.DisplayRole):
        return self._formatStrings[role]

    def setFormatString(self, formatString, role=None):
        if role is None:
            for key in self._formatStrings.keys():
                self._formatStrings[key] = unicode(formatString)
        else:
            self._formatStrings[role] = unicode(formatString)

        self._resultCache.clear()

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self._columnName
            return QVariant()
        #if orientation == Qt.Vertical and role == Qt.DisplayRole:
            #return QVariant("{0}".format(section+1))
        return self.sourceModel().headerData(section, orientation, role)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()

        cacheId = "{0}-{1}".format(index.row(), index.column())

        if role in (Qt.DisplayRole, Qt.EditRole, Qt.ToolTipRole, Qt.StatusTipRole):
            if not self._resultCache.has_key(cacheId):
                self._resultCache[cacheId] = {}
            try:
                return self._resultCache[cacheId][role]
            except KeyError:
                self._resultCache[cacheId][role] = QVariant(self._buildStringOfRow(index.row(), role))
                return self._resultCache[cacheId][role]
            except AttributeError:
                return QVariant()

        return QVariant()

    def _buildStringOfRow(self, row, role):
        rowData = []
        for col in range(self.sourceModel().columnCount()):
            sourceVal = unicode(variant_to_pyobject(self.sourceModel().index(row, col).data()))
            rowData.append(sourceVal)
        return QString.fromUtf8(self._formatStrings[role].format(*rowData))

    def parent(self, *args, **kwargs):
        return QModelIndex()

    def columnCount(self, parentIndex=QModelIndex()):
        return 1

    def rowCount(self, parentIndex=QModelIndex()):
        return self.sourceModel().rowCount(parentIndex)

    def index(self, row, col, parentIndex=QModelIndex()):
        return self.createIndex(row, col, parentIndex)

    def mapToSource(self, proxyIndex):
        return self.sourceModel().createIndex(proxyIndex.row(), proxyIndex.column())

    def mapFromSource(self, sourceIndex):
        return self.createIndex(sourceIndex.row(), sourceIndex.column())

    def reset(self):
        self.beginResetModel()
        self.endResetModel()

    def endResetModel(self):
        self._resultCache.clear()
        QAbstractProxyModel.endResetModel(self)

    def signal2ResetTranslator(self, unused1=None, unused2=None, unused3=None):
        self.reset()

    def setSourceModel(self, srcModel):
        if isinstance(self.sourceModel(), QAbstractItemModel):
            self.sourceModel().disconnect(self.onSourceModelDataChanged)
        srcModel.dataChanged.connect(self.onSourceModelDataChanged)
        srcModel.modelReset.connect(self.reset)
        srcModel.columnsInserted.connect(self.signal2ResetTranslator)
        srcModel.columnsMoved.connect(self.signal2ResetTranslator)
        srcModel.columnsRemoved.connect(self.signal2ResetTranslator)
        srcModel.rowsInserted.connect(self.signal2ResetTranslator)
        srcModel.rowsMoved.connect(self.signal2ResetTranslator)
        srcModel.rowsRemoved.connect(self.signal2ResetTranslator)
        QAbstractProxyModel.setSourceModel(self, srcModel)