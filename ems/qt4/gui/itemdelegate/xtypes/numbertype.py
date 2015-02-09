'''
Created on 04.03.2012

@author: michi
'''
from PyQt4.QtCore import QString, Qt
from PyQt4.QtGui import QSpinBox, QDoubleSpinBox

from ems.xtype.base import UnitType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypedelegate import XTypeDelegate #@UnresolvedImport

class NumberTypeDelegate(XTypeDelegate):
    
    def __init__(self, xType, parent=None):
        XTypeDelegate.__init__(self, xType, parent)
        self.textAlignment = Qt.AlignRight | Qt.AlignVCenter
    
    def createEditor(self, parent, option, index):
        if self.xType.pyType == float:
            widget = QDoubleSpinBox(parent)
            if self.xType.decimalsCount:
                widget.setDecimals(self.xType.decimalsCount)
        elif self.xType.pyType == int:
            widget = QSpinBox(parent)
        else:
            XTypeDelegate.createEditor(self, parent, option, index)
        self.configureEditor(widget, self.xType)
        return widget
    
    def configureEditor(self, widget, xType):
        XTypeDelegate.configureEditor(self, widget, xType)
        widget.setSuffix(QString.fromUtf8(self.xType.strSuffix))
        widget.setPrefix(QString.fromUtf8(self.xType.strPrefix))
        widget.setMinimum(self.xType.minValue)
        widget.setMaximum(self.xType.maxValue)
        if self.xType.pyType == float and self.xType.decimalsCount is not None:
            widget.setDecimals(self.xType.decimalsCount)
    
        