'''
Created on 19.09.2011

@author: michi
'''
from PyQt4.QtCore import Qt, QVariant
from PyQt4.QtGui import QStyledItemDelegate, QComboBox

from ems.qt4.util import variant_to_pyobject
from ems.qt4.gui.widgets.bigcombo import BigComboBox


from base import MapperDelegate #@UnresolvedImport

class Many2OneDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)

    def setEditorData(self, editor, index):
        if isinstance(editor, QComboBox):
            for i in range(editor.count()):
                editorData = variant_to_pyobject(editor.itemData(i))
                modelData = variant_to_pyobject(index.data(Qt.EditRole))
                
                if modelData is editorData:
                    editor.setCurrentIndex(i)
                    return None
                
        
        return QStyledItemDelegate.setEditorData(self, editor, index)
    
    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            value = editor.itemData(editor.currentIndex())
            model.setData(index,value)
            return None
        return QStyledItemDelegate.setModelData(self, editor, model, index)

class Many2OneComboMapperDelegate(MapperDelegate, Many2OneDelegate):
    def __init__(self, mapper, propertyName, parent=None):
        MapperDelegate.__init__(self, mapper, propertyName, parent)
        Many2OneDelegate.__init__(self, parent)
        