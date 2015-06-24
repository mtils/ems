
from PyQt4.QtCore import Qt, QVariant, pyqtSignal
from PyQt4.QtGui import QStyledItemDelegate, QComboBox, QAbstractButton, QRadioButton

from ems.qt4.util import variant_to_pyobject as py

class ButtonGroupDelegate(QStyledItemDelegate):

    columnChanged = pyqtSignal(int)

    currentRowChanged = pyqtSignal(int)

    def __init__(self, buttonGroup, model, column, parent=None):

        QStyledItemDelegate.__init__(self, parent)

        self._buttonGroup = None
        self._model = None
        self._column = 0
        self._currentRow = 0

        self.trueButton = None

        self.buttonGroup = buttonGroup
        self.model = model
        self.column = column

        self.currentRowChanged.connect(self.updateButtons)
        self.columnChanged.connect(self.updateButtons)

        self.updateButtons()

    def getButtonGroup(self):
        return self._buttonGroup

    def setButtonGroup(self, buttonGroup):
        self.delButtonGroup()
        self._checkButtons(buttonGroup.buttons())
        self._buttonGroup = buttonGroup
        self._buttonGroup.buttonClicked.connect(self.updateModel)

    def delButtonGroup(self):
        if not self._buttonGroup:
            return
        self._buttonGroup.disconnect(self.updateModel)
        self._buttonGroup = None

    buttonGroup = property(getButtonGroup, setButtonGroup, delButtonGroup)

    def getModel(self):
        return self._model

    def setModel(self, model):
        self.delModel()
        self._model = model
        self._model.dataChanged.connect(self.onModelChanged)

    def delModel(self):
        if not self._model:
            return
        self._model.disconnect(self.onModelChanged)

    model = property(getModel, setModel, delModel)

    def getColumn(self):
        return self._column

    def setColumn(self, column):
        if column == self._column:
            return
        self._column = column
        self.columnChanged.emit(self._column)

    column = property(getColumn, setColumn)

    def getCurrentRow(self):
        return self._currentRow

    def setCurrentRow(self, row):
        if row == self._currentRow:
            return
        self._currentRow = row
        self.currentRowChanged.emit(row)

    currentRow = property(getCurrentRow, setCurrentRow)

    def _checkButtons(self, buttons):
        for button in buttons:
            if button.property('buttonValue').isValid():
                continue
            raise RuntimeError('Every button in a buttongroup you want to map has to have a property "buttonValue"')


    def setCurrentModelData(self, currentIndex=0):
        modelData = py(self.getModelIndex().data())
        self.setButtonValue(modelData)

    def getButtonGroupValue(self):
        for button in self._buttonGroup.buttons():
            if button.isChecked():
                return py(button.property('buttonValue'))

        return None

    def getModelIndex(self):
        return self._model.index(self.currentRow, self.column, Qt.EditRole)

    def updateModel(self, *args, **kwargs):

        newValue = self.getButtonGroupValue()
        index = self.getModelIndex()
        oldValue = py(index.data(Qt.EditRole))

        if newValue == oldValue:
            return

        self._model.setData(index, QVariant(newValue))

    def updateButtons(self):

        index = self.getModelIndex()
        newValue = py(index.data(Qt.EditRole))

        if newValue == self.getButtonGroupValue():
            return

        self.setButtonValue(newValue)

    def onModelChanged(self, fromIndex, toIndex):

        if not self._currentRow in range(fromIndex.row(), toIndex.row()+1):
            return

        if not self._column in range(fromIndex.column(), toIndex.column()+1):
            return

        self.updateButtons()

    def setButtonValue(self, value):

        for button in self._buttonGroup.buttons():
            button.setChecked(py(button.property("buttonValue")) == value)



    def setEditorData(self, editor, index):
        self.setButtonValue(py(index.data(Qt.EditRole)))

    def setModelData(self, editor, model, index):
        model.setData(index, QVariant(self.getButtonGroupValue()))
