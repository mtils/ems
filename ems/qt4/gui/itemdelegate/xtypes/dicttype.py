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


class DictDelegate(XTypeDelegate):
    
    def __init__(self, xType, parent=None):
        XTypeDelegate.__init__(self, xType, parent)
    
    def getString(self, value):
        rows = [u'<table>']
        if isinstance(value, list):
            pyKey2Key = {}
            for row in value:
                rows.append(u'<tr>')
                
                pyKey2Key.clear()
                for key in row:
                    pyKey2Key[unicode(key)] = key
                    
                for pyKey in self.xType.itemType.keys():
                    rows.append(u'<td>')
                    rows.append(unicode(self.xType.itemType.keyType(pyKey).value2String(row[pyKey2Key[pyKey]])))
                    rows.append(u'</td>')
                rows.append(u'</tr>')
            
        rows.append(u'</table>')
        return u"".join(rows)
        
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
        model = index.model().childModel(index)
        pyObject = variant_to_pyobject(index.data())
        if isinstance(pyObject, model.xType.cls):
            model.setModelData(pyObject)
        editor.setModel(model)
    
    def setModelData(self, editor, model, index):
        pyObj = editor.model().modelData()
        model.setData(index, pyObj)
        
    def sizeHint(self, option, index):
        value = variant_to_pyobject(index.data())
        string = self.getString(value)
        option.text = QString.fromUtf8(string)
        return self.htmlDelegate.sizeHint(option, index, option.text)
    
    
    
        