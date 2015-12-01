
from sqlalchemy.inspection import inspect

class ToManySynchronizer(object):

    def __init__(self, relation):
        self._relationKey = relation.key
        self._relationClass = relation.class_
        self._mapper = relation.parent
        self._property = self._mapper.get_property(self._relationKey)
        self._foreignClass = self._property.mapper.class_
        self._primaryKey = inspect(self._foreignClass).primary_key[0].key

        #print(relation, type(relation), relation.key, relation.class_)

        #print(self._property, type(self._property), self._foreignClass, self._primaryKey)
        #print(dir(self._property))
        #for prop in self._mapper.iterate_properties:
            #print(prop, type(prop))

    def syncRelation(self, model, dictData):

        dictIds = self._collectDictItemIds(dictData)
        items = getattr(model, self._relationKey)
        self._deleteMissingItems(items, dictIds)
        self._updateExistingItems(items, dictData)
        self._createNewItems(items, dictData)

    def _deleteMissingItems(self, items, dictIds):

        key = self._primaryKey

        deletes = []
        for item in items:
            if getattr(item, key) not in dictIds:
                deletes.append(item)

        for item in deletes:
            items.remove(item)

    def _updateExistingItems(self, items, itemsDict):

        key = self._primaryKey

        itemsById = self._itemsById(items)

        for itemDict in itemsDict:

            if key not in itemDict or itemDict[key] is None:
                continue

            if not itemDict[key] in itemsById:
                continue

            note = itemsById[itemDict[key]]

            for dictKey, value in itemDict.items():
                if value != getattr(note, dictKey):
                    setattr(note, dictKey, value)

    def _createNewItems(self, items, itemsDict):

        key = self._primaryKey

        for itemDict in itemsDict:
            if key in itemDict and itemDict[key] is not None:
                continue
            items.append(self._foreignClass(**itemDict))

    def _collectDictItemIds(self, items):
        key = self._primaryKey
        return [item[key] for item in items if key in item and item[key] is not None]

    def _itemsById(self, items):
        byId = {}
        key = self._primaryKey
        for item in items:
            byId[getattr(item, key)] = item
        return byId