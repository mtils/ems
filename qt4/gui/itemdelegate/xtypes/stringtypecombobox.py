'''
Created on 22.03.2012

@author: michi
'''
from PyQt4.QtCore import QString, Qt, QAbstractListModel, QAbstractItemModel
from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QComboBox, QAbstractButton, QLineEdit

from ems.xtype.base import XType, NumberType, BoolType, StringType, ComplexType
from ems.qt4.gui.itemdelegate.xtypedelegate import XTypeDelegate #@UnresolvedImport
from ems.qt4.util import variant_to_pyobject
from ems.qt4.itemmodel.xtype.oneofalistmodel import OneOfAListModel #@UnresolvedImport

class StringComboboxDelegate(XTypeDelegate):
    
    def __init__(self, xType, parent=None):
        XTypeDelegate.__init__(self, xType, parent)
        self._model = None
        self._itemsModelRole = Qt.UserRole
    
    def getString(self, value):
        if self.valueNames.has_key(value):
            return self.valueNames[value]
        
        if value is None:
            return ""
        
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
        editor = QLineEdit(parent)
        #self.configureEditor(editor, self.xType)
        return editor

    def configureEditor(self, editor, xType):
        """OneOfAListDelegate.configureEditor(QComboBox editor, XType xType)
        @brief Configures the Combobox. If it has a property named
               "indexMapping" it maps with it. If not it builds an own model
               with the OneOfAListType
        
        :returns: void
        """

        if isinstance(editor, QComboBox):
            if editor.property('indexMapping').isValid():
                self._itemsModelRole = Qt.UserRole
                mapping = variant_to_pyobject(editor.property('indexMapping'))
                pyType = xType.itemType.pyType
                for idx, srcVal in enumerate(mapping):
                    val = unicode(srcVal)
                    if pyType is int:
                        idxValue = int(val)
                    elif pyType is float:
                        idxValue = float(val)
                    elif pyType is str or pyType is unicode:
                        idxValue = val
                    elif pyType is bool:
                        idxValue = BoolType.castToBool(val)
                    else:
                        msg = "Couldnt map value '{0}' of indexMapping".format(val)
                        raise TypeError(msg)
                    editor.setItemData(idx, QVariant(idxValue), self._itemsModelRole)
            else:
                editor.setModel(self.getModel())

    def setEditorData(self, editor, index):

        if isinstance(editor, QComboBox):
            modelData = variant_to_pyobject(index.data(Qt.EditRole))


            for i in range(editor.count()):
                editorData = variant_to_pyobject(editor.itemData(i, self._itemsModelRole))

                if modelData == editorData:
                    editor.setCurrentIndex(i)
                    return None

        return XTypeDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            value = editor.itemData(editor.currentIndex(), self._itemsModelRole)
            model.setData(index, value, Qt.EditRole)
            return None
        return XTypeDelegate.setModelData(self, editor, model, index)

