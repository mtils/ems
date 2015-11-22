
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, pyqtSlot, QByteArray
from PyQt5.QtCore import pyqtSignal, QDateTime, QDate, pyqtProperty

class ListSubModel(QAbstractTableModel):

    currentIndexChanged = pyqtSignal(int)

    sourceColumnChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._parentModel = None
        self._currentIndex = -1
        self._sourceColumn = -1

    def parentModel(self):
        return self._parentModel

    def setParentModel(self, parentModel):
        self._parentModel = parentModel

    @pyqtProperty(int, notify=currentIndexChanged)
    def currentIndex(self):
        return self._currentIndex

    @currentIndex.setter
    def currentIndex(self, index):
        if self._currentIndex == index:
            return
        self._currentIndex = index
        self.currentIndexChanged.emit(self._currentIndex)

    @pyqtProperty
    def sourceColumn(self):
        return self._sourceColumn

    @sourceColumn.setter
    def sourceColumn(self, column):
        self._sourceColumn = column