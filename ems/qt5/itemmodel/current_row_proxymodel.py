
from PyQt5.QtCore import QModelIndex, Qt, pyqtSignal, pyqtProperty, pyqtSlot
from PyQt5.QtCore import QAbstractItemModel
from ems.qt5.itemmodel.full_proxymodel import FullProxyModel

class CurrentRowProxyModel(FullProxyModel):

    currentRowChanged = pyqtSignal(int)
    isValidChanged = pyqtSignal(bool)

    hasPreviousChanged = pyqtSignal(bool)
    hasNextChanged = pyqtSignal(bool)

    parentModelChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._currentRow = -1
        self._queueRowInsert = False
        self.__isValid = False
        self.__hasNext = False
        self.__hasPrevious = False
        self.currentRowChanged.connect(self._emitRowChangeSignals)
        self.currentRowChanged.connect(self._updatePreviousAndNextStates)
        self.currentRowChanged.connect(self._checkValid)
        self.sourceModelChanged.connect(self.parentModelChanged)

    def getCurrentRow(self):
        return self._currentRow

    def setCurrentRow(self, currentRow):
        if not self._isRowValid(currentRow):
            currentRow = -1

        if self._currentRow == currentRow:
            return

        if self._currentRow == -1 and currentRow >= 0:
            self._queueRowInsert = True

        self._currentRow = currentRow
        self.currentRowChanged.emit(self._currentRow)

    currentRow = pyqtProperty(int, getCurrentRow, setCurrentRow, notify=currentRowChanged)

    def getValid(self):
        return self.__isValid

    def _setValid(self, valid):
        if self.__isValid == valid:
            return
        self.__isValid = valid

        self.isValidChanged.emit(self.__isValid)

    isValid = pyqtProperty(bool, getValid, notify=isValidChanged)

    def getHasPrevious(self):
        return self._isRowValid(self.currentRow) and self.currentRow > 0

    def _setHasPrevious(self, hasPrevious):
        if self.__hasPrevious == hasPrevious:
            return
        self.__hasPrevious = hasPrevious
        self.hasPreviousChanged.emit(self.__hasPrevious)

    hasPrevious = pyqtProperty(bool, getHasPrevious, notify=hasPreviousChanged)

    def getHasNext(self):
        return self._isRowValid(self.currentRow) and \
            self.currentRow < (self.sourceModel().rowCount()-1)

    def _setHasNext(self, hasNext):
        if self.__hasNext == hasNext:
            return
        self.__hasNext = hasNext
        self.hasNextChanged.emit(self.__hasNext)

    hasNext = pyqtProperty(bool, getHasNext, notify=hasNextChanged)

    @pyqtSlot(result=bool)
    def previous(self):

        previous = self.currentRow - 1
        if not self._isRowValid(previous):
            return False

        self.currentRow = previous

        return True

    @pyqtSlot(result=bool)
    def next(self):

        next_ = self.currentRow + 1

        if not self._isRowValid(next_):
            return False

        self.currentRow = next_
        return True

    def setSourceModel(self, sourceModel):

        if sourceModel is None:
            return

        result = super().setSourceModel(sourceModel)

        if self.currentRow >= 0:
            self._updatePreviousAndNextStates()

        self._checkValid()

        sourceModel.modelReset.connect(self._resetState)

        return result

    def getParentModel(self):
        return self.sourceModel()

    parentModel = pyqtProperty(QAbstractItemModel, getParentModel, setSourceModel, notify=parentModelChanged)

    def rowCount(self, parentIndex=QModelIndex()):
        if self._currentRow < 0 or not self.sourceModel():
            return 0

        return int(self.sourceModel().rowCount() > 0)

    def mapFromSource(self, sourceIndex):
        if sourceIndex.row() != self.currentRow:
            return QModelIndex()
        return self.index(0, sourceIndex.column())

    def mapToSource(self, proxyIndex):
        if proxyIndex.row() != 0:
            return QModelIndex()
        return self.sourceModel().index(self.currentRow, proxyIndex.column())

    def onSourceModelRowsInserted(self, parentIndex, start, end):
        self._resetState()
        if start > self.currentRow or end < self.currentRow:
            return
        self.beginInsertRows(parentIndex, start, end)
        self.endInsertRows()

    def onSourceModelRowsDeleted(self, parentIndex, start, end):

        if self._invalidateIfCurrentIndexInvalid():
            self._resetState()
            return

        if start > self.currentRow or end < self.currentRow:
            self._resetState()
            return

        self.currentRow = -1

    def onDataChanged(self, fromIndex, toIndex):
        if self._currentRow == -1:
            return

        if fromIndex.row() < self.currentRow or toIndex.row() > self.currentRow:
            return

        self.dataChanged.emit(self.index(0, fromIndex.column()),
                              self.index(0, toIndex.column()))


    @pyqtSlot(str, 'QVariant', result='QVariant')
    def findRow(self, key, value):

        sourceModel = self.sourceModel()
        if not sourceModel:
            return -1

        for i in range(sourceModel.rowCount()):
            data = sourceModel.get(i)
            if data[key] == value:
                return i

        return -1

    def _emitRowChangeSignals(self, currentRow):

        if currentRow == -1:
            self.modelReset.emit()
            return

        if self._queueRowInsert:
            self._queueRowInsert = False
            self.beginInsertRows(QModelIndex(), 0, 0)
            self.endInsertRows()

        self.dataChanged.emit(self.index(0, 0),
                              self.index(0, self.columnCount()-1))

    def _updatePreviousAndNextStates(self, currentRow):

        if not self._isRowValid(currentRow):
            self._setHasPrevious(False)
            self._setHasNext(False)
            return

        self._setHasPrevious(currentRow > 0)
        self._setHasNext(currentRow < (self.sourceModel().rowCount()-1))

    def _invalidateIfCurrentIndexInvalid(self):

        if not self._isRowValid(self.currentRow):
            self.currentRow = -1
            return True
        return False

    def _isRowValid(self, row):

        if not self.sourceModel():
            return False

        return (row <= (self.sourceModel().rowCount()-1) and row != -1)

    def _resetState(self):
        self._updatePreviousAndNextStates(self.currentRow)
        self._checkValid()

    def _checkValid(self, *args):
        self._setValid(self._isRowValid(self.currentRow))