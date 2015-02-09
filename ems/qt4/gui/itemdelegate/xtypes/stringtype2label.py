'''
Created on 04.03.2012

@author: michi
'''
from PyQt4.QtCore import QString, QVariant
from PyQt4.QtGui import QLineEdit

from ems.xtype.base import StringType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypedelegate import XTypeDelegate #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.stringtype import StringTypeDelegate #@UnresolvedImport

class StringType2LabelDelegate(StringTypeDelegate):
    def createEditor(self, parent, option, index):
        widget = QLineEdit(parent)
        self.configureEditor(widget, self.xType)
        return widget
    
    def configureEditor(self, widget, xType):
        XTypeDelegate.configureEditor(self, widget, xType)
        widget.setMaxLength(self.xType.maxLength)
        widget.setAlignment(self.textAlignment)
        
    def setModelData(self, editor, model, index):
        model.setData(index, QVariant(editor.text()))
    
    def setEditorData(self, editor, index):
        editor.setText(index.data().toString())    