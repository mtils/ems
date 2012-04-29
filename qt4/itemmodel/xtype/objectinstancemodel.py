'''
Created on 26.04.2012

@author: michi
'''
from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant, \
    pyqtSignal, pyqtSlot
from PyQt4.QtGui import QColor

from ems import qt4
from ems.qt4.util import variant_to_pyobject, VariantContainer
from ems.xtype.base import XType #@UnresolvedImport
from ems.qt4.itemmodel.reflectable_mixin import ReflectableMixin #@UnresolvedImport
from ems.xtype.base import ListOfDictsType #@UnresolvedImport
from namedfieldmodel import NamedFieldModel #@UnresolvedImport
from copy import copy

from ems.qt4.itemmodel.xtype.base import SingleRowObjectModel #@UnresolvedImport
#from pprint import pprint

class ObjectInstanceModel(SingleRowObjectModel):
    
    def addRow(self, *args, **kwargs):
        if self.rowCount() > 0:
            return False
        
        data = {}
        if kwargs:
            data = kwargs
        if args:
            data = args[0]
        
        rowTpl = self.getRowTemplate()
        for key in self.xType.keys():
            if isinstance(data, dict):
                rowTpl.__setattr__(key, data[key])
            else:
                rowTpl.__setattr__(key, data.__getattribute(key))
        
        self.beginInsertRows(QModelIndex(), 0, 1)
        self._modelData.append(rowTpl)
        self.endInsertRows()
    
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