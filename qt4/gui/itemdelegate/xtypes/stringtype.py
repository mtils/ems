'''
Created on 04.03.2012

@author: michi
'''
from PyQt4.QtCore import QString
from PyQt4.QtGui import QLineEdit

from ems.xtype.base import StringType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypedelegate import XTypeDelegate #@UnresolvedImport

class StringTypeDelegate(XTypeDelegate):
    def createEditor(self, parent, option, index):
        widget = QLineEdit(parent)
        widget.setMaxLength(self.xType.maxLength)
        widget.setAlignment(self.textAlignment)
        return widget
    
        