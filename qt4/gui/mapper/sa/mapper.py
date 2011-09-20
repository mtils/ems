'''
Created on 19.06.2011

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
from ems.qt4.gui.itemdelegate.genericdelegate import GenericDelegate
from delegate.itemview import MapperItemViewDelegate #@UnresolvedImport

from strategy.base import BaseStrategy
from ems.qt4.itemmodel.sa.orm_search_model import SAOrmSearchModel

class SAInterfaceMixin(object):
    def _init(self):
        self._strategies = {}
    
    def addStrategy(self, type_, strategy):
        if not isinstance(strategy, BaseStrategy):
            raise TypeError("strategy has to be instance of BaseStrategy")
        self._strategies[hash(type_)] = strategy
        

class SAMapperDefaults(Singleton, SAInterfaceMixin):
    def __init__(self):
        SAInterfaceMixin._init(self)

class SAMapper(QObject, SAInterfaceMixin):
    def __init__(self, ormObjInstance, model=None, session=None, parent=None):
        QObject.__init__(self, parent)
        SAInterfaceMixin._init(self)
        self._defaults = SAMapperDefaults.getInstance()
        self._dataWidgetMapper = None
        self._ormObj = ormObjInstance
        self._dataWidgetMapperDelegate = None
        
        self._defaultStrategy = BaseStrategy(self)
        self._defaultStrategy.mapper = self
        self._mappings = {}
        self._hashToType = {}
        self._model = model
        self.session = session
    
    
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
    
    def itemViewDelegate(self, ormObj, model, parent=None):
        return MapperItemViewDelegate(ormObj, model, self, parent)
    
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
    
    def getPrototype(self, classOrObj):
        if isinstance(classOrObj, type):
            return classOrObj()
        return classOrObj
    
    def getRealRelationSymbol(self, rProperty):
        direction = rProperty.direction
        uselist = rProperty.uselist
        #print "%s uselist %s" % (direction, uselist)
        if uselist:
            return symbol('ONETOMANY')
        else:
            return symbol('MANYTOONE')
    
    def getStrategyFor(self, ormObj, property):
        objMapper = object_mapper(ormObj)
        rProperty = objMapper.get_property(property)
        mappingKey = None
        
        if isinstance(rProperty, ColumnProperty):
            cols = rProperty.columns
            if len(cols) == 1:
                col = cols[0]
                colType = col.type
                if isinstance(colType, AbstractType):
                    mappingKey = col.type.__class__
                else:
                    raise TypeError("Could not determine Type of %s.%s" % \
                                    (ormObj.__class__.__name__,property))
            else:
                raise NotImplementedError("ColumnProperties with more than " +
                                          "one Column are not supported")
            
        elif isinstance(rProperty, RelationshipProperty):
            realSymbol = self.getRealRelationSymbol(rProperty)
            mappingKey = realSymbol
            #mappingKey = rProperty.direction
        #print "%s.%s mappingKey: %s" % (ormObj.__class__.__name__, property, mappingKey)
        key = hash(mappingKey)
        self._hashToType[key] = mappingKey
        
        if self._strategies.has_key(key):
            self._strategies[key].mapper = self
            return self._strategies[key]
        
        else:
            return self._defaultStrategy
        
    
    def getWidget(self, ormObj, property):
        return self.getStrategyFor(ormObj, property).getWidget(ormObj, property)
        
    
    def addMapping(self, widget, ormObj, propertyName):
        if not isinstance(self._model, (AlchemyOrmModel, SAOrmSearchModel)):
            raise TypeError("Assign a AlchemyOrmModel prior to addMapping")
        return self.getStrategyFor(ormObj, propertyName).map(widget, ormObj, propertyName)