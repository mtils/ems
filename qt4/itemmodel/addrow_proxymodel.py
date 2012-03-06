'''
Created on 22.09.2011

@author: michi
'''

from PyQt4.QtCore import QModelIndex, Qt, pyqtSignal, QVariant
from PyQt4.QtGui import QAbstractProxyModel
from ems.qt4.itemmodel.editable_proxymodel import EditableProxyModel
from ems.qt4.util import hassig
from ems.xtype.base import NumberType #@UnresolvedImport


class AddRowProxyModel(EditableProxyModel):
    
    #modelReset = pyqtSignal()
    #layoutChanged = pyqtSignal()
    #headerDataChanged = pyqtSignal(Qt.Orientation, int, int)
    xTypeMapChanged = pyqtSignal(dict)
    
    def __init__(self, parent):
        super(AddRowProxyModel, self).__init__(parent)
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section == 0:
                    return QVariant("Aktion")
                return self.sourceModel().headerData(section-1, orientation, role)
            
        if orientation == Qt.Vertical:
            if role == Qt.DisplayRole:
                if section == self.rowCount() - 1:
                    return QVariant("")
                return self.sourceModel().headerData(section, orientation, role)
            
        return EditableProxyModel.headerData(self, section, orientation, role)
    
    def insertRows(self, row, count, parentIndex=QModelIndex()):
        if row == self.rowCount():
            row = row - 1
        return self.sourceModel().insertRows(row, count, parentIndex)
    
    def removeRows(self, row, count, parentIndex=QModelIndex()):
        return self.sourceModel().removeRows(row, count, parentIndex)
    
    def setSourceModel(self, sourceModel):
        EditableProxyModel.setSourceModel(self, sourceModel)
        if hassig(sourceModel, 'xTypeMapChanged'):
            sourceModel.xTypeMapChanged.connect(self.onXTypeMapChanged)
    
    def xTypeMap(self):
        if hasattr(self.sourceModel(),'xTypeMap'):
            xTypeMap = self.sourceModel().xTypeMap()
            myMap = {0:NumberType(int)}
            for i in xTypeMap:
                print i
                myMap[i+1] = xTypeMap[i]
            return myMap
                    
    
    def onXTypeMapChanged(self, xTypeMap):
        self.xTypeMapChanged.emit(self.xTypeMap())
    
    def index(self, row, column, parentIndex=QModelIndex()):
        return self.createIndex(row, column, parentIndex)
        #return self.sourceModel().index(row, column, parentIndex)
    
    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemIsEnabled
        if index.row() == self.rowCount() - 1:
            return Qt.ItemIsEnabled
        return self.sourceModel().flags(index)
    
    def mapFromSource(self, sourceIndex):
        #if sourceIndex.column() == 0:
        #    return self.createIndex(sourceIndex.row(), 0)
        return self.index(sourceIndex.row(), sourceIndex.column()+1)
    
    def mapToSource(self, proxyIndex):
#        print "mapToSource"
        if not proxyIndex.isValid():
            return QModelIndex()
        
        if proxyIndex.column() == 0:
            return QModelIndex()
            #return self.createIndex(proxyIndex.row(), 0)
        
        return self.sourceModel().index(proxyIndex.row(), proxyIndex.column()-1)
    
    def rowCount(self, parentIndex=QModelIndex()):
        return self.sourceModel().rowCount(parentIndex) + 1
    
    def columnCount(self, parentIndex=QModelIndex()):
        return self.sourceModel().columnCount(parentIndex) + 1
    