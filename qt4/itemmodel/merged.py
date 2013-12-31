'''
Created on 01.08.2011

@author: michi
'''

from PyQt4.QtCore import QModelIndex, Qt, pyqtSignal, QObject, QVariant
from PyQt4.QtGui import QAbstractProxyModel

from ems.qt4.itemmodel.reflectable_mixin import ReflectableMixin #@UnresolvedImport
from ems.qt4.util import variant_to_pyobject

class SignalTranslator(QObject):
    
    dataChangedWithId = pyqtSignal(int, QModelIndex, QModelIndex)
    modelResetWithId = pyqtSignal(int)
    rowsInsertedWithId = pyqtSignal(int, QModelIndex, int, int)
    rowsRemovedWithId = pyqtSignal(int, QModelIndex, int, int)
    columnsInsertedWithId = pyqtSignal(int, QModelIndex, int, int)
    columnsRemovedWithId = pyqtSignal(int, QModelIndex, int, int)
    headerDataChangedWithId = pyqtSignal(int, int, int, int)
    
    def __init__(self, modelId, sourceModel, parent=None):
        QObject.__init__(self, parent)
        self.sourceModel = sourceModel
        self.modelId = modelId
        self.sourceModel.dataChanged.connect(self.onDataChanged)
        self.sourceModel.modelReset.connect(self.onModelReset)
        self.sourceModel.rowsInserted.connect(self.onRowsInserted)
        self.sourceModel.rowsRemoved.connect(self.onRowsRemoved)
        self.sourceModel.columnsInserted.connect(self.onColumnsInserted)
        self.sourceModel.columnsRemoved.connect(self.onColumnsRemoved)
        self.sourceModel.headerDataChanged.connect(self.onHeaderDataChanged)
    
    def onDataChanged(self, topLeft, bottomRight):
        self.dataChangedWithId.emit(self.modelId, topLeft, bottomRight)
    
    def onModelReset(self):
        self.modelResetWithId.emit(self.modelId)
    
    def onRowsInserted(self, index, start, end):
        self.rowsInsertedWithId.emit(self.modelId, index, start, end)
    
    def onRowsRemoved(self, index, start, end):
        self.rowsRemovedWithId.emit(self.modelId, index, start, end)
    
    def onColumnsInserted(self, index, start, end):
        self.columnsInsertedWithId.emit(self.modelId, index, start, end)
    
    def onColumnsRemoved(self, index, start, end):
        self.columnsRemovedWithId.emit(self.modelId, index, start, end)
    
    def onHeaderDataChanged(self, orientation, first, last):
        self.headerDataChangedWithId.emit(self.modelId, orientation, first, last)
        
        

class MergedProxyModel(QAbstractProxyModel, ReflectableMixin):
    
    #modelReset = pyqtSignal()
    #layoutChanged = pyqtSignal()
    #headerDataChanged = pyqtSignal(Qt.Orientation, int, int)
    
    def __init__(self, parent):
        super(MergedProxyModel, self).__init__(parent)
        self._sourceModels = {}
        self._sourceModelKeys = []
        self._signalEmitters = {}
    
    def index(self, row, column, parentIndex=QModelIndex()):
        proxyIndex = self.createIndex(row, column, parentIndex)
        return proxyIndex
        #return self.sourceModel().index(row, column, parentIndex)
    
    def createIndex(self, row, column, parentIndex=QModelIndex()):
        proxyIndex = QAbstractProxyModel.createIndex(self, row, column, parentIndex)
        proxyIndex.modelId = self.getModelIdOfProxyColumn(column)
        return proxyIndex
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            modelId = self.getModelIdOfProxyColumn(section)
            sourceSection = self.getSourceModelColumn(modelId, section)
            return self._sourceModels[modelId].headerData(sourceSection,
                                                          orientation,
                                                          role)
        return QAbstractProxyModel.headerData(self, section, orientation, role)
    
    def getModelIdOfSourceColumn(self, col):
        pass
    
    def getModelIdOfProxyColumn_(self, col):
        foundedCols = 0 
        lastModelId = self._sourceModelKeys[0]
        for modelId in self._sourceModelKeys:
            #print "modelId", modelId, 'has', self._sourceModels[modelId].columnCount(), 'cols'
            foundedCols += self._sourceModels[modelId].columnCount()
            if foundedCols > col:
                return lastModelId
            lastModelId = modelId
        if foundedCols > col:
            return lastModelId
        return -1
    
    def getModelIdOfProxyColumn(self, proxyCol):
        col = 0 
        for modelIdKey in self._sourceModelKeys:
            for sCol in range(self._sourceModels[modelIdKey].columnCount()):
                if col == proxyCol:
                    return modelIdKey
                col += 1
                    
        
        return -1
    def getProxyModelColumn(self, modelId, sourceCol):
        col = 0 
        for modelIdKey in self._sourceModelKeys:
            for sCol in range(self._sourceModels[modelIdKey].columnCount()):
                if (modelIdKey == modelId) and (sCol == sourceCol):
                    return col
                col += 1
                    
        
        return -1
    
    def getSourceModelColumn(self, modelId, proxyCol):
        col = 0 
        for modelIdKey in self._sourceModelKeys:
            for sCol in range(self._sourceModels[modelIdKey].columnCount()):
                if (modelIdKey == modelId) and (col == proxyCol):
                    return sCol
                col += 1
                    
        
        return -1
            
    
    def addSourceModel(self, sourceModel):
        modelId = hash(sourceModel)
        self._signalEmitters[modelId] = SignalTranslator(modelId, sourceModel,
                                                         self)
        self._signalEmitters[modelId].dataChangedWithId.connect(self.onDataChanged)
        self._signalEmitters[modelId].modelResetWithId.connect(self.onModelReset)
        self._signalEmitters[modelId].rowsInsertedWithId.connect(self.onRowsInserted)
        self._signalEmitters[modelId].rowsRemovedWithId.connect(self.onRowsRemoved)
        self._signalEmitters[modelId].columnsInsertedWithId.connect(self.onColumnsInserted)
        self._signalEmitters[modelId].columnsRemovedWithId.connect(self.onColumnsRemoved)
        self._signalEmitters[modelId].headerDataChangedWithId.connect(self.onHeaderDataChanged)
        
        self._sourceModels[modelId] = sourceModel
        self._sourceModelKeys.append(modelId)
    
    def onDataChanged(self, modelId, topLeft, bottomRight):
        self.dataChanged.emit(self.mapFromSource(topLeft), self.mapFromSource(bottomRight))
    
    def onModelReset(self, modelId):
        self.modelReset.emit()
    
    def onRowsInserted(self, modelId, index, start, end):
        self.rowsInserted.emit(index, start, end)
    
    def onRowsRemoved(self, modelId, index, start, end):
        self.rowsRemovedWithId.emit(self.modelId, index, start, end)
    
    def onColumnsInserted(self, modelId, index, start, end):
        self.columnsInsertedWithId.emit(self.modelId, index, start, end)
    
    def onColumnsRemoved(self, modelId, index, start, end):
        self.columnsRemovedWithId.emit(self.modelId, index, start, end)
    
    def onHeaderDataChanged(self, modelId, orientation, first, last):
        self.headerDataChangedWithId.emit(self.modelId, orientation, first, last)
    
    def setSourceModel(self, sourceModel):
        raise TypeError("Please use addSourceModel")
        sourceModel.rowsAboutToBeInserted.connect(self.onSourceModelRowsInserted)
        sourceModel.rowsAboutToBeRemoved.connect(self.onSourceModelRowsDeleted)
        sourceModel.dataChanged.connect(self.onDataChanged)
        sourceModel.modelReset.connect(self.modelReset)
        sourceModel.layoutChanged.connect(self.layoutChanged)
        sourceModel.headerDataChanged.connect(self.headerDataChanged)
        return QAbstractProxyModel.setSourceModel(self, sourceModel)
    
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
        modelId = self.getModelIdOfProxyColumn(index.column())
        #sourceIndex = self.mapToSource(index)
        #print "flags", modelId, sourceIndex.row(), sourceIndex.column()
        return self._sourceModels[modelId].flags(self.mapToSource(index))
    
    def mapFromSource(self, sourceIndex):
        if not sourceIndex.isValid():
            return QModelIndex()
        #modelId = self.getModelIdOfProxyColumn(sourceIndex.column())
        modelId = hash(sourceIndex.model())
        proxyModelColumn = self.getProxyModelColumn(modelId, sourceIndex.column())
        
#        print "mapFromSource: Column", sourceIndex.column(), 'is', proxyModelColumn
        return self.index(sourceIndex.row(), proxyModelColumn)
    
    def mapToSource(self, proxyIndex):
        if not proxyIndex.isValid():
            return QModelIndex()

        modelId = self.getModelIdOfProxyColumn(proxyIndex.column())
        sourceModelColumn = self.getSourceModelColumn(modelId, proxyIndex.column())

        return self._sourceModels[modelId].index(proxyIndex.row(), sourceModelColumn)

    def rowCount(self, parentIndex=QModelIndex()):
        rows = 1000000
        for modelId in self._sourceModelKeys:
            rows = min(self._sourceModels[modelId].rowCount(), rows)
        return rows
    
    def columnCount(self, parentIndex=QModelIndex()):
        cols = 0
        for modelId in self._sourceModelKeys:
            cols += self._sourceModels[modelId].columnCount()
        return cols
    
    def data(self, index, role=Qt.DisplayRole):
        #data = QAbstractProxyModel.data(self, index, role)
        #index = self.mapToSource(index)
        #print "data role:",role
        #print "data:", variant_to_pyobject(index.data())
        return self.mapToSource(index).data(role)
    
    def setData(self, index, value, role=Qt.EditRole):
        return QAbstractProxyModel.setData(self, index, value, role)
    
    def columnType(self, column):
        modelId = self.getModelIdOfProxyColumn(column)
        srcColumn = self.getSourceModelColumn(modelId, column)
        return self._sourceModels[modelId].columnType(srcColumn)

    def _getColumnOffsetOfModel(self, modelId):
        columns = 0
        for modelIdKey in self._sourceModelKeys:
            if modelIdKey == modelId:
                return columns
            columns += self._sourceModels[modelIdKey].columnCount()
        return columns

    def nameOfColumn(self, column):
        modelId = self.getModelIdOfProxyColumn(column)
        srcColumn = self.getSourceModelColumn(modelId, column)
        return self._sourceModels[modelId].nameOfColumn(srcColumn)
    
    def columnsOfName(self, name):
        columns = []
        for modelId in self._sourceModelKeys:
            try:
                cols = self._sourceModels[modelId].columnOfName(name)
                if cols != -1:
                    columns.append(cols + self._getColumnOffsetOfModel(modelId))
            except Exception:
                continue
        return columns

    def columnOfName(self, name):
        columns = self.columnsOfName(name)
        if len(columns):
            return columns[0]
        return -1

    def childModel(self, index):
        modelId = self.getModelIdOfProxyColumn(index.column())
        srcColumn = self.getSourceModelColumn(modelId, index.column())
        return self._sourceModels[modelId].childModel(srcColumn)    

class MergedRowsProxyModel(MergedProxyModel):

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            modelId = self.getModelIdOfProxyRow(section)
            sourceSection = self.getSourceModelRow(modelId, section)
            original = self._sourceModels[modelId].headerData(sourceSection,
                                                              orientation,
                                                              role)
            rowNum = variant_to_pyobject(original)
            if isinstance(rowNum, int):
                return QVariant(rowNum+self._getRowOffsetOfModel(modelId))
            return original
        return QAbstractProxyModel.headerData(self, section, orientation, role)

    def rowCount(self, parentIndex=QModelIndex()):
        rows = 0
        for modelId in self._sourceModelKeys:
            rows += self._sourceModels[modelId].rowCount()
        return rows

    def columnCount(self, parentIndex=QModelIndex()):
        cols = 1000000
        for modelId in self._sourceModelKeys:
            cols = min(self._sourceModels[modelId].columnCount(), cols)
        return cols

    def getProxyModelRow(self, modelId, sourceRow):
        row = 0 
        for modelIdKey in self._sourceModelKeys:
            for sCol in range(self._sourceModels[modelIdKey].rowCount()):
                if (modelIdKey == modelId) and (sCol == sourceRow):
                    return row
                row += 1

        return -1

    def getModelIdOfProxyRow(self, proxyRow):
        row = 0
        for modelIdKey in self._sourceModelKeys:
            for sRow in range(self._sourceModels[modelIdKey].rowCount()):
                if row == proxyRow:
                    return modelIdKey
                row += 1

        return -1

    def getSourceModelRow(self, modelId, proxyRow):
        row = 0 
        for modelIdKey in self._sourceModelKeys:
            for sRow in range(self._sourceModels[modelIdKey].rowCount()):
                if (modelIdKey == modelId) and (row == proxyRow):
                    return sRow
                row += 1

        return -1

    def mapToSource(self, proxyIndex):
        if not proxyIndex.isValid():
            return QModelIndex()

        modelId = self.getModelIdOfProxyRow(proxyIndex.row())
        sourceModelRow = self.getSourceModelRow(modelId, proxyIndex.row())

        return self._sourceModels[modelId].index(sourceModelRow, proxyIndex.column())

    def mapFromSource(self, sourceIndex):
        if not sourceIndex.isValid() or sourceIndex.column() > self.columnCount():
            return QModelIndex()
        modelId = hash(sourceIndex.model())
        proxyModelRow = self.getProxyModelRow(modelId, sourceIndex.column())
        return self.index(proxyModelRow, sourceIndex.column())
    
    def flags(self, index):
        modelId = self.getModelIdOfProxyRow(index.row())
        #sourceIndex = self.mapToSource(index)
        #print "flags", modelId, sourceIndex.row(), sourceIndex.column()
        return self._sourceModels[modelId].flags(self.mapToSource(index))

    def _getRowOffsetOfModel(self, modelId):
        rows = 0
        for modelIdKey in self._sourceModelKeys:
            if modelIdKey == modelId:
                return rows
            rows += self._sourceModels[modelIdKey].rowCount()
        return rows

    def rowOfName(self, name):
        rows = self.rowsOfName(name)
        if not len(rows):
            return -1
        return rows[0]
    
    def rowsOfName(self, name):
        rows = []
        for modelId in self._sourceModelKeys:
            try:
                row = self._sourceModels[modelId].rowOfName(name)
                if row != -1:
                    rows.append(row + self._getRowOffsetOfModel(modelId))
            except Exception:
                continue
        return rows
