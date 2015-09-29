'''
Created on 19.06.2011

@author: michi
'''

from PyQt4.QtCore import QObject, pyqtSignal
from PyQt4.QtGui import QDataWidgetMapper

from sqlalchemy.types import AbstractType, String, Integer, Float, Boolean
from sqlalchemy.orm import object_mapper
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from sqlalchemy.util import symbol
from sqlalchemy.ext.hybrid import hybrid_property, Comparator

from ems.singletonmixin import Singleton
from ems.qt4.itemmodel.alchemyormmodel import AlchemyOrmModel
from ems.model.sa.orm.querybuilder import SAQueryBuilder
from delegate.itemview import MapperItemViewDelegate #@UnresolvedImport

from strategy.base import BaseStrategy
from ems.qt4.itemmodel.sa.orm_search_model import SAOrmSearchModel

class SAInterfaceMixin(object):
    def _init(self):
        self._strategies = {}
    
    def getStrategy(self, type_):
        dictKey = hash(type_)
        if self._strategies.has_key(dictKey):
            return self._strategies[dictKey]
    
    def setStrategy(self, type_, strategy):
        if not isinstance(strategy, BaseStrategy):
            raise TypeError("strategy has to be instance of BaseStrategy")
        self._strategies[hash(type_)] = strategy
    
    def hasStrategyForType(self, type_):
        return self._strategies.has_key(hash(type_))
        

class SAMapperDefaults(Singleton, SAInterfaceMixin):
    def __init__(self):
        SAInterfaceMixin._init(self)

class SAMapper(QObject, SAInterfaceMixin):

    currentIndexChanged = pyqtSignal(int)

    def __init__(self, ormObjInstance, model=None, session=None, parent=None):
        QObject.__init__(self, parent)
        SAInterfaceMixin._init(self)
        self._defaults = SAMapperDefaults.getInstance()
        self._dataWidgetMapper = None
        self._ormObj = ormObjInstance
        self._dataWidgetMapperDelegate = None
        self._queryBuilder = None
        self._defaultStrategy = BaseStrategy(self)
#        self._defaultStrategy.mapper = self
        self._mappings = {}
        self._hashToType = {}
        self._model = model
        self.session = session
        self._currentIndex = -1

    def currentIndex(self):
        return self.dataWidgetMapper.currentIndex()

    def setCurrentIndex(self, idx):
        self.dataWidgetMapper.setCurrentIndex(idx)

    @property
    def ormObject(self):
        return self._ormObj
    
    @property
    def queryBuilder(self):
        if self._queryBuilder is None:
            try:
                self._queryBuilder = self.model.queryBuilder
            except AttributeError:
                self._queryBuilder = SAQueryBuilder(self._ormObj)

        return self._queryBuilder
    
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
            self._dataWidgetMapper.currentIndexChanged.connect(self.currentIndexChanged)
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
    
    def getPrototype(self, classOrObj):
        if isinstance(classOrObj, type):
            return classOrObj()
        return classOrObj
    
    def getRealRelationSymbol(self, rProperty):
        #direction = rProperty.direction
        uselist = rProperty.uselist
        #print "%s uselist %s" % (direction, uselist)
        if uselist:
            return symbol('ONETOMANY')
        else:
            return symbol('MANYTOONE')
    
    def getStrategyFor(self, propertyName, rProperty=None):
        if rProperty is None:
            rProperty = self.queryBuilder.properties[propertyName]
        #rProperty = self.queryBuilder.properties[propertyName]
        #rProperty = objMapper.get_property(property)
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
                                    (self._ormObj.__class__.__name__,propertyName))
            else:
                raise NotImplementedError("ColumnProperties with more than " +
                                          "one Column are not supported")
            
        elif isinstance(rProperty, RelationshipProperty):
            realSymbol = self.getRealRelationSymbol(rProperty)
            mappingKey = realSymbol

        elif isinstance(rProperty, hybrid_property):
            cmp = rProperty.expr(self._ormObj).comparator
            if not isinstance(cmp, Comparator):
                raise ValueError('Please implement a Comparator on hybrid_property "{0}"'.format(rProperty))
            if not hasattr(cmp,'type') or not isinstance(cmp.type, AbstractType):
                raise ValueError('Please implement {0}.type (AbstractType)'.format(cmp.__class__.__name__))
            
            mappingKey = cmp.type.__class__

        key = hash(mappingKey)
        
        self._hashToType[key] = mappingKey
        
        if self._strategies.has_key(key):
            self._strategies[key].mapper = self
            return self._strategies[key]
        elif self._defaults.hasStrategyForType(mappingKey):
            return self._defaults.getStrategy(mappingKey)
        else:
            return self._defaultStrategy
        
    
    def getWidget(self, propertyName, parent=None):
        rProperty = self.queryBuilder.properties[propertyName]
        strategy = self.getStrategyFor(propertyName, rProperty)
        return strategy.getWidget(self, propertyName, rProperty, parent)
        
    
    def addMapping(self, widget, propertyName):
        #if not isinstance(self._model, (AlchemyOrmModel, SAOrmSearchModel)):
            #raise TypeError("Assign a AlchemyOrmModel prior to addMapping")
        rProperty = self.queryBuilder.properties[propertyName]
        strategy = self.getStrategyFor(propertyName, rProperty)
        return strategy.map(self, widget, propertyName, rProperty)