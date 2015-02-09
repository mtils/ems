'''
Created on 04.03.2012

@author: michi
'''
from PyQt4.QtCore import QString, Qt
from PyQt4.QtGui import QLineEdit, QCompleter, QStringListModel, \
    QAbstractProxyModel

from ems.xtype.base import StringType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypedelegate import XTypeDelegate #@UnresolvedImport

class HintListModel(QAbstractProxyModel):
    def __init__(self, parent=None):
        QAbstractProxyModel.__init__(self, parent)
    
    def match(self, start, role, value, hits=1, flags=Qt.MatchStartsWith | Qt.MatchWrap):
        return QStringListModel.match(self, start, role, value, hits, flags)

class StringTypeDelegate(XTypeDelegate):
    
    def createEditor(self, parent, option, index):
        widget = QLineEdit(parent)
        self.configureEditor(widget, self.xType)
        return widget
    
    def configureEditor(self, widget, xType):
        XTypeDelegate.configureEditor(self, widget, xType)
        widget.setMaxLength(self.xType.maxLength)
        widget.setAlignment(self.textAlignment)
        if hasattr(self.xType, 'hints') and len(self.xType.hints):
            completer = QCompleter(self.xType.hints, self)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            widget.setCompleter(completer)
        
        