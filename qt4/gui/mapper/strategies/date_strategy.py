'''
Created on 21.03.2012

@author: michi
'''
from PyQt4.QtGui import QDateEdit

from ems.qt4.gui.mapper.base import BaseStrategy #@UnresolvedImport
from ems.xtype.base import DateType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.datetype import DateTypeDelegate #@UnresolvedImport

class DateStrategy(BaseStrategy):
    
    def match(self, param):
        if isinstance(param, DateType):
            return True
        return False
    
    def getDelegateForItem(self, mapper, type_, parent=None):
        return DateTypeDelegate(type_, parent)
    
    def addMapping(self, mapper, widget, columnName, type_):
        if isinstance(widget, QDateEdit):
            widget.dateDelegate = self.getDelegateForItem(mapper, type_, None)
            widget.dateDelegate.configureEditor(widget, type_)
        columnIndex = mapper.model.columnOfName(columnName)
        mapper.dataWidgetMapper.addMapping(widget, columnIndex)
