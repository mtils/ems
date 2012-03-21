'''
Created on 21.03.2012

@author: michi
'''
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
