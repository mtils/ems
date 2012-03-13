'''
Created on 04.03.2012

@author: michi
'''
from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant, \
    pyqtSignal, pyqtSlot
from PyQt4.QtGui import QColor

from ems import qt4
from ems.qt4.util import variant_to_pyobject

class ListOfDictsModel(QAbstractTableModel):
    
    xTypeMapChanged = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.__modelData = []
        self.__keys = []
        self.__keyLabels = {}
        self.__xTypes = {}
        self.isEditable = True
        self._standardRow = None
        self.standardRowBackground = '#00E3F3'
        self.hHeaderAlignment = Qt.AlignLeft|Qt.AlignVCenter
        self.vHeaderAlignment = Qt.AlignRight|Qt.AlignVCenter
    
    def xTypeMap(self):
        return self.__xTypes
    
    def setKeyLabel(self, key, label):
        self.__keyLabels[key] = label
        i = self.__keys.index(key)
        self.headerDataChanged.emit(Qt.Horizontal, i, i)
    
    def setXType(self, col, xType):
        if not self.__xTypes.has_key(col):
            self.__xTypes[col] = xType
            self.xTypeMapChanged.emit(self.__xTypes)
        if self.__xTypes is not xType:
            self.__xTypes[col] = xType
            self.xTypeMapChanged.emit(self.__xTypes)
    
    def addKey(self, name, xType=None, label=None):
        nextIndex = len(self.__keys)
        if nextIndex < 0:
            nextIndex = 0
        self.beginInsertColumns(QModelIndex(), nextIndex, nextIndex+1)
        self.__keys.append(name)
        self.endInsertColumns()
        if xType is not None:
            self.setXType(nextIndex, xType)
        if label is not None:
            self.setKeyLabel(name, label)
    
    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column, object=0)
    
    def rowCount(self, index=QModelIndex()):
        #self.perform()
        #print "rowCount called %s" % len(self.__modelData)
        return len(self.__modelData)
    
    def columnCount(self, index=QModelIndex()):
        #self.perform()
        return len(self.__keys)
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(self.hHeaderAlignment))
            return QVariant(int(self.vHeaderAlignment))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            keyName = self.__keys[section]
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
                keyName = self.__keys[index.column()]
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
            return QVariant(unicode(self.__keys[index.column()]))
        if role == qt4.RowObjectRole:
            return QVariant(self.__modelData[index.row()])
        
        return QVariant()
    
    def setStandardRow(self, row):
        self._standardRow = row
    
    def standardRow(self):
        return self._standardRow 
    
    def setData(self, index, value, role=Qt.EditRole):
        keyName = self.__keys[index.column()]
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
        
        self.beginInsertRows(parent, row, row)
        self.__modelData.append(self.getRowTemplate())
        self.endInsertRows()
        return True
    
    def removeRows(self, row, count, parentIndex=QModelIndex()):
        if count > 1:
            raise NotImplementedError("Currently only one row can be removed")
        self.beginRemoveRows(parentIndex, row, row)
        self.__modelData.pop(row)
        self.endRemoveRows()
        
        return True
    
    def addRow(self, *args, **kwargs):
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
        for key in self.__keys:
            template[key] = None
        return template
    
    def setModelData(self, modelData):
        self.beginResetModel()
        self.__modelData = modelData
        self.endResetModel()
    
    @pyqtSlot()
    def exportModelData(self):
        return self.__modelData