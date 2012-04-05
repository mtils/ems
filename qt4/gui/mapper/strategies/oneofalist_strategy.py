'''
Created on 21.03.2012

@author: michi
'''
from PyQt4.QtGui import QStyledItemDelegate, QComboBox

from ems.qt4.gui.mapper.base import BaseStrategy #@UnresolvedImport
from ems.xtype.base import BoolType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.stringtype import StringTypeDelegate #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.oneofalisttype import OneOfAListDelegate #@UnresolvedImport
from ems.xtype.base import OneOfAListType #@UnresolvedImport
from ems.qt4.itemmodel.xtype.oneofalistmodel import OneOfAListModel #@UnresolvedImport

class OneOfAListStrategy(BaseStrategy):
    
    def __init__(self, parent=None):
        BaseStrategy.__init__(self, parent)
        self.valueNames = {}
    
    def match(self, param):
        if isinstance(param, OneOfAListType):
            return True
        return False
    
    def getDelegateForItem(self, mapper, type_, parent=None):
        delegate = OneOfAListDelegate(type_, parent)
        delegate.valueNames = self.valueNames
        return delegate
    
    def addMapping(self, mapper, widget, columnName, type_):
        if isinstance(widget, QComboBox):
            widget.boolDelegate = self.getDelegateForItem(mapper, type_, None)
            widget.boolDelegate.configureEditor(widget, type_)
            widget.boolDelegate.valueNames = self.valueNames
        columnIndex = mapper.model.columnOfName(columnName)
        mapper.dataWidgetMapper.addMapping(widget, columnIndex)
    
