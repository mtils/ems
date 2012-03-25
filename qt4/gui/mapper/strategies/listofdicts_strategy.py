'''
Created on 21.03.2012

@author: michi
'''
from PyQt4.QtGui import QComboBox

from ems.qt4.gui.mapper.base import BaseStrategy #@UnresolvedImport
from ems.xtype.base import ListOfDictsType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.listofdictstype import ListOfDictsDelegate #@UnresolvedImport

class ListOfDictsStrategy(BaseStrategy):
    
    def match(self, param):
        if isinstance(param, ListOfDictsType):
            return True
        return False
    
    def getDelegateForItem(self, mapper, type_, parent=None):
        return ListOfDictsDelegate(type_, parent)
    
    def addMapping(self, mapper, widget, columnName, type_):
        if isinstance(widget, QComboBox):
            widget.boolDelegate = self.getDelegateForItem(mapper, type_, None)
            widget.boolDelegate.configureEditor(widget, type_)
            widget.boolDelegate.valueNames = self.valueNames
        columnIndex = mapper.model.columnOfName(columnName)
        mapper.dataWidgetMapper.addMapping(widget, columnIndex)
    