'''
Created on 20.03.2012

@author: michi
'''

from PyQt4.QtCore import QObject
from PyQt4.QtGui import QDataWidgetMapper

from sqlalchemy.types import AbstractType, String, Integer, Float, Boolean
from sqlalchemy.orm import object_mapper
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from sqlalchemy.util import symbol

from ems.thirdparty.singletonmixin import Singleton
from ems.qt4.itemmodel.alchemyormmodel import AlchemyOrmModel
from ems.model.sa.orm.querybuilder import SAQueryBuilder
from sa.delegate.itemview import MapperItemViewDelegate 

from ems.qt4.itemmodel.sa.orm_search_model import SAOrmSearchModel

class BaseStrategy(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
    
    def getEditor(self, mapper, propertyName, rProperty, parent=None):
        raise NotImplementedError()
        
    def getDelegateForItem(self, mapper, propertyName, rProperty, parent=None):
        raise NotImplementedError()
    
    def map(self, mapper, widget, propertyName, rProperty):
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
    def __init__(self, ormObjInstance, model=None, parent=None):
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
            itemDelegate = MapperItemViewDelegate(self._ormObj,
                                                  self.model,
                                                  self,
                                                  self._dataWidgetMapper)
            self._dataWidgetMapper.setItemDelegate(itemDelegate)
        return self._dataWidgetMapper
    
    
    def getDelegateForItemView(self, propertyName=None, parent=None):
        return MapperItemViewDelegate(self._ormObj, self.model, self, parent)
    
    def getDelegateForItem(self, propertyName, rProperty=None, parent=None):
        if rProperty is None:
            rProperty = self.queryBuilder.properties[propertyName]
        strategy = self.getStrategyFor(propertyName, rProperty)
        return strategy.getDelegateForItem(self, propertyName, rProperty,
                                           parent)
    
    def widgetDelegate(self, ormObj, propertyName, model):
        pass
    
    def getModel(self):
        return self._model
    
    def setModel(self, model):
        if not isinstance(model, (AlchemyOrmModel, SAOrmSearchModel)):
            raise TypeError("Model has to be instanceof AlchemyOrmModel")
        self._model = model
        if isinstance(self._dataWidgetMapper,QDataWidgetMapper):
            self._dataWidgetMapper.setModel(model)
        #self._dataWidgetMapper.setItemDelegate(self._delegate)
    
    
    model = property(getModel, setModel)
    
    @property
    def mapper(self):
        return self._mapper
    
    def getEditor(self, propertyName, parent=None):
        rProperty = self.queryBuilder.properties[propertyName]
        strategy = self.getStrategyFor(propertyName, rProperty)
        return strategy.getWidget(self, propertyName, rProperty, parent)
        
    
    def addMapping(self, widget, propertyName):
        if not isinstance(self._model, (AlchemyOrmModel, SAOrmSearchModel)):
            raise TypeError("Assign a AlchemyOrmModel prior to addMapping")
        rProperty = self.queryBuilder.properties[propertyName]
        strategy = self.getStrategyFor(propertyName, rProperty)
        return strategy.map(self, widget, propertyName, rProperty)