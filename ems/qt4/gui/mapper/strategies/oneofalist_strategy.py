'''
Created on 21.03.2012

@author: michi
'''
from PyQt4.QtGui import QComboBox, QAbstractButton, QButtonGroup

from ems.qt4.gui.mapper.base import BaseStrategy
from ems.qt4.gui.mapper.delegates.buttongroup_delegate import ButtonGroupDelegate
from ems.qt4.gui.itemdelegate.xtypes.oneofalisttype import OneOfAListDelegate
from ems.xtype.base import OneOfAListType


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

        if isinstance(widget, QButtonGroup):
            widget.mapperDelegate = ButtonGroupDelegate(widget, mapper.model, columnIndex, parent=widget)
            mapper.dataWidgetMapper.currentIndexChanged.connect(widget.mapperDelegate.setCurrentRow)
            return

        if isinstance(widget, QComboBox):
            index = mapper.model.createIndex(0, columnIndex)
            delegate = mapper.dataWidgetMapper.itemDelegate()._getDelegate(index)
            delegate.configureEditor(widget, type_)
            delegate.valueNames = self.valueNames

        mapper.dataWidgetMapper.addMapping(widget, columnIndex)

