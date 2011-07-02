'''
Created on 26.06.2011

@author: michi
'''

from sqlalchemy.orm import joinedload, joinedload_all, object_mapper, \
    RelationshipProperty, ColumnProperty

from ems.util import GenClause   #@UnresolvedImport

from sqlalchemy.util import symbol

class PathClause(GenClause):
    def like(self, other):
        self.operator = 'like'
        self.right = other
        return self
    
    def notLike(self, other):
        self.operator = 'notLike'
        self.right = other
        return self
        
    

class SAQueryBuilder(object):
    
    def __init__(self, ormObj, filterJoins=()):
        self._ormObj = ormObj
        self._mapper = object_mapper(self._ormObj)
        self._propertyNames = []
        self._properties = {}
        self._joinNames = []
        self._joinNameClasses = {}
        self._propertyNameClasses = {}
        self._filterJoins = filterJoins
    
    @property
    def ormObj(self):
        return self._ormObj
    
    def getPropertyNames(self):
        if not len(self._propertyNames):
            self._extractPropertiesAndJoins(self._ormObj)
        return self._propertyNames
    
    propertyNames = property(getPropertyNames)
    
    def getQuery(self, session, properties=[], joins=[], filters=[]):
        query = session.query(self._ormObj.__class__)
        
        joinloads = []
        
        for join in joins:
            joinloads.append(joinedload_all(join))
        else:
            for joinName in self.joinNames:
                joinloads.append(joinedload_all(joinName))
        query = query.options(*joinloads)
        return query
    
    @property
    def propertyName2Class(self):
        return self._propertyNameClasses
    
    @property
    def properties(self):
        return self._properties 
    
    def getJoinNames(self):
        if not len(self._joinNames):
            self._extractPropertiesAndJoins(self._ormObj)
        
        return self._joinNames
    
    joinNames = property(getJoinNames)
    
    def getJoinNameClasses(self):
        if not len(self._joinNameClasses):
            self._extractPropertiesAndJoins(self._ormObj)
        return self._joinNameClasses
    
    joinNameClasses = property(getJoinNameClasses)
    
    def _extractPropertiesAndJoins(self, obj, pathStack=[],
                                        alreadyAddedClasses=[],
                                        recursionCounter = -1):
        recursionCounter += 1
        if recursionCounter > 100:
            raise StopIteration()
        
        mapper = object_mapper(obj)
        alreadyAddedClasses.append(obj.__class__)
        
        for prop in mapper.iterate_properties:
            if isinstance(prop, ColumnProperty):
                if len(pathStack):
                    propertyName = "%s.%s" % (".".join(pathStack), prop.key) 
                else:
                    propertyName = prop.key
                self._propertyNames.append(propertyName)
                self._properties[propertyName] = prop
                self._propertyNameClasses[propertyName] = obj.__class__
                
            elif isinstance(prop, RelationshipProperty):
                if not prop.uselist:
                    classType = prop.mapper.class_
                    if classType is not self._ormObj.__class__:
                        if len(pathStack):
                            joinName = "%s.%s" % (".".join(pathStack), prop.key)
                        else:
                            joinName = prop.key
                        
                        if joinName not in self._joinNames:
                            self._joinNames.append(joinName)
                        
                        self._propertyNames.append(joinName)
                        self._propertyNameClasses[joinName] = obj.__class__
                        self._properties[joinName] = prop
                        
                        pathStack.append(prop.key)
                        self._joinNameClasses[joinName] = classType
                        self._extractPropertiesAndJoins(classType(), pathStack,
                                                       alreadyAddedClasses,
                                                       recursionCounter)
                        
                        pathStack.pop()