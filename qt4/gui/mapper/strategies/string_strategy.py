'''
Created on 21.03.2012

@author: michi
'''
from ems.qt4.gui.mapper.base import BaseStrategy #@UnresolvedImport
from ems.xtype.base import StringType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.stringtype import StringTypeDelegate #@UnresolvedImport

class StringStrategy(BaseStrategy):
    
    def match(self, param):
        if isinstance(param, StringType):
            return True
        return False
    
    def getDelegateForItem(self, mapper, type_, parent=None):
        return StringTypeDelegate(type_, parent)
