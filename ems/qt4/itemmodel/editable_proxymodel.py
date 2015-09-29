'''
Created on 22.09.2011

@author: michi
'''

from PyQt4.QtCore import QModelIndex, Qt, pyqtSignal
from PyQt4.QtGui import QAbstractProxyModel

from ems.qt4.itemmodel.reflectable_mixin import ReflectableMixin #@UnresolvedImport

class EditableProxyModel(QAbstractProxyModel, ReflectableMixin):
    
    #modelReset = pyqtSignal()
    #layoutChanged = pyqtSignal()
    #headerDataChanged = pyqtSignal(Qt.Orientation, int, int)
    
    def __init__(self, parent):
        super(EditableProxyModel, self).__init__(parent)
    
    def index(self, row, column, parentIndex=QModelIndex()):
        return self.createIndex(row, column, parentIndex)
        #return self.sourceModel().index(row, column, parentIndex)
    
    def setSourceModel(self, sourceModel):
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
        return self.sourceModel().flags(index)
    
    def mapFromSource(self, sourceIndex):
        return self.index(sourceIndex.row(), sourceIndex.column())
    
    def mapToSource(self, proxyIndex):
#        print "mapToSource"
        return self.sourceModel().index(proxyIndex.row(), proxyIndex.column())
    
    def rowCount(self, parentIndex=QModelIndex()):
        return self.sourceModel().rowCount(parentIndex)
    
    def columnCount(self, parentIndex=QModelIndex()):
        return self.sourceModel().columnCount(parentIndex)
    
    def setData(self, index, value, role=Qt.EditRole):
        return QAbstractProxyModel.setData(self, index, value, role)
    
    def onDataChanged(self, fromIndex, toIndex):
        self.dataChanged.emit(self.mapFromSource(fromIndex),
                              self.mapFromSource(toIndex))
    
    def columnType(self, column):
        srcColumn = self.mapToSource(self.index(0, column)).column()
        return self.sourceModel().columnType(srcColumn)
    
    def nameOfColumn(self, column):
        srcColumn = self.mapToSource(self.index(0, column)).column()
        return self.sourceModel().nameOfColumn(srcColumn)
    
    def columnOfName(self, name):
        col = self.sourceModel().columnOfName(name)
        return self.mapFromSource(self.index(0, col)).column()
    
    def childModel(self, index):
        srcIndex = self.mapToSource(index)
        return self.sourceModel().childModel(srcIndex)
    
    def getRowAsDict(self, row):
        sourceIndex = self.mapFromSource(self.createIndex(row,0))
        return self.sourceModel().getRowAsDict(sourceIndex.row())
    
    def __getattr__(self, name):
        return self.sourceModel().__getattribute__(name)
