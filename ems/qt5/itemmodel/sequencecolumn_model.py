
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
    def __init__(self, itemRepository, parentModel, idKey='id'):

        search = SequenceColumnSearch(parentModel)
        repository = SequenceColumnRepository(parentModel, itemRepository, idKey)

        super().__init__(search, repository)
        self._parentModel = None
        self.setParentModel(parentModel)
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
        self._parentModel.dataChanged.connect(self._onParentModelDataChanged)

    def getCurrentRow(self):
        return self._currentRow

    def setCurrentRow(self, row):
        if self._currentRow == row:
            return
        self._currentRow = row
        self._search.setCurrentRow(row)
        self._repository.setCurrentRow(row)
        self.currentRowChanged.emit(self._currentRow)

    currentRow = pyqtProperty(int, getCurrentRow, setCurrentRow, notify=currentRowChanged)

    def getSourceColumn(self):
        return self._sourceColumn

    def setSourceColumn(self, column):
        if self._sourceColumn == column:
            return
        self._sourceColumn = column
        self._search.setSourceColumn(column)
        self._repository.setSourceColumn(column)
        self.sourceColumnChanged.emit(self._sourceColumn)

    sourceColumn = pyqtProperty(int, getSourceColumn, setSourceColumn)

    def _onParentModelDataChanged(self, topLeft, bottomRight):

        if self.currentRow < topLeft.row() or self.currentRow > bottomRight.row():
            return

        if self.sourceColumn < topLeft.column() or self.sourceColumn > bottomRight.column():
            return

        if self._isInSubmit:
            return

        self.refill()

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
        #print("SequenceColumnSearch.all()", type(items), items)
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

    def new(self, attributes=None):
        return self._modelRepository.new(attributes)

    def store(self, attributes, obj=None):
        #print("receiving", obj.__dict__, attributes)
        obj = self.new(attributes) if obj is None else self._fill(obj, attributes)
        #print("after self.new", obj.__dict__)
        items = self._getItemsFromModel()
        items.append(obj)
        #print("storing:", items)
        #for item in items:
            #print("writing", item.__dict__)
        self._writeItemsToModel(items)

    def update(self, model, changedAttributes):

        items = self._getItemsFromModel()
        for key, val in changedAttributes.items():
            setattr(model, key, val)
        # force dataChanged
        self._writeItemsToModel(items)

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

    def _fill(self, ormObject, attributes):
        for key in attributes:
            setattr(ormObject, key, attributes[key])
        return ormObject
    def _getItemsFromModel(self):
        items = self._itemsIndex().data(Qt.EditRole)
        return [] if items is None else items

    def _writeItemsToModel(self, items):
        self._parentModel.setData(self._itemsIndex(), items)