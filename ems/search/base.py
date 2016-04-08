
from collections import OrderedDict
from abc import ABCMeta, abstractmethod

from six import add_metaclass

from ems.event.hook import EventHookProperty


AND = 'and'
OR = 'or'
ASC = 'asc'
DESC = 'desc'

def parseWhere(key, operator=None, value=None, boolean=AND):

    if value is not None:
        return (key, operator, value, boolean)

    if isinstance(operator, (list, set, tuple)):
        return (key, 'in', operator, boolean)

    return (key, '=', operator, boolean)

@add_metaclass(ABCMeta)
class Queryable(object):

    @abstractmethod
    def where(self, key, operator=None, value=None, boolean=AND):
        """
        Add an expression to this Queryable. If no operator is passed, the
        operator will be = and the passed operator is the value:
        where('foo', 'bar') -> foo == bar
        If you pass a tuple, list or set as an operator is considered as in:
        where('foo', ('a','b')) -> foo IN ('a','b')
        """
        return self

class Sortable(object):

    def __init__(self):
        self._sorting = OrderedDict()

    @property
    def sorting(self):
        return self._sorting

    def sort(self, key, direction='asc'):
        self._sorting[key] = direction
        return self

    def removeSort(self, key):
        del self._sorting[key]
        return self

class HoldsKeys(object):

    def __init__(self):
        self._keys = []

    def withKey(self, *args):
        self._keys = self._keys + list(args)
        return self

    @property
    def keys(self):
        return self._keys

    def removeKey(self, key):
        self._keys.remove(key)
        return self

    def replaceKeys(self, *args):
        self._keys = args

class Expression(Queryable):

    def __init__(self, key=None, operator=None, value=None, boolean=AND):
        self.key = None
        self.operator = None
        self.value = None
        self.boolean = None
        if key is not None:
            self.where(key, operator, value, boolean)

    def where(self, key, operator=None, value=None, boolean=AND):

        key, operator, value, boolean = parseWhere(key, operator, value, boolean)

        self.key = key
        self.operator = operator
        self.value = value
        self.boolean = boolean

        return self

    def __repr__(self):
        return "<Expression: {0} {1} {2} ({3})>".format(self.key, self.operator, self.value, self.boolean)

class Filter(Queryable):

    def __init__(self, expressionCreator=None):
        self._expressions = []
        self._expressionCreator = expressionCreator if expressionCreator else Expression

    def append(self, expression):
        self._expressions.append(expression)
        return self

    def remove(self, expression):
        self._expressions.remove(expression)
        return self

    def index(self, expression):
        return self._expressions.index(expression)

    def clear(self):
        self._expressions = []

    def __len__(self):
        return len(self._expressions)

    def __iter__(self):
        return iter(self._expressions)

    def where(self, key, operator=None, value=None, boolean=AND):

        expression = self._expressionCreator()
        expression.where(key, operator, value, boolean)
        self.append(expression)
        return self

class Criteria(Queryable, Sortable):

    def __init__(self, filter=None):
        self._modelClass = None
        self._filter = filter if filter else Filter()
        super().__init__()

    def getModelClass(self):
        return self._modelClass

    def setModelClass(self, modelClass):
        self._modelClass = modelClass

    modelClass = property(getModelClass, setModelClass)

    def getFilter(self):
        return self._filter

    def setFilter(self, filter):
        self._filter = filter

    filter = property(getFilter, setFilter)

    def where(self, key, operator=None, value=None, boolean=AND):
        self._filter.where(key, operator, value, boolean)
        return self

@add_metaclass(ABCMeta)
class Search(Queryable, HoldsKeys):

    searching = EventHookProperty()
    '''
    This event is fired before a search will be performed. The signature
    is: searching(self)
    Subscribers than can modify the Search object
    '''

    searched = EventHookProperty()
    '''
    This event is fired after a search was performed. Signature is:
    searched(self, result)
    '''

    querying = EventHookProperty()
    '''
    This will be fired with the backend dependent native query object.
    For example a sqlalchemy query object. Signature is:
    querying(self, query).
    First searching is fired, after that querying
    '''

    def __init__(self, criteria=None):
        self._criteria = criteria if criteria else Criteria()
        super(Search, self).__init__()

    @abstractmethod
    def all(self):
        pass

    @property
    def modelClass(self):
        return self._criteria.modelClass

    @property
    def criteria(self):
        return self._criteria

    def where(self, key, operator=None, value=None, boolean=AND):
         return self._criteria.where(key, operator, value, boolean)

    @property
    def sorting(self):
        return self._criteria.sorting

    def sort(self, key, direction='asc'):
        self._criteria.sort(key, direction)
        return self

    def removeSort(self, key):
        self._criteria.removeSort(key)
        return self

if __name__ == '__main__':

    class SearchTest(Search):
        def all(self):
            return []

    s = SearchTest()
    s.where('a','b').where('c','>=','d').where('e', ('a','b','c')).sort('a')
    print(list(s.criteria.filter))
    print(s.sorting)