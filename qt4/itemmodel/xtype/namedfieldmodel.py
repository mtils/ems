'''
Created on 26.04.2012

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
from ems.qt4.itemmodel.xtype.base import SingleRowDictModel #@UnresolvedImport
from ems.xtype.base import ListOfDictsType #@UnresolvedImport

#from pprint import pprint

class NamedFieldModel(SingleRowDictModel):
    
    def addRow(self, *args, **kwargs):
        if self.rowCount() > 0:
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
        
        self.beginInsertRows(QModelIndex(), 0, 1)
        self._modelData.append(rowTpl)
        self.endInsertRows()
    
    def getRowTemplate(self):
        template = {}
        for key in self._xType.keys():
            xType = self._xType.keyType(key)
            if isinstance(xType, XType):
                template[key] = xType.defaultValue
            else:
                template[key] = None
        return template
    
    def setModelData(self, modelData):
        self.beginResetModel()
        
        self._modelData = []
        
        i = 0    
        
        rowTpl = self.getRowTemplate()
        for key in modelData:
            pyKey = unicode(key)
            if rowTpl.has_key(pyKey):
                rowTpl[pyKey] = modelData[key]
            
        self._modelData.append(rowTpl)    
        
        self.endResetModel()
    
    def _appendToModelData(self, row):
        self._modelData.append(row)
    
    @pyqtSlot()
    def exportModelData(self, omitEmptyRows=False):
        if not omitEmptyRows:
            return self._modelData
        else:
            result = []
            for row in self._modelData:
                rowIsEmpty = True
                for key in self._xType.keys():
                    if row.has_key(key) and row[key]:
                        rowIsEmpty = False
                if not rowIsEmpty:
                    result.append(row)
            return result