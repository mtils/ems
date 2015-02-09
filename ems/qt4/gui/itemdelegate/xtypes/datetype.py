'''
Created on 04.03.2012

@author: michi
'''
from datetime import date 
from PyQt4.QtCore import QString, QDate, Qt, QVariant
from PyQt4.QtGui import QSpinBox, QDoubleSpinBox, QDateEdit

from ems.xtype.base import UnitType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypedelegate import XTypeDelegate #@UnresolvedImport
from ems.qt4.util import variant_to_pyobject

class DateTypeDelegate(XTypeDelegate):
    
    def getString(self, value):
        #print "Isch bins"
        if isinstance(value, date):
            qValue = QDate(value.year, value.month, value.day)
            strValue = unicode(qValue.toString(Qt.SystemLocaleShortDate))
        else:
            strValue = ""
        
        return self.xType.value2String(strValue)
    
    def createEditor(self, parent, option, index):
        widget = QDateEdit(parent)
        self.configureEditor(widget, self.xType)
        return widget
    
    def configureEditor(self, widget, xType):
        XTypeDelegate.configureEditor(self, widget, xType)
        
        if isinstance(self.xType.minDate, date):
            widget.setMinimumDate(QDate(self.xType.minDate.year,
                                        self.xType.minDate.month,
                                        self.xType.minDate.day))
            
        if isinstance(self.xType.maxDate, date):
            widget.setMaximumDate(QDate(self.xType.maxDate.year,
                                        self.xType.maxDate.month,
                                        self.xType.maxDate.day))
    
    def setEditorData(self, editor, index):
        pyDate = variant_to_pyobject(index.data())
        qDate = QDate(pyDate.year, pyDate.month, pyDate.day)
        editor.setDate(qDate)
        super(DateTypeDelegate, self).setEditorData(editor, index)
    
    def setModelData(self, editor, model, index):
        qDate = editor.date()
        pyDate = date(qDate.year(), qDate.month(), qDate.day())
        model.setData(index, QVariant(pyDate))
        
    
    
    
    
        