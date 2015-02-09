'''
Created on 22.09.2011

@author: michi
'''

from PyQt4.QtCore import QModelIndex, Qt, pyqtSignal, QVariant, pyqtSlot
from PyQt4.QtGui import QAbstractProxyModel
from ems.qt4.itemmodel.editable_proxymodel import EditableProxyModel
from ems.qt4.util import hassig
from ems.xtype.base import NumberType #@UnresolvedImport
from pprint import pprint



class AddRowProxyModel(EditableProxyModel):
    
    #modelReset = pyqtSignal()
    #layoutChanged = pyqtSignal()
    #headerDataChanged = pyqtSignal(Qt.Orientation, int, int)
    xTypeMapChanged = pyqtSignal(dict)
    rowInsertionRequested = pyqtSignal(int, QModelIndex)
    rowRemovalRequested = pyqtSignal(int, QModelIndex)
    
    ADD = 1
    REMOVE = 2
    
    ACTION_COLUMN_NAME = 'actionAddOrRemove'
    
    def __init__(self, parent, connectModificationSignals=True):
        super(AddRowProxyModel, self).__init__(parent)
        self.pseudoAddType = NumberType(int)
        self.addPixmap = None
        self.removePixmap = None
        if connectModificationSignals:
            self.connectModificationSingals()
    
    def connectModificationSingals(self):
        self.rowInsertionRequested.connect(self.insertRow)
        self.rowRemovalRequested.connect(self.removeRow)
    
    def disconnectModificationSignals(self):
        self.rowInsertionRequested.disconnect(self.insertRow)
        self.rowRemovalRequested.disconnect(self.removeRow)
    
    @pyqtSlot()
    def exportModelData(self, omitEmptyRows=False):
        return self.sourceModel().exportModelData(omitEmptyRows)
    
    def onIndexPressed(self, index):
        if index.column() == 0:
            if index.row() == self.rowCount() - 1:
                self.rowInsertionRequested.emit(index.row(), index.parent())
                #self.insertRow(index.row(), index.parent())
            else:
                self.rowRemovalRequested.emit(index.row(), index.parent())
                #self.removeRow(index.row(), index.parent())
    
    def data(self, index, role=Qt.DisplayRole):
        if index.column() == 0:
            if role == Qt.DecorationRole:
                if self.addPixmap is not None:
                    if index.row() == (self.rowCount() - 1):
                        return QVariant(self.addPixmap)
                if self.removePixmap is not None:
                    if index.row() < (self.rowCount() - 1):
                        return QVariant(self.removePixmap)
            if role == Qt.UserRole:
                if index.row() == (self.rowCount() - 1):
                    return QVariant(self.ADD)
                if index.row() < (self.rowCount() - 1):
                    return QVariant(self.REMOVE)
                
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter | Qt.AlignVCenter
                
        return EditableProxyModel.data(self, index, role)
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section == 0:
                    return QVariant(self.trUtf8("Aktion"))
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
        return self.sourceModel().flags(self.mapToSource(index))
    
    def mapFromSource(self, sourceIndex):
        #if sourceIndex.column() == 0:
        #    return self.createIndex(sourceIndex.row(), 0)
        return self.index(sourceIndex.row(), sourceIndex.column()+1)
    
    def mapToSource(self, proxyIndex):
        if not proxyIndex.isValid():
            return QModelIndex()
        
        if proxyIndex.column() == 0:
            return QModelIndex()
        
        return self.sourceModel().index(proxyIndex.row(), proxyIndex.column()-1)
    
    def rowCount(self, parentIndex=QModelIndex()):
        return self.sourceModel().rowCount(parentIndex) + 1
    
    def columnCount(self, parentIndex=QModelIndex()):
        return self.sourceModel().columnCount(parentIndex) + 1
    
    def columnType(self, column):
        if column == 0:
            return self.pseudoAddType
        return EditableProxyModel.columnType(self, column)
    
    def columnOfName(self, name):
        if name == AddRowProxyModel.ACTION_COLUMN_NAME:
            return 0
        return EditableProxyModel.columnOfName(self, name)
    
    def nameOfColumn(self, column):
        if column == 0:
            return AddRowProxyModel.ACTION_COLUMN_NAME
        return EditableProxyModel.nameOfColumn(self, column)
    