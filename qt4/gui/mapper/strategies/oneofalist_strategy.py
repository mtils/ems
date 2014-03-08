'''
Created on 21.03.2012

@author: michi
'''
from PyQt4.QtCore import QModelIndex
from PyQt4.QtGui import QStyledItemDelegate, QComboBox, QAbstractButton, QRadioButton

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
        columnIndex = mapper.model.columnOfName(columnName)
        if isinstance(widget, QComboBox):
            index = mapper.model.createIndex(0, columnIndex)
            delegate = mapper.dataWidgetMapper.itemDelegate()._getDelegate(index)
            delegate.configureEditor(widget, type_)
            delegate.valueNames = self.valueNames

        mapper.dataWidgetMapper.addMapping(widget, columnIndex)

