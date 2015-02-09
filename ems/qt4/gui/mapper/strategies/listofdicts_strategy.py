'''
Created on 21.03.2012

@author: michi
'''
from PyQt4.QtGui import QTableView

from ems.qt4.gui.mapper.base import BaseStrategy #@UnresolvedImport
from ems.xtype.base import DictType, SequenceType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.listofdictstype import ListOfDictsDelegate #@UnresolvedImport

class ListOfDictsStrategy(BaseStrategy):
    
    def __init__(self, parent=None):
        BaseStrategy.__init__(self, parent)
        self.addPixmap = None
        self.removePixmap = None
        
    def match(self, param):
        if isinstance(param, SequenceType) and isinstance(param.itemType,
                                                          DictType):
            return True
        
        return False
    
    def getDelegateForItem(self, mapper, type_, parent=None):
        delegate = ListOfDictsDelegate(type_, parent)
        if self.addPixmap is not None:
            delegate.addPixmap = self.addPixmap
        if self.removePixmap is not None:
            delegate.removePixmap = self.removePixmap 
        return delegate
    
    def addMapping(self, mapper, widget, columnName, type_):
        if isinstance(widget, QTableView):
            
            #widget.setModel(mapper.model.childModel())
            
            columnIndex = mapper.model.columnOfName(columnName)
            mapper.dataWidgetMapper.addMapping(widget, columnIndex)
    