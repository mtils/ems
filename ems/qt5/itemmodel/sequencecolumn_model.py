
from PyQt5.QtCore import QAbstractItemModel, Qt, QModelIndex, pyqtSlot, QByteArray
from PyQt5.QtCore import pyqtSignal, QDateTime, QDate, pyqtProperty

from ems.typehint import accepts
from ems.event.hook import EventHook
from ems.qt5.itemmodel.search_model import SearchModel
from ems.search.base import Search
from ems.resource.repository import Repository

class SequenceColumnModel(SearchModel):
    """
    The SequenceColumnModel is like an proxy model. If you have a model property
    which holds non-scalar data like a relation (a list, set, tuple , called
    sequence here) you cannot simply put that relations in a qt view (widgets or qml)
    So this model comes in and acts a little like the DataWidgetMapper.

    Give it a sourceColumn and a currentRow and it will behave like an own model
    for the (scalable) data of this single value.

    In some sense this will get nasty complicated, because I think it is where
    important to let the datastore untouched until the model is submitted.
    If you write directly to your database models or relation properties this
    is not the case.
    So the model will write to its parent model through ModelBuffer objects,
    which are basically dicts and the related models are all untouched.

    If you submit this model, it will call parentModel.setData, which is only
    a submit to its parentModel and not to the dataStore.
    If you submit the parentModel, the changed Data is an dict with all 
    items of that model. Your repository than have to care about syncing the
    passed array with the relation.

    Why oh why so complicated? Please let me write directly to the related 
    models.

    No ;-)

    Sqlalchemy for example can handle all sorts of nested relation updating,
    but you couldnt send our plain orm objects through a http request.
    And because the repositories and the most other parts shouldnt depend of
    whatever your datastore or the client is, cast to dicts and back.

    Repositories which accept dicts are very good to test because they have
    no hard dependencies to the outer world.

    The same is with validation. Validate an array of data, not the models after
    setting their state. This is to late.
    """

    currentRowChanged = pyqtSignal(int)

    sourceColumnChanged = pyqtSignal(int)

    @accepts(Repository, QAbstractItemModel)
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

    @pyqtSlot()
    def submit(self):
        self._needsRefill = super().submit()
        return self._needsRefill

    def _onParentModelDataChanged(self, topLeft, bottomRight):

        if self.currentRow < topLeft.row() or self.currentRow > bottomRight.row():
            return

        if self.sourceColumn < topLeft.column() or self.sourceColumn > bottomRight.column():
            return

        if self._isInSubmit:
            return

        self.refill()

    def _extractValue(self, currentObj, key):

        if not isinstance(currentObj, dict):
            return super()._extractValue(currentObj, key)

        if key in currentObj:
            return currentObj[key]

        #if hasattr(currentObj, key):
            #return currentObj.__getattribute__(key)

        #elif key.find('.'):
            #stack = key.split('.')
            #value = self._extractValueRecursive(currentObj, stack)
            #if value is not None:
                #return value

        return None

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
        obj = self.new(attributes) if obj is None else self._fill(obj, attributes)

        objData = self._modelToDict(obj)

        items = self._getItemsFromModel()
        items.append(objData)

        self._writeItemsToModel(items)

    def update(self, model, changedAttributes):

        objId = id(model)
        items = self._getItemsFromModel()
        modelDict = self._findModelEntry(model, items)

        for key, val in changedAttributes.items():
            modelDict[key] = val

        self._writeItemsToModel(items)

    def delete(self, model):

        items = self._getItemsFromModel()
        items.remove(self._findModelEntry(model, items))
        self._writeItemsToModel(items)

    def _findItemByModelId(self, modelId):
        for item in self._getItemsFromModel():
            if getattr(item, self._idKey) == modelId:
                return item

    def _findItemByModelId(self, modelId):
        for item in self._getItemsFromModel():
            if getattr(item, self._idKey) == modelId:
                return item

    def _modelToDict(self, model):

        modelData = ModelBuffer()
        modelData.modelId = id(model)

        for key, value in model.__dict__.items():
            if key[0] == '_':
                continue
            modelData[key] = value

        return modelData

    def _fill(self, ormObject, attributes):
        for key in attributes:
            setattr(ormObject, key, attributes[key])
        return ormObject

    def _getItemsFromModel(self):
        items = self._itemsIndex().data(Qt.EditRole)
        items = [] if items is None else items

        dictItems = []
        for obj in items:
            if isinstance(obj, ModelBuffer):
                dictItems.append(obj)
                continue
            dictItems.append(self._modelToDict(obj))

        return dictItems

    def _writeItemsToModel(self, items):
        self._parentModel.setData(self._itemsIndex(), items)

    def _findModelEntry(self, model, modelAsDicts):

        modelId = model.modelId if isinstance(model, ModelBuffer) else id(model)
        for modelDict in modelAsDicts:
            if modelDict.modelId == modelId:
                return modelDict

class ModelBuffer(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modelId = None