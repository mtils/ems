'''
Created on 21.03.2012

@author: michi
'''
from PyQt4.QtGui import QLineEdit, QTextEdit, QLabel, QComboBox
from ems.qt4.gui.mapper.base import BaseStrategy #@UnresolvedImport
from ems.xtype.base import StringType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.stringtype import StringTypeDelegate #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.stringtype2label import StringType2LabelDelegate #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.stringtypecombobox import StringComboboxDelegate

class StringStrategy(BaseStrategy):
    
    def match(self, param):
        if isinstance(param, StringType):
            return True
        return False
    
    def getDelegateForItem(self, mapper, type_, parent=None):
        return StringTypeDelegate(type_, parent)
    
    def addMapping(self, mapper, widget, columnName, type_):
        columnIndex = mapper.model.columnOfName(columnName)
        if isinstance(widget, (QLineEdit, QTextEdit)):
            delegate = self.getDelegateForItem(mapper, type_, None)
            delegate.configureEditor(widget, type_)

        elif isinstance(widget, QLabel):
            mapper.dataWidgetMapper.itemDelegate()._columnDelegates[columnIndex] = \
                                                                        StringType2LabelDelegate(type_)
        elif isinstance(widget, QComboBox):
            mapper.dataWidgetMapper.itemDelegate()._columnDelegates[columnIndex] = \
                                                                        StringComboboxDelegate(type_)

        mapper.dataWidgetMapper.addMapping(widget, columnIndex)
