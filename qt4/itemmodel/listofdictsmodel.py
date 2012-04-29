'''
Created on 04.03.2012

@author: michi
'''
from copy import copy

from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant, \
    pyqtSignal, pyqtSlot
from PyQt4.QtGui import QColor

from ems import qt4
from ems.qt4.util import variant_to_pyobject, VariantContainer
from ems.xtype.base import XType #@UnresolvedImport
from ems.qt4.itemmodel.reflectable_mixin import ReflectableMixin #@UnresolvedImport
from ems.xtype.base import ListOfDictsType #@UnresolvedImport
from ems.qt4.itemmodel.xtype.base import MultipleRowDictModel #@UnresolvedImport
#from pprint import pprint

class ListOfDictsModel(MultipleRowDictModel):
    
    def __init__(self, xType, parent=None):
        MultipleRowDictModel.__init__(self, xType, parent)
        self.isEditable = True
        self._standardRow = None
        self.standardRowBackground = '#00E3F3'
    
    def setStandardRow(self, row):
        self._standardRow = row
    
    def standardRow(self):
        return self._standardRow 
    
    def addRow(self, *args, **kwargs):
        if self._xType.maxLength is not None:
            if self.rowCount() >= self._xType.maxLength:
                return False
        
        data = {}
        if kwargs:
            data = kwargs
        if args:
            data = args[0]
            
        print data
        
        rowTpl = self.getRowTemplate(data)
        
        nextIndex = len(self._modelData)
        if nextIndex < 0:
            nextIndex = 0
        
        self.beginInsertRows(QModelIndex(), nextIndex, nextIndex+1)
        self._appendToModelData(rowTpl)
        
        self.endInsertRows()
    
#    def getRowTemplate(self):
#        template = {}
#        for key in self.__xType.keys():
#            xType = self.__xType.keyType(key)
#            if isinstance(xType, XType):
#                template[key] = xType.defaultValue
#            else:
#                template[key] = None
#        return template
    
    
    @pyqtSlot()
    def exportModelData(self, omitEmptyRows=False):
        if not omitEmptyRows:
            return self._modelData
        else:
            result = []
            for row in self._modelData:
                rowIsEmpty = True
                for key in self.__xType.keys():
                    if row.has_key(key) and row[key]:
                        rowIsEmpty = False
                if not rowIsEmpty:
                    result.append(row)
            return result