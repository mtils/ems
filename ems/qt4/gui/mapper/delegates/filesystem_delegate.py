
from PyQt4.QtCore import Qt, QVariant, pyqtSignal
from PyQt4.QtGui import QStyledItemDelegate, QComboBox, QAbstractButton, QRadioButton

from ems.qt4.util import variant_to_pyobject as py
from ems.qt4.gui.inputs.filesystem import FileSelect

class FileInputDelegate(QStyledItemDelegate):

    columnChanged = pyqtSignal(int)

    currentRowChanged = pyqtSignal(int)

    def __init__(self, fileInput, model, column, parent=None):

        QStyledItemDelegate.__init__(self, parent)

        self._fileInput = None
        self._model = None
        self._column = 0
        self._currentRow = 0

        self.trueButton = None

        self.fileInput = fileInput
        self.model = model
        self.column = column

        self.currentRowChanged.connect(self.updateInput)
        self.columnChanged.connect(self.updateInput)

        self.updateInput()

    def getFileInput(self):
        return self._fileInput

    def setFileInput(self, fileInput):
        self.delFileInput()
        self._fileInput = fileInput
        self._fileInput.pathChanged.connect(self.updateModel)

    def delFileInput(self):
        if not self._fileInput:
            return
        self._fileInput.pathChanged.disconnect(self.updateModel)
        self._fileInput = None

    fileInput = property(getFileInput, setFileInput, delFileInput)

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

    def getModelIndex(self):
        return self._model.index(self.currentRow, self.column, Qt.EditRole)

    def updateModel(self, path):

        index = self.getModelIndex()
        oldPath = py(index.data(Qt.EditRole))

        if path == oldPath:
            return

        self._model.setData(index, QVariant(path))

    def updateInput(self):

        index = self.getModelIndex()
        path = py(index.data(Qt.EditRole))

        self._fileInput.setPath(path)

    def onModelChanged(self, fromIndex, toIndex):

        if not self._currentRow in range(fromIndex.row(), toIndex.row()+1):
            return

        if not self._column in range(fromIndex.column(), toIndex.column()+1):
            return

        self.updateInput()

    def setEditorData(self, editor, index):
        self._fileInput.setPath(py(index.data(Qt.EditRole)))

    def setModelData(self, editor, model, index):
        model.setData(index, QVariant(self._fileInput.path))

    def createEditor(self, parent, option, index):
        return FileSelect(parent=parent)