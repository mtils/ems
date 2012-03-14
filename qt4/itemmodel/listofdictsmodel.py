'''
Created on 04.03.2012

@author: michi
'''
from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant, \
    pyqtSignal, pyqtSlot
from PyQt4.QtGui import QColor

from ems import qt4
from ems.qt4.util import variant_to_pyobject
from ems.xtype.base import XType #@UnresolvedImport
#from pprint import pprint

class ListOfDictsModel(QAbstractTableModel):
    
    xTypeMapChanged = pyqtSignal(dict)
    
    def __init__(self, xType, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.__modelData = []
        self.__xType = xType
        self.__keyLabels = {}
        self.isEditable = True
        self._standardRow = None
        self.standardRowBackground = '#00E3F3'
        self.hHeaderAlignment = Qt.AlignLeft|Qt.AlignVCenter
        self.vHeaderAlignment = Qt.AlignRight|Qt.AlignVCenter
    
    def setKeyLabel(self, key, label):
        self.__keyLabels[key] = label
        try:
            i = self.__xType.keys().index(key)
            self.headerDataChanged.emit(Qt.Horizontal, i, i)
        except ValueError:
            pass
    
    def getKeyLabel(self, key):
        if self.__keyLabels.has_key(key):
            return self.__keyLabels[key]
        return key
    
    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column, object=0)
    
    def rowCount(self, index=QModelIndex()):
        return len(self.__modelData)
    
    def columnCount(self, index=QModelIndex()):
        return len(self.__xType)
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(self.hHeaderAlignment))
            return QVariant(int(self.vHeaderAlignment))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            keyName = self.__xType.keyName(section)
            if self.__keyLabels.has_key(keyName):
                return QVariant(self.__keyLabels[keyName])
            return QVariant(keyName)
#        else:
#            print "headerData: {0}".format(variant_to_pyobject(QVariant(int(section + 1))))
        return QVariant(int(section + 1))
    
    def data(self, index, role=Qt.DisplayRole):
        
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()
        
        if role in (Qt.DisplayRole, Qt.EditRole):
            try:
                keyName = self.__xType.keyName(index.column())
                return QVariant(self.__modelData[index.row()][keyName])
            except KeyError:
                return QVariant()
            except AttributeError:
                return QVariant()
        
        if role == Qt.BackgroundColorRole:
            if self._standardRow is not None:
                if index.row() == self._standardRow:
                    return QVariant(QColor(self.standardRowBackground))

        
        if role == qt4.ColumnNameRole:
            return QVariant(unicode(self.__xType.keyName(index.column())))
        if role == qt4.RowObjectRole:
            return QVariant(self.__modelData[index.row()])
        
        return QVariant()
    
    def setStandardRow(self, row):
        self._standardRow = row
    
    def standardRow(self):
        return self._standardRow 
    
    def setData(self, index, value, role=Qt.EditRole):
        keyName = self.__xType.keyName(index.column())
        pyValue = variant_to_pyobject(value)
        self.__modelData[index.row()][keyName] = pyValue
        self.dataChanged.emit(index, index)
        return True
    
    def flags(self, index):
        if not self.isEditable:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled  | Qt.ItemIsEditable
    
    def insertRows(self, row, count, parent=QModelIndex()):
        if count > 1:
            raise NotImplementedError("Currently only one row can be inserted")
        rowCount = self.rowCount(parent)
        if row != rowCount:
            raise NotImplementedError("Currently the row can be inserted at the end")
        
        if self.__xType.maxLength is not None:
            if rowCount >= self.__xType.maxLength:
                return False
            
        self.beginInsertRows(parent, row, row)
        self.__modelData.append(self.getRowTemplate())
        self.endInsertRows()
        return True
    
    def removeRows(self, row, count, parentIndex=QModelIndex()):
        if count > 1:
            raise NotImplementedError("Currently only one row can be removed")
        
        if self.__xType.minLength is not None:
            if self.rowCount() <= self.__xType.minLength:
                return False
            
        self.beginRemoveRows(parentIndex, row, row)
        self.__modelData.pop(row)
        self.endRemoveRows()
        
        return True
    
    def addRow(self, *args, **kwargs):
        if self.__xType.maxLength is not None:
            if self.rowCount() >= self.__xType.maxLength:
                return False
        
        data = {}
        if kwargs:
            data = kwargs
        if args:
            data = args[0]
        
        rowTpl = self.getRowTemplate()
        for key in data:
            if rowTpl.has_key(key):
                rowTpl[key] = data[key]
        
        nextIndex = len(self.__modelData)
        if nextIndex < 0:
            nextIndex = 0
        
        self.beginInsertRows(QModelIndex(), nextIndex, nextIndex+1)
        self.__modelData.append(rowTpl)
        self.endInsertRows()
    
    def getRowTemplate(self):
        template = {}
        for key in self.__xType.keys():
            xType = self.__xType.keyType(key)
            if isinstance(xType, XType):
                template[key] = xType.defaultValue
            else:
                template[key] = None
        return template
    
    def setModelData(self, modelData):
        self.beginResetModel()
        
        self.__modelData = []
        
        
        i = 0    
        for row in modelData:
            rowTpl = self.getRowTemplate()
            for key in row:
                pyKey = unicode(key)
                if rowTpl.has_key(pyKey):
                    rowTpl[pyKey] = row[key]
                
            self.__modelData.append(rowTpl)
            
            i += 1
            if self.__xType.maxLength is not None:
                if i >= self.__xType.maxLength:
                    break
            
        
        self.endResetModel()
    
    @pyqtSlot()
    def exportModelData(self, omitEmptyRows=False):
        if not omitEmptyRows:
            return self.__modelData
        else:
            result = []
            for row in self.__modelData:
                rowIsEmpty = True
                for key in self.__xType.keys():
                    if row.has_key(key) and row[key]:
                        rowIsEmpty = False
                if not rowIsEmpty:
                    result.append(row)
            return result