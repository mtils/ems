'''
Created on 22.03.2012

@author: michi
'''
from PyQt4.QtCore import QString, Qt, QAbstractListModel, QAbstractItemModel
from PyQt4.QtCore import QVariant, pyqtSignal
from PyQt4.QtGui import QComboBox, QAbstractButton, QLineEdit

from ems.xtype.base import XType, NumberType, BoolType, StringType, ComplexType
from ems.qt4.gui.itemdelegate.xtypedelegate import XTypeDelegate #@UnresolvedImport
from ems.qt4.util import variant_to_pyobject
from ems.qt4.itemmodel.xtype.oneofalistmodel import OneOfAListModel #@UnresolvedImport

class StringComboboxDelegate(XTypeDelegate):

    currentRowChanged = pyqtSignal(int)

    def __init__(self, xType, parent=None):
        XTypeDelegate.__init__(self, xType, parent)
        self._model = None
        self._itemsModelRole = Qt.UserRole

        self._connectedWidget = None
        self._currentRow = 0
        self._connectedColumn = None
        self._connectedModel = None

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

    def getConnectedWidget(self):
        return self._connectedWidget

    def setConnectedWidget(self, widget, model, column):

        if not isinstance(widget, QComboBox):
            raise TypeError('Widget has to be QComboBox')

        self._connectedWidget = widget
        self._connectedWidget.lineEdit().editingFinished.connect(self.updateModelByEditor)
        self._connectedModel = model
        self._connectedModel.dataChanged.connect(self.updateEditorByModel)
        self._connectedModel.modelReset.connect(self.updateEditorByModel)
        self._connectedColumn = column
        self.updateEditorByModel()

    def updateModelByEditor(self):
        text = self._connectedWidget.lineEdit().text()
        index = self._connectedModel.index(self._currentRow, self._connectedColumn)
        self._connectedModel.setData(index, QVariant(text), Qt.EditRole)

    def getCurrentRow(self):
        return self._currentRow

    def setCurrentRow(self, row):
        if self._currentRow == row:
            return
        self._currentRow = row

        self.currentRowChanged.emit(self._currentRow)
        self.updateEditorByModel()

    currentRow = property(getCurrentRow, setCurrentRow)

    def _onConnectedModelChanged(self, fromIndex, toIndex):

        if self._connectedColumn not in range(fromIndex.column(), toIndex.column()):
            return

        self.updateEditorByModel()

    def updateEditorByModel(self):
        index = self._connectedModel.index(self._currentRow, self._connectedColumn)
        text = variant_to_pyobject(index.data(Qt.EditRole))
        try:
            self._connectedWidget.lineEdit().setText(QString.fromUtf8(text))
        except RuntimeError: # Happens if the _connectedWidget is destroyed
            return


