'''
Created on 21.03.2012

@author: michi
'''
from PyQt4.QtGui import QTableView

from ems.qt4.gui.mapper.base import BaseStrategy #@UnresolvedImport
from ems.xtype.base import DictType, ObjectInstanceType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.objectinstancetype import ObjectInstanceDelegate #@UnresolvedImport

class DictStrategy(BaseStrategy):
    
    def match(self, param):
        if isinstance(param, DictType):
            return True
        
        return False
    
    def getDelegateForItem(self, mapper, type_, parent=None):
        return ObjectInstanceDelegate(type_, parent)
    
    def addMapping(self, mapper, widget, columnName, type_):
        if isinstance(widget, QTableView):
            columnIndex = mapper.model.columnOfName(columnName)
            mapper.dataWidgetMapper.addMapping(widget, columnIndex)
    