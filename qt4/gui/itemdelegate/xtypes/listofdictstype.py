'''
Created on 04.03.2012

@author: michi
'''
from datetime import date 
from PyQt4.QtCore import QString, QDate, Qt, QVariant
from PyQt4.QtGui import QTableView, QIcon

from ems.xtype.base import UnitType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypedelegate import XTypeDelegate #@UnresolvedImport
from ems.qt4.util import variant_to_pyobject
from ems.qt4.gui.itemdelegate.htmldelegate import HtmlDelegate
from ems.qt4.itemmodel.addrow_proxymodel import AddRowProxyModel #@UnresolvedImport
from ems.qt4.gui.mapper.base import BaseMapper #@UnresolvedImport
from ems.qt4.gui.itemdelegate.addrow_delegate import AddRowDelegate #@UnresolvedImport


class ListOfDictsDelegate(XTypeDelegate):
    
    def __init__(self, xType, parent=None):
        XTypeDelegate.__init__(self, xType, parent)
        self.htmlDelegate = HtmlDelegate(self)
        self.headerLabels = {}
        self.addPixmap = None
        self.removePixmap = None
    
    def paint(self, painter, option, index):
        value = variant_to_pyobject(index.data())
        string = self.getString(value, option)
        option.text = QString.fromUtf8(string)
        self.htmlDelegate.paint(painter, option, index, option.text)
        
    def getString(self, value, styleOption=None):
        if styleOption is None:
            rows = [u'<table>']
        else:
            rows = [u'<table style="color:{0}">'.format(styleOption.palette.text().color().name())]
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
        from ems.qt4.gui.itemdelegate.xtypemapdelegate import XTypeMapDelegate #@UnresolvedImport
        model = index.model().childModel(index)
        #print "setEditorData {0}".format(model)
        pyList = variant_to_pyobject(index.data())
        
        editorModel = AddRowProxyModel(model)
        editorModel.setSourceModel(model)
        
        mapper = BaseMapper(editorModel,editor)
        viewDelegate = mapper.getDelegateForItemView()
        
            
        addRowDelegate = AddRowDelegate(editor)
        
        if self.addPixmap is not None:
            editorModel.addPixmap = self.addPixmap
            addRowDelegate.addIcon = QIcon(self.addPixmap)
        if self.removePixmap is not None:
            editorModel.removePixmap = self.removePixmap
            addRowDelegate.removeIcon = QIcon(self.removePixmap)
        
        
        
        viewDelegate.columnDelegates()[0] = addRowDelegate
        
        editor.setItemDelegate(viewDelegate)
        
        
        
        
        #delegate = XTypeMapDelegate(editor)
        #delegate.setXTypeMap(self.xType.itemType.xTypeMap)
        #editor.setItemDelegate(delegate)

        if isinstance(pyList, list) and len(pyList):
            model.setModelData(pyList)
        
        editor.setModel(editorModel)
        if isinstance(editor, QTableView):
            editor.pressed.connect(editorModel.onIndexPressed)
        #editor.setModel(model)
    
    def setModelData(self, editor, model, index):
        pyDict = editor.model().exportModelData(True)
        model.setData(index, pyDict)
        
    def sizeHint(self, option, index):
        value = variant_to_pyobject(index.data())
        string = self.getString(value)
        option.text = QString.fromUtf8(string)
        return self.htmlDelegate.sizeHint(option, index, option.text)
    
    
    
        