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
from ems.qt4.itemmodel.listofdictsmodel import ListOfDictsModel #@UnresolvedImport
from ems.qt4.gui.itemdelegate.htmldelegate import HtmlDelegate


class ListOfDictsDelegate(XTypeDelegate):
    
    def __init__(self, xType, parent=None):
        XTypeDelegate.__init__(self, xType, parent)
        self.htmlDelegate = HtmlDelegate(self)
        self.headerLabels = {}
    
    def paint(self, painter, option, index):
        value = variant_to_pyobject(index.data())
        string = self.getString(value)
        option.text = QString.fromUtf8(string)
        self.htmlDelegate.paint(painter, option, index, option.text)
        
    def getString(self, value):
        rows = [u'<table>']
        if isinstance(value, list):
            pyKey2Key = {}
            for row in value:
                rows.append(u'<tr>')
                
                pyKey2Key.clear()
                for key in row:
                    pyKey2Key[unicode(key)] = key
                    
                for pyKey in self.xType.keys():
                    rows.append(u'<td>')
                    rows.append(self.xType.keyType(pyKey).value2String(row[pyKey2Key[pyKey]]))
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
        from ems.qt4.gui.itemdelegate.xtypemapdelegate import XTypeMapDelegate #@UnresolvedImport
        
        model = ListOfDictsModel(self.xType, self)
        pyList = variant_to_pyobject(index.data())
        delegate = XTypeMapDelegate(editor)
        delegate.setXTypeMap(self.xType.xTypeMap)
        editor.setItemDelegate(delegate)
        if isinstance(index.model(), ListOfDictsModel):
            for key in self.xType.keys():
                label = index.model().getKeyLabel(key)
                model.setKeyLabel(key, label)
        if isinstance(pyList, list) and len(pyList):
            model.setModelData(pyList)
        else:
            model.addRow({})
            model.addRow({})
            model.addRow({})
            model.addRow({})
        editor.setModel(model)
        #super(ListOfDictsDelegate, self).setEditorData(editor, index)
    
    def setModelData(self, editor, model, index):
        pyDict = editor.model().exportModelData(True)
        model.setData(index, pyDict)
        
    def sizeHint(self, option, index):
        value = variant_to_pyobject(index.data())
        string = self.getString(value)
        option.text = QString.fromUtf8(string)
        return self.htmlDelegate.sizeHint(option, index, option.text)
    
    
    
        