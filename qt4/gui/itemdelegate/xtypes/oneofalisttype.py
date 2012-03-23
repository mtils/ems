'''
Created on 22.03.2012

@author: michi
'''
from PyQt4.QtCore import QString, Qt, QAbstractListModel, QAbstractItemModel
from PyQt4.QtGui import QComboBox

from ems.xtype.base import EnumType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypedelegate import XTypeDelegate #@UnresolvedImport
from ems.qt4.util import variant_to_pyobject
from ems.qt4.itemmodel.xtype.oneofalistmodel import OneOfAListModel #@UnresolvedImport

class OneOfAListDelegate(XTypeDelegate):
    
    def __init__(self, xType, parent=None):
        XTypeDelegate.__init__(self, xType, parent)
        self.valueNames = {}
        self._model = None
    
    def getString(self, value):
        if value is None:
            return ""
        
        if self.valueNames.has_key(value):
            return self.valueNames[value]
        return unicode(value)
    
    def getModel(self):
        if not isinstance(self._model, QAbstractItemModel):
            self._model = OneOfAListModel(self.xType, self)
            self._model.valueNames = self.valueNames
        return self._model
    
    def setModel(self, model):
        self._model = model
    
    model = property(getModel, setModel)
    
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        self.configureEditor(editor, self.xType)
        return editor
    
    def configureEditor(self, editor, xType):
        if isinstance(editor, QComboBox):
            editor.setModel(self.model)
            
        
    def setEditorData(self, editor, index):
        if isinstance(editor, QComboBox):
            for i in range(editor.count()):
                editorData = variant_to_pyobject(editor.itemData(i, Qt.EditRole))
                modelData = variant_to_pyobject(index.data(Qt.EditRole))
                if modelData is editorData:
                    editor.setCurrentIndex(i)
                    return None
                
        
        return XTypeDelegate.setEditorData(self, editor, index)
    
    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            value = editor.itemData(editor.currentIndex(), Qt.EditRole)
            model.setData(index,value)
            return None
        return XTypeDelegate.setModelData(self, editor, model, index)

