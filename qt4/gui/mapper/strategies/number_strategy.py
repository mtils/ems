'''
Created on 21.03.2012

@author: michi
'''
from ems.qt4.gui.mapper.base import BaseStrategy #@UnresolvedImport
from ems.xtype.base import NumberType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.numbertype import NumberTypeDelegate #@UnresolvedImport

class NumberStrategy(BaseStrategy):
    
    def match(self, param):
        if isinstance(param, NumberType):
            return True
        return False
    
    def getDelegateForItem(self, mapper, type_, parent=None):
        return NumberTypeDelegate(type_, parent)
