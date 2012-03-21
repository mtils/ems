'''
Created on 20.03.2012

@author: michi
'''

from PyQt4.QtCore import QObject, QAbstractItemModel
from PyQt4.QtGui import QDataWidgetMapper

from ems.thirdparty.singletonmixin import Singleton
from ems.qt4.gui.itemdelegate.mapper import MapperItemViewDelegate #@UnresolvedImport


class BaseStrategy(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
    
    def getEditor(self, mapper, type_, parent=None):
        raise NotImplementedError()
        
    def getDelegateForItem(self, mapper, type_, parent=None):
        raise NotImplementedError()
    
    def addMapping(self, mapper, widget, propertyName, type_):
        raise NotImplementedError()
    
    def match(self, param):
        raise NotImplementedError()   

class MapperInterfaceMixin(object):
    def _init(self):
        self._strategies = []
    
    def getStrategy(self, type_):
        for strategy in self._strategies:
            if strategy.match(type_):
                return strategy
            
    def getStrategies(self, type_=None):
        if type_ is None:
            return self._strategies
        
        strategies = []
        for strategy in self._strategies:
            if strategy.match(type_):
                strategies.append(strategy)
        return strategies
    
    def addStrategy(self, strategy):
        if not isinstance(strategy, BaseStrategy):
            raise TypeError("strategy has to be instance of BaseStrategy")
        self._strategies.insert(0, strategy)
    
    def hasStrategyForType(self, type_):
        return isinstance(self.getStrategy(type_),BaseStrategy)        

class MapperDefaults(Singleton, MapperInterfaceMixin):
    def __init__(self):
        MapperInterfaceMixin._init(self)

class BaseMapper(QObject, MapperInterfaceMixin):
    def __init__(self, model=None, parent=None):
        QObject.__init__(self, parent)
        MapperInterfaceMixin._init(self)
        self._defaults = MapperDefaults.getInstance()
        self._dataWidgetMapper = None
        self._dataWidgetMapperDelegate = None
        self._mappings = {}
        self._hashToType = {}
        self._model = model
    
    @property
    def dataWidgetMapper(self):
        if not isinstance(self._dataWidgetMapper, QDataWidgetMapper):
            self._dataWidgetMapper = QDataWidgetMapper(self)
            self._dataWidgetMapper.setModel(self.model)
            itemDelegate = MapperItemViewDelegate(self, self._dataWidgetMapper)
            self._dataWidgetMapper.setItemDelegate(itemDelegate)
        return self._dataWidgetMapper
    
    def getModel(self):
        return self._model
    
    def setModel(self, model):
        if not isinstance(model, QAbstractItemModel):
            raise TypeError("Model has to be instanceof AbstractItemModel")
        self._model = model
        if isinstance(self._dataWidgetMapper,QDataWidgetMapper):
            self._dataWidgetMapper.setModel(model)
        
    model = property(getModel, setModel)
    
    def getDelegateForItemView(self, parent=None):
        return MapperItemViewDelegate(self, parent)
    
    def getDelegateForItem(self, type_,  parent=None):
        strategy = self.getStrategy(type_)
        return strategy.getDelegateForItem(self, type_, parent)
    
    def getEditor(self, propertyName, parent=None):
        type_ = self._getTypeOfPropertyName(propertyName)
        strategy = self.getStrategy(type_)
        return strategy.getEditor(self, type_, parent)
    
    def _getTypeOfPropertyName(self, propertyName):
        return self._model.columnType(propertyName)
        
    def addMapping(self, widget, propertyName):
        if not isinstance(self._model, QAbstractItemModel):
            raise TypeError("Assign a QAbstractItemModel prior to addMapping")
        
        type_ = self._getTypeOfPropertyName(propertyName)
        strategy = self.getStrategy(type_)
        return strategy.addMapping(self, widget, propertyName, type_)