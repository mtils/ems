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
        self._extractFunction = None
        self._formatStrings = {
            Qt.DisplayRole:u"{0}",
            Qt.EditRole:u"{0}",
            Qt.ToolTipRole:u"{0}",
            Qt.StatusTipRole:u"{0}"
        }
        self._srcColumns = {
            Qt.DisplayRole: (0,),
            Qt.EditRole: (0,),
            Qt.ToolTipRole: (0,),
            Qt.StatusTipRole: (0,)
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

        columns = []
        for key in formatString.split('{'):
            end = key.find('}')
            if end != -1:
                columns.append(int(key[0:end]))

        if role is None:
            for key in self._formatStrings.keys():
                self._formatStrings[key] = unicode(formatString)
                self._srcColumns[key] = columns
        else:
            self._formatStrings[role] = unicode(formatString)
            self._srcColumns[role] = columns

        self._resultCache.clear()

    def flags(self, index):

        #if self._extractFunction is None:
            #return Qt.ItemIsSelectable | Qt.ItemIsEnabled

        lowestFlags = Qt.ItemIsSelectable | Qt.ItemIsEditable | \
                      Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | \
                      Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | \
                      Qt.ItemIsTristate

        for col in self._srcColumns[Qt.DisplayRole]:
            srcIndex = self.sourceModel().index(index.row(), col)
            flags = srcIndex.flags()
            if int(flags) < int(lowestFlags):
                lowestFlags = flags

        if self._extractFunction is None:
            return lowestFlags ^ Qt.ItemIsEditable

        return lowestFlags

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

    def setData(self, index, value, role=Qt.EditRole):
        if not self._extractFunction:
            return False
        res = self._extractFunction(variant_to_pyobject(value))
        if len(res) != len(self._srcColumns[Qt.EditRole]):
            raise TypeError("Result of extractFunction has to have self len() as defined cols")
        i = 0
        for val in res:
            srcCol = self._srcColumns[Qt.EditRole][i]
            srcIndex = self.sourceModel().index(index.row(), srcCol)
            self.sourceModel().setData(srcIndex, QVariant(val))
            i += 1
        return False

    def extractFunction(self):
        return self._extractFunction

    def setExtractFunction(self, function):
        self._extractFunction = function

    def _buildStringOfRow(self, row, role):
        rowData = []
        for col in range(self.sourceModel().columnCount()):
            sourceVal = variant_to_pyobject(self.sourceModel().index(row, col).data())
            if sourceVal is None:
                sourceVal = ''
            rowData.append(sourceVal)
        return QString.fromUtf8(self._formatStrings[role].format(*rowData).strip())

    def parent(self, *args, **kwargs):
        return QModelIndex()

    def columnCount(self, parentIndex=QModelIndex()):
        return 1

    def rowCount(self, parentIndex=QModelIndex()):
        return self.sourceModel().rowCount(parentIndex)

    def index(self, row, col, parentIndex=QModelIndex()):
        return self.createIndex(row, col, parentIndex)

    def mapToSource(self, proxyIndex):
        return QModelIndex()
        return self.sourceModel().createIndex(proxyIndex.row(), proxyIndex.column())

    def mapFromSource(self, sourceIndex):
        for col in self._srcColumns[Qt.DisplayRole]:
            if col == sourceIndex.column():
                return self.index(sourceIndex.row(),0)
        return QModelIndex()
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