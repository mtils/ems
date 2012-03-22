'''
Created on 22.03.2012

@author: michi
'''
from PyQt4.QtCore import QString, Qt, QAbstractListModel
from PyQt4.QtGui import QComboBox

from ems.xtype.base import EnumType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypedelegate import XTypeDelegate #@UnresolvedImport
from ems.qt4.util import variant_to_pyobject

class EnumDelegateModel(QAbstractListModel):
    pass

class EnumDelegate(XTypeDelegate):
    
    def __init__(self, xType, parent=None):
        XTypeDelegate.__init__(self, xType, parent)
        self._valueNames = {}
        
    def setEditorData(self, editor, index):
        if isinstance(editor, QComboBox):
            for i in range(editor.count()):
                editorData = variant_to_pyobject(editor.itemData(i))
                modelData = variant_to_pyobject(index.data(Qt.EditRole))
                
                if modelData is editorData:
                    editor.setCurrentIndex(i)
                    return None
                
        
        return XTypeDelegate.setEditorData(self, editor, index)
    
    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            value = editor.itemData(editor.currentIndex())
            model.setData(index,value)
            return None
        return XTypeDelegate.setModelData(self, editor, model, index)

