
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, pyqtSlot, QByteArray
from PyQt5.QtCore import pyqtSignal, QDateTime, QDate, pyqtProperty

from ems.typehint import accepts
from ems.event.hook import EventHook
from ems.qt5.itemmodel.search_model import SearchModel
from ems.search.base import Search
from ems.resource.repository import Repository

class SequenceColumnModel(SearchModel):

    currentRowChanged = pyqtSignal(int)

    sourceColumnChanged = pyqtSignal(int)

    @accepts(Repository, QAbstractTableModel)
    def __init__(self, itemRepository, parentModel):

        search = SequenceColumnSearch(parentModel)

        super().__init__(search)
        self._parentModel = parentModel
        self._currentRow = -1
        self._sourceColumn = -1
        self._itemRepository = itemRepository
        self.appended = EventHook()

        self.currentRowChanged.connect(self.refill)

    @property
    def search(self):
        return self._search

    def parentModel(self):
        return self._parentModel

    def setParentModel(self, parentModel):
        self._parentModel = parentModel

    def getCurrentRow(self):
        return self._currentRow

    def setCurrentRow(self, row):
        if self._currentRow == row:
            return
        self._currentRow = row
        self._search.setCurrentRow(row)
        self.currentRowChanged.emit(self._currentRow)

    currentRow = pyqtProperty(int, getCurrentRow, setCurrentRow, notify=currentRowChanged)

    def getSourceColumn(self):
        return self._sourceColumn

    def setSourceColumn(self, column):
        self._sourceColumn = column
        self._search.setSourceColumn(column)

    sourceColumn = pyqtProperty(int, getSourceColumn, setSourceColumn)

class CurrentRowColumnMixin(object):

    def __init__(self, parentModel, *args, **kwargs):
        self._parentModel = parentModel
        self._sourceColumn = -1
        self._currentRow = -1
        self.sourceColumnChanged = EventHook()
        self.currentRowChanged = EventHook()

    def getCurrentRow(self):
        return self._currentRow

    def setCurrentRow(self, row):
        if self._currentRow == row:
            return
        self._currentRow = row
        self.currentRowChanged.fire(self._currentRow)

    currentRow = property(getCurrentRow, setCurrentRow)

    def getSourceColumn(self):
        return self._sourceColumn

    def setSourceColumn(self, column):
        if self._sourceColumn == column:
            return
        self._sourceColumn = column
        self.sourceColumnChanged.fire(self._sourceColumn)

    sourceColumn = property(getSourceColumn, setSourceColumn)

    def _itemsIndex(self):
        return self._parentModel.index(self.currentRow, self.sourceColumn)

class SequenceColumnSearch(Search, CurrentRowColumnMixin):

    def __init__(self, parentModel):
        CurrentRowColumnMixin.__init__(self, parentModel)
        super().__init__(parentModel)

    def all(self):
        index = self._itemsIndex()
        items = self._itemsIndex().data(Qt.EditRole)
        print("SequenceColumnSearch.all()", items)
        return [] if items is None else items

class SequenceColumnRepository(Repository, CurrentRowColumnMixin):
    """
    This repository acts as an repository which database store is
    the list property of one parent item
    so all methods here apply to one item inside the list of a property
    new() would create an item in that list
    store() stores one item in that list
    """
    def __init__(self, parentModel, modelRepository, idKey):
        super().__init__(parentModel)
        self._modelRepository = modelRepository
        self._idKey = idKey

    def get(self, id_):
        return self._findItemByModelId(id_)

    def new(self, attributes):
        return self._modelRepository.new(attributes)

    def store(self, attributes, obj=None):
        obj = self.new(attributes) if obj is None else obj
        items = self._getItemsFromModel()
        items.append(obj)
        self._writeItemsToModel(items)

    def update(self, model, changedAttributes):
        for key, val in changedAttributes:
            setattr(model, key, val)

    def delete(self, model):
        items = self._getItemsFromModel()
        items.remove(model)
        self._writeItemsToModel(items)

    def _findItemByModelId(self, modelId):
        for item in self._getItemsFromModel():
            if getattr(item, self._idKey) == modelId:
                return item

    def _findItemByModelId(self, modelId):
        for item in self._getItemsFromModel():
            if getattr(item, self._idKey) == modelId:
                return item

    def _getItemsFromModel(self):
        return self._itemsIndex().data(Qt.EditRole)

    def _writeItemsToModel(self, items):
        self._parentModel.setData(self._itemsIndex(), items)