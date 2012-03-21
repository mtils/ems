'''
Created on 21.03.2012

@author: michi
'''
from PyQt4.QtGui import QStyledItemDelegate

from ems.qt4.gui.mapper.base import BaseStrategy #@UnresolvedImport
from ems.xtype.base import BoolType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.stringtype import StringTypeDelegate #@UnresolvedImport

class BoolStrategy(BaseStrategy):
    
    def match(self, param):
        if isinstance(param, BoolType):
            return True
        return False
    
    def getDelegateForItem(self, mapper, type_, parent=None):
        return QStyledItemDelegate(parent)
