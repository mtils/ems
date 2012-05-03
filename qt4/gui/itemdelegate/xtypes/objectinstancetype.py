'''
Created on 04.03.2012

@author: michi
'''
from datetime import date 
from PyQt4.QtCore import QString, QDate, Qt, QVariant
from PyQt4.QtGui import QTableView

from ems.xtype.base import UnitType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypedelegate import XTypeDelegate #@UnresolvedImport
from ems.qt4.util import variant_to_pyobject
from ems.qt4.gui.itemdelegate.htmldelegate import HtmlDelegate
from ems.model.sa.orm.decorator import friendly_name


class ObjectInstanceDelegate(XTypeDelegate):
    
    def __init__(self, xType, parent=None):
        XTypeDelegate.__init__(self, xType, parent)
    
    def getString(self, value):
        return friendly_name(value)
        
    def createEditor(self, parent, option, index):
        widget = QTableView(parent)
        widget.setMinimumWidth(200)
        widget.setMinimumHeight(200)
        widget.verticalHeader().setVisible(False)
        widget.horizontalHeader().setResizeMode(widget.horizontalHeader().Stretch)
        widget.setFrameStyle(widget.StyledPanel)
        widget.setFrameShadow(widget.Raised)
        
        return widget
    
    def setEditorData(self, editor, index):
        from ems.qt4.gui.itemdelegate.xtypemapdelegate import XTypeMapDelegate #@UnresolvedImport
        model = index.model().childModel(index)
        pyList = variant_to_pyobject(index.data())
        
        #delegate = XTypeMapDelegate(editor)
        #delegate.setXTypeMap(self.xType.itemType.xTypeMap)
        #editor.setItemDelegate(delegate)

        if isinstance(pyList, list) and len(pyList):
            model.setModelData(pyList)
        editor.setModel(model)
    
    def setModelData(self, editor, model, index):
        pyObj = editor.model().modelData()
        model.setData(index, pyObj)
        
    def sizeHint(self, option, index):
        value = variant_to_pyobject(index.data())
        string = self.getString(value)
        option.text = QString.fromUtf8(string)
        return self.htmlDelegate.sizeHint(option, index, option.text)
    
    
    
        