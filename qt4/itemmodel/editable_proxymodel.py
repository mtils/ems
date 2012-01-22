'''
Created on 22.09.2011

@author: michi
'''

from PyQt4.QtCore import QModelIndex, Qt, pyqtSignal
from PyQt4.QtGui import QAbstractProxyModel


class EditableProxyModel(QAbstractProxyModel):
    
    modelReset = pyqtSignal()
    
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
        fromIndexProxy = self.mapFromSource(fromIndex)
        if fromIndexProxy.isValid():
            self.dataChanged.emit(fromIndexProxy,
                                  self.mapFromSource(toIndex))
