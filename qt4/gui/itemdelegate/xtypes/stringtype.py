'''
Created on 04.03.2012

@author: michi
'''
from PyQt4.QtCore import QString
from PyQt4.QtGui import QLineEdit, QCompleter

from ems.xtype.base import StringType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypedelegate import XTypeDelegate #@UnresolvedImport

class StringTypeDelegate(XTypeDelegate):
    def createEditor(self, parent, option, index):
        widget = QLineEdit(parent)
        self.configureEditor(widget, self.xType)
        return widget
    
    def configureEditor(self, widget, xType):
        XTypeDelegate.configureEditor(self, widget, xType)
        widget.setMaxLength(self.xType.maxLength)
        widget.setAlignment(self.textAlignment)
        if hasattr(self.xType,'hints') and len(self.xType.hints):
            completer = QCompleter(self.xType.hints, self)
            widget.setCompleter(completer)
        
        