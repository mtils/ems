'''
Created on 10.01.2011

@author: michi
'''
from PyQt4.QtGui import QStyledItemDelegate
from PyQt4.QtCore import Qt, pyqtSlot

from ems import qt4

from ems.xtype.base import StringType, NumberType, UnitType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypedelegate import XTypeDelegate #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.unittype import UnitTypeDelegate #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.stringtype import StringTypeDelegate #@UnresolvedImport


from genericdelegate import GenericDelegate


class XTypeMapDelegate(GenericDelegate):

    def __init__(self, parent=None):
        GenericDelegate.__init__(self, parent)
        self.__xTypeMap = {}
        
    
    def _getDelegate(self, index):
        return self.delegates.get(index.column())
    
    @pyqtSlot(dict)
    def setXTypeMap(self, typeMap):
        self.delegates.clear()
        self.__xTypeMap = typeMap
        for col in self.__xTypeMap:
            if isinstance(self.__xTypeMap[col], UnitType):
                self.delegates[col] = UnitTypeDelegate(self.__xTypeMap[col],
                                                       self)
            elif isinstance(self.__xTypeMap[col], StringType):
                self.delegates[col] = StringTypeDelegate(self.__xTypeMap[col],
                                                         self)
            else:
                self.delegates[col] = XTypeDelegate(self.__xTypeMap[col],
                                                       self)
