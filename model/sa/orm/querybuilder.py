'''
Created on 26.06.2011

@author: michi
'''

from sqlalchemy.orm import joinedload, joinedload_all, object_mapper, \
    RelationshipProperty, ColumnProperty, aliased, contains_eager


from ems.util import GenClause   #@UnresolvedImport
from ems.thirdparty.odict import OrderedDict

from sqlalchemy.util import symbol
from sqlalchemy.sql.expression import and_, or_
from lib.ems.model.sa.orm.base_object import OrmBaseObject

class PathClauseList(object):
    def __init__(self, conjunction, initialClauses=[]):
        self.conjunction = conjunction
        self.clauses = []
        
        #self.clauses = initialClauses
        
    def append(self, clause):
        self.clauses.append(clause)
    
#    def __str__(self):
#        conjString = ""
#        conjStrings = []
#        #return str(id(self))
#        for clause in self.clauses:
#            conjStrings.append(conjString)
#            conjStrings.append(str(clause))
#            conjString = " " + self.conjunction + " "
#            
#            
#        return "".join(conjStrings)
#    
#    def __repr__(self):
#        return self.__str__()
    
class AndList(PathClauseList):
    def __init__(self, *args):
        super(AndList, self).__init__('AND',*args)
        
class OrList(PathClauseList):
    def __init__(self, *args):
        super(OrList, self).__init__('OR',*args)

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
    
    def __init__(self, ormObj, filterJoins=(), forceJoins=[]):
        self._ormObj = ormObj
        self._mapper = object_mapper(self._ormObj)
        self._propertyNames = []
        self._propertyNamesDecorated = []
        self._properties = {}
        self._joinNames = []
        self._joinNameClasses = {}
        self._propertyNameClasses = {}
        self._filterJoins = filterJoins
        self._multipleRowsProperties = []
        self._forceJoins = forceJoins
    
    @property
    def ormObj(self):
        return self._ormObj
    
    def getPropertyNames(self):
        if not len(self._propertyNames):
            self._extractPropertiesAndJoins(self._ormObj)
        return self._propertyNames
    
    propertyNames = property(getPropertyNames)
    
    def getPropertyNamesDecorated(self):
        if not len(self._propertyNamesDecorated):
            self._loadPropertyNamesDecorated()
        return self._propertyNamesDecorated
    
    propertyNamesDecorated = property(getPropertyNamesDecorated)
    
    def _loadPropertyNamesDecorated(self, ormClass=None, pathStack=[]):
        
        if ormClass is None:
            ormClass = self._ormObj.__class__
        
        dec = ormClass.__ormDecorator__()
        
        for propertyName in dec.getShownProperties():
            
            pathStack.append(propertyName)
            propertyPath = ".".join(pathStack)
            
            if self.properties.has_key(propertyPath):
                if isinstance(self.properties[propertyPath],
                              RelationshipProperty):
                    if propertyPath in self.joinNames:
                        joinClass = self.joinNameClasses[propertyPath]
                        self._propertyNamesDecorated.append(propertyPath)
                        self._loadPropertyNamesDecorated(joinClass, pathStack)
                        
                if isinstance(self.properties[propertyPath],
                              ColumnProperty):
                    self._propertyNamesDecorated.append(propertyPath)
            
            pathStack.pop()
        return self._propertyNamesDecorated
    
    def _addJoinPath(self, joins, joinPath):
        pathName = []
        for pathPart in joinPath.split('.'):
            pathName.append(pathPart)
            path = ".".join(pathName)
            if path not in joins:
                joins.append(path)
            
    def _calculateJoinNames(self, propertyNames, filter):
        joins = []
        filterPropertyNames = []
        if not len(self._properties):
            self._extractPropertiesAndJoins(self._ormObj)
            
        if isinstance(filter, PathClauseList):
            #raise NotImplementedError("Or und And kommt noch")
            filterPropertyNames = self._extractPropertyNamesFromClauseList(filter, [])
        if isinstance(filter, PathClause):
            filterPropertyNames = [filter.left]
        
        
        
        for propertyName in filterPropertyNames:
            property = self.properties[propertyName]
            if isinstance(property, RelationshipProperty):
#                print "%s is RelationShip" % propertyName
                self._addJoinPath(joins, propertyName)
            else:
#                print "%s is Column" % propertyName
                split = propertyName.split('.')
                if len(split):
                    parentName = ".".join(split[:-1])
                    if parentName in self.joinNames:
                        self._addJoinPath(joins, parentName)
                        #if parentName not in joins:
                        #    joins.append(parentName)
                else:
                    parentName = None
                
                #print self.properties[propertyName]
                #print "prop: %s parent: %s" % (propertyName, parentName)
#        print self.properties.keys()
        for propertyName in propertyNames:
            #print propertyName
            property = self.properties[propertyName]
            if isinstance(property, RelationshipProperty):
                self._addJoinPath(joins, propertyName)
            else:
                split = propertyName.split('.')
                if len(split) > 1:
                    parentName = ".".join(split[:-1])
                    self._addJoinPath(joins, parentName)
#                    if parentName not in joins:
#                        joins.append(parentName)
            #print split
            
        #print joins
        return joins
    
    def _buildJoinAliases(self, joinNames):
        sortedAliases = OrderedDict()
        aliases = {}
        for joinName in joinNames:
            #print self.joinNameClasses[joinName]
            aliases[joinName] = aliased(self.joinNameClasses[joinName])
        return aliases
    
    def _extractPropertyNamesFromClauseList(self, clauseList, propertyNames=[]):
        
        for clause in clauseList.clauses:
            if isinstance(clause, PathClauseList):
                self._extractPropertyNamesFromClauseList(clause, propertyNames)
            elif isinstance(clause, PathClause):
                if clause.left not in propertyNames:
                    propertyNames.append(clause.left)
            
        return propertyNames
    
    def getQuery(self, session, propertySelection=[], appendOptions=None, filter=None):
        
#        self._multipleRowsProperties = []
        
        if not len(propertySelection):
            propertySelection = self.propertyNamesDecorated
        
        uniqueJoinNames = self._calculateJoinNames(propertySelection, filter)
#        print uniqueJoinNames
        aliases = self._buildJoinAliases(uniqueJoinNames)
        joinNames = aliases.keys()
        joinNames.sort()
        #print joinNames
        query = session.query(self._ormObj.__class__)
        
        for joinName in joinNames:
            parentClass = None
            split = joinName.split('.')
            #print split
            if len(split) > 1:
                propertyName = split[-1:][0]
                parentName = ".".join(split[:-1])
                parentClass = aliases[parentName]
                query = query.outerjoin((aliases[joinName],parentClass.__getattr__(propertyName)))
            else:
                parentClass = self._ormObj.__class__
                propertyName = joinName
                query = query.outerjoin((aliases[joinName],parentClass.__dict__[propertyName]))
        
        query = self._addFilter(query, filter, aliases)
        containsEagers = self._getContainsEagers(propertySelection, aliases,
                                                joinNames)            
        
        if len(containsEagers):
            if appendOptions is not None:
                for option in appendOptions:
                    containsEagers.append(option)
            query = query.options(*containsEagers)
        #print str(query).replace('LEFT OUTER JOIN', '\nLEFT OUTER JOIN')
        return query
    
    
    def _getContainsEagers(self, propertyNames, aliases, joinNames):
        neededJoins = []
#        print "PropertyNames:"
        for propertyName in propertyNames:
#            print propertyName
            property = self.properties[propertyName]
            if isinstance(property, RelationshipProperty):
                #print "Relationship: %s" % propertyName
                split = propertyName.split('.')
                stack = []
                for part in split:
                    stack.append(part)
                    stackedProperty = u".".join(stack)
                    #print "Einzeln: %s" % stackedProperty 
                    if stackedProperty not in neededJoins:
                        neededJoins.append(stackedProperty)
                        #print "I add %s" % stackedProperty
                        
            elif isinstance(property, ColumnProperty):
#                print "ColumnProperty: %s" % propertyName
                split = propertyName.split('.')
                if len(split) > 1:
                    joinSplit = split[:-1] 
                    #print "joinName of Property: %s" % joinName
                    stack = []
                    for part in joinSplit:
                        stack.append(part)
                        stackedProperty = u".".join(stack)
                        if stackedProperty not in neededJoins:
                            neededJoins.append(stackedProperty)
#                    if joinName not in neededJoins:
#                        neededJoins.append(joinName)
                    
            
        containsEagers = []
#        print "neededJoins:"
        for neededJoin in neededJoins:
#            print "NeededJoin %s" % neededJoin
            containsEagers.append(contains_eager(neededJoin, alias=aliases[neededJoin]))
            
        return containsEagers
        
    
    def _addFilter(self, query, filter, aliases):
        #print filter
        if isinstance(filter, PathClauseList):
            saClauseList = self._convertPathClauseList(filter, aliases)
            query = query.filter(saClauseList)
            
        if isinstance(filter, PathClause):
            try:
                clause = self._convertPathClause(filter, aliases)
                query = query.filter(clause)
            except:
                print "Cannot convert PathClause %s" % clause
        
        return query
    
    def _convertPathClauseList(self, clauseList, aliases, parentClause=None):
        if isinstance(clauseList, PathClauseList):
            if clauseList.conjunction == "AND":
                saClause = and_()
            elif clauseList.conjunction == 'OR':
                saClause = or_()
            for clause in clauseList.clauses:
                if isinstance(clause, PathClause):
                    try:
                        saClause.append(self._convertPathClause(clause, aliases))
                    except:
                        print "Cannot convert PathClause %s" % clause
                         
                elif isinstance(clause, PathClauseList):
                    saClause.append(self._convertPathClauseList(clause, aliases, saClause))
            return saClause
                    
    def _convertPathClause(self, clause, aliases):
        
        property = self.properties[clause.left]
        if isinstance(property, ColumnProperty):
            split = clause.left.split('.')
            if len(split) < 2:
                return self._ormObj.__class__.__dict__[clause.left].__getattribute__(self._translateOperator(clause.operator))(clause.right)
            else:
                parentName = ".".join(split[:-1])
                propName = split[-1:][0]
                method = self._translateOperator(clause.operator)
                return aliases[parentName].__getattr__(propName).__getattr__(method)(clause.right)
            
        if isinstance(property, RelationshipProperty):
            split = clause.left.split('.')
#            print clause
#            if not isinstance(clause.right, OrmBaseObject):
#                return
#            print type(clause.right)
            if len(split) < 2:
                return self._ormObj.__class__.__dict__[clause.left].__eq__(clause.right)
            else:
                parentName = ".".join(split[:-1])
                propName = split[-1:][0]
                
                return aliases[parentName].__getattr__(propName).__eq__(clause.right)
    
    def _translateOperator(self, operator):
        table = {'==':'__eq__',
         '!=':'__ne__',
         '<':'__lt__',
         '<=':'__le__',
         '>':'__gt__',
         '>=':'__ge__',
         'like':'like',
         'BEFORE':'<',
         'AFTER':'>'}
        return table[operator]
    @property
    def propertyName2Class(self):
        return self._propertyNameClasses
    
    @property
    def properties(self):
        if not len(self._properties):
            self._extractPropertiesAndJoins(self._ormObj)
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
    
    def hasMultipleRowProperties(self, propertyNames):
        checkedProperties = []
        multipleRowProperties = []
        for propertyName in propertyNames:
            prop = self._properties[propertyName]
            if isinstance(prop, RelationshipProperty):
                if (prop.uselist) and (propertyName not in multipleRowProperties):
                    multipleRowProperties.append(propertyName)
#                print "%s is Rel" % propertyName
            elif isinstance(prop, ColumnProperty):
                propNameSplit = propertyName.split('.')
                nodes = []
                
                for node in propNameSplit:
                    nodes.append(node)
                    joinName = '.'.join(nodes)
#                    print joinName
                    if joinName not in checkedProperties:
                        parentProp = self._properties[joinName]
                        if isinstance(parentProp, RelationshipProperty):
                            if parentProp.uselist and (joinName not in multipleRowProperties):
                                multipleRowProperties.append(joinName)
#                            print "%s is Rel" % parentProp
                        checkedProperties.append(joinName)
#                #parentName = ".".join(propNameSplit[:-1])
#                print "%s as parent %s" % 
#                print "%s is Col" % propertyName
        return multipleRowProperties
    
    def _extractPropertiesAndJoins(self, obj, pathStack=[],
                                        alreadyAddedClasses=[],
                                        recursionCounter = -1):
        recursionCounter += 1
        if recursionCounter == 0:
            pathStack = []
            alreadyAddedClasses = []

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
#                print prop
                if len(pathStack):
                    joinName = "%s.%s" % (".".join(pathStack), prop.key)
                else:
                    joinName = prop.key
                #print joinName
                
                if not prop.uselist or (joinName in self._forceJoins):
                    
                    if prop.uselist:
                        self._multipleRowsProperties.append(joinName)
                        
                    classType = prop.mapper.class_
                    if classType is not self._ormObj.__class__:
                        
                        
                        if joinName not in self._joinNames:
                            self._joinNames.append(joinName)
                        
                        self._propertyNames.append(joinName)
                        self._propertyNameClasses[joinName] = obj.__class__
                        self._properties[joinName] = prop
                        
                        pathStack.append(prop.key)
                        self._joinNameClasses[joinName] = classType
                        if classType not in alreadyAddedClasses:
                            self._extractPropertiesAndJoins(classType(), pathStack,
                                                           alreadyAddedClasses,
                                                           recursionCounter)
                        
                        pathStack.pop()