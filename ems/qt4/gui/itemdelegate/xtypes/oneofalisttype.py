'''
Created on 22.03.2012

@author: michi
'''
from PyQt4.QtCore import QString, Qt, QAbstractListModel, QAbstractItemModel
from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QComboBox, QAbstractButton

from ems.xtype.base import XType, NumberType, BoolType, StringType, ComplexType
from ems.xtype.base import OneOfAListType
from ems.qt4.gui.itemdelegate.xtypedelegate import XTypeDelegate #@UnresolvedImport
from ems.qt4.util import variant_to_pyobject as py
from ems.qt4.itemmodel.xtype.oneofalistmodel import OneOfAListModel #@UnresolvedImport

class OneOfAListDelegate(XTypeDelegate):
    
    def __init__(self, xType, parent=None):
        XTypeDelegate.__init__(self, xType, parent)
        self.valueNames = {}
        self._model = None
        self._itemsModelRole = Qt.EditRole
    
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
        editor = QComboBox(parent)
        self.configureEditor(editor, self.xType)
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
                mapping = py(editor.property('indexMapping'))
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

    def collectButtonSiblings(self, button):
        siblings = []
        if button.group():
            for child in button.group().buttons():
                siblings.append(child)
        else:
            parentWidget = button.parentWidget()
            for child in  parentWidget.findChildren(QAbstractButton):
                siblings.append(child)
        return siblings

    def setRadioButtonData(self, button, index):
        modelVal = py(index.data(Qt.EditRole))
        for child in self.collectButtonSiblings(button):
            buttonVal = py(child.property('buttonValue'))
            child.setChecked(buttonVal == modelVal)

    def getRadioButtonData(self, button):
        for child in  self.collectButtonSiblings(button):
            if child.isChecked():
                return child.property('buttonValue')

    def setEditorData(self, editor, index):

        if isinstance(editor, QComboBox):
            modelData = py(index.data(Qt.EditRole))

            strictCompare = not isinstance(modelData, (basestring, int, float))

            for i in range(editor.count()):
                editorData = py(editor.itemData(i, self._itemsModelRole))

                if strictCompare:
                    if modelData is editorData:
                        editor.setCurrentIndex(i)
                        return None
                else:
                    if modelData == editorData:
                        editor.setCurrentIndex(i)
                        return None

        elif isinstance(editor, QAbstractButton):
            if isinstance(self.xType.itemType, BoolType):
                editor.setChecked(py(index.data(Qt.EditRole)))
                return None
            else:
                if not editor.property('buttonValue').isNull():
                    self.setRadioButtonData(editor, index)
                    return None
                else:
                    print editor
                    raise ValueError("Every Button mapped has to have a buttonValue property")

        return XTypeDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            value = editor.itemData(editor.currentIndex(), self._itemsModelRole)
            model.setData(index, value, Qt.EditRole)
            return None
        elif isinstance(editor, QAbstractButton):
            if isinstance(self.xType.itemType, BoolType):
                model.setData(index, QVariant(editor.isChecked()), Qt.EditRole)
                return None
            else:
                model.setData(index, self.getRadioButtonData(editor))
                return
        return XTypeDelegate.setModelData(self, editor, model, index)

