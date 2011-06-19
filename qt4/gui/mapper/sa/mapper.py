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

from strategy.base import BaseStrategy

class SAInterfaceMixin(object):
    def _init(self):
        self._strategies = {}
    
    def addStrategy(self, type_, strategy):
        if not isinstance(strategy, BaseStrategy):
            raise TypeError("strategy has to be instance of BaseStrategy")
        self._strategies[hash(type_)] = strategy
        print self._strategies
        

class SAMapperDefaults(Singleton, SAInterfaceMixin):
    def __init__(self):
        SAInterfaceMixin._init(self)

class SAMapper(QObject, SAInterfaceMixin):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        SAInterfaceMixin._init(self)
        self._defaults = SAMapperDefaults.getInstance()
        self._dataWidgetMapper = QDataWidgetMapper(self)
        self._defaultStrategy = BaseStrategy(self)
        self._defaultStrategy.mapper = self
        self._mappings = {}
        self._hashToType = {}
        self._model = None
    
    @property
    def dataWidgetMapper(self):
        return self._dataWidgetMapper
    
    def getModel(self):
        return self._model
    
    def setModel(self, model):
        if not isinstance(model, AlchemyOrmModel):
            raise TypeError("Model has to be instanceof AlchemyOrmModel")
        self._model = model
        self._dataWidgetMapper.setModel(model)
    
    
    model = property(getModel, setModel)
    
    @property
    def mapper(self):
        return self._mapper
        
    
    def addMapping(self, widget, ormClassOrObj, property):
        if not isinstance(self._model, AlchemyOrmModel):
            raise TypeError("Assign a AlchemyOrmModel prior to addMapping")
        if isinstance(ormClassOrObj, type):
            prototype = ormClassOrObj()
        else:
            prototype = ormClassOrObj
        objMapper = object_mapper(prototype)
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
                                    (prototype.__class__.__name__,property))
            else:
                raise NotImplementedError("ColumnProperties with more than " +
                                          "one Column are not supported")
            
        elif isinstance(rProperty, RelationshipProperty):
            mappingKey = rProperty.direction
            
        #print rProperty.direction
        #print widget, prototype, property
#        print mappingKey
        key = hash(mappingKey)
        self._hashToType[key] = mappingKey
        if self._strategies.has_key(key):
            print "Ja da jibt es einen"
            self._strategies[key].map(widget, prototype, property)
        
        else:
            return self._defaultStrategy.map(widget, prototype, property)