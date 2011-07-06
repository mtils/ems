#coding=utf-8
'''
Created on 26.06.2011

@author: michi
'''
from PyQt4.QtCore import QVariant, QString, Qt
from PyQt4.QtGui import QSpinBox, QDoubleSpinBox, QLineEdit

from sqlalchemy import and_, or_
from sqlalchemy.orm import RelationshipProperty, ColumnProperty
from sqlalchemy.types import AbstractType, String, Integer, Float, Boolean

from ems.qt4.gui.widgets.row_add_search import BuilderBackend #@UnresolvedImport
from ems.model.sa.orm.querybuilder import SAQueryBuilder, PathClause, AndList, OrList #@UnresolvedImport

class SABuilderBackend(BuilderBackend):
    def __init__(self, ormObj, mapper):
        self._ormObj = ormObj
        self._mapper = mapper
        self._decorators = {}
        self._queryBuilder = SAQueryBuilder(ormObj)
        self._orderedProperties = []
        self._shownPropertiesByClassName = {}
    
    @property
    def queryBuilder(self):
        
        return self._queryBuilder
    
    def populateFieldInput(self, fieldInput):
        
        i=0
        for property in self.orderedProperties:
            depth = len(property[0].split('.')) - 1
            fieldInput.addItemFlat(depth, (QString.fromUtf8(property[1]),
                                           property[0]))
#            print property
            i += 1
        
    
    @property
    def shownPropertiesByClassName(self):
        if not len(self._shownPropertiesByClassName):
            dec = self._ormObj.__ormDecorator__()
            self._shownPropertiesByClassName[self._ormObj.__class__.__name__] = dec.getShownProperties()
            joinNames = self._queryBuilder.joinNames
            for joinName in joinNames:
                class_ = self._queryBuilder.joinNameClasses[joinName]
                dec = class_.__ormDecorator__()
                self._shownPropertiesByClassName[class_.__name__] = dec.getShownProperties()
        return self._shownPropertiesByClassName
    
    @property
    def orderedProperties(self):
        if not len(self._orderedProperties):
            self._loadOrderedProperties()
        return self._orderedProperties
    
    def _loadOrderedProperties(self, ormClass=None, pathStack=[]):
        
        joinNames = self._queryBuilder.joinNames
        
        if ormClass is None:
            ormClass = self._ormObj.__class__
        
        dec = ormClass.__ormDecorator__()
        
        for propertyName in dec.getShownProperties():
            
            pathStack.append(propertyName)
            propertyPath = ".".join(pathStack)
            
            if self._queryBuilder.properties.has_key(propertyPath):
                if isinstance(self._queryBuilder.properties[propertyPath],
                              RelationshipProperty):
                    if propertyPath in joinNames:
                        joinClass = self._queryBuilder.joinNameClasses[propertyPath]
                        self._orderedProperties.append((propertyPath,
                                                    self.getFieldFriendlyName(propertyPath),
                                                    'join'))
                        self._loadOrderedProperties(joinClass, pathStack)
                        
                if isinstance(self._queryBuilder.properties[propertyPath],
                              ColumnProperty):
                    self._orderedProperties.append((propertyPath,
                                                    self.getFieldFriendlyName(propertyPath),
                                                    'column'))
            
            pathStack.pop()
        return self._orderedProperties
    
    def getFieldFriendlyName(self, fieldName):
        try:
            dec = self._queryBuilder.propertyName2Class[fieldName].__ormDecorator__()
            return dec.getPropertyFriendlyName(fieldName)
        except KeyError:
            return fieldName
    
    def onFieldInputCurrentItemChanged(self, searchRow, item):
        self.refillOperatorCombo(searchRow, str(item.data(1,Qt.DisplayRole).toString()))
        self.displayValueWidget(searchRow, str(item.data(1,Qt.DisplayRole).toString()))
        
    def refillOperatorCombo(self, searchRow, currentProperty):
        #print "refill: %s" % currentProperty
        property = self._queryBuilder.properties[currentProperty]
        if isinstance(property, ColumnProperty):
            cols = property.columns
            if len(cols) == 1:
                col = cols[0]
                colType = col.type
                if isinstance(colType, AbstractType):
                    type_ = col.type
                    if isinstance(type_,(Integer, Float)):
                        searchRow.operatorInput.clear()
                        searchRow.operatorInput.addItem('=',QVariant('='))
                        searchRow.operatorInput.addItem('>',QVariant('>'))
                        searchRow.operatorInput.addItem('>=',QVariant('>='))
                        searchRow.operatorInput.addItem('<',QVariant('<'))
                        searchRow.operatorInput.addItem('<=',QVariant('<='))
                    
                    if isinstance(type_,String):
                        searchRow.operatorInput.clear()
                        searchRow.operatorInput.addItem(QString.fromUtf8('enthält'),QVariant('LIKE'))
                        searchRow.operatorInput.addItem(QString.fromUtf8('ist alphabetisch vor'),QVariant('BEFORE'))
                        searchRow.operatorInput.addItem(QString.fromUtf8('ist alphabetisch nach'),QVariant('AFTER'))
                else:
                    raise TypeError("Could not determine Type of %s" % \
                                    property)
            else:
                raise NotImplementedError("ColumnProperties with more than " +
                                          "one Column are not supported")
        else:
            searchRow.operatorInput.clear()
            searchRow.operatorInput.addItem(QString.fromUtf8('ist'),QVariant('='))
            
    def displayValueWidget(self, searchRow, currentProperty):
#        print "displayValueWidget %s" % currentProperty
        propertyKey = currentProperty.split('.')[-1:][0]
        class_ = self._queryBuilder.propertyName2Class[currentProperty]
        newWidget = self._mapper.getWidget(class_(), propertyKey)
        searchRow.replaceValueInput(newWidget)
    
    def buildQuery(self, clauses):
        
        crit = self._queryBuilder.propertyName2Class['zustand.baujahrklasseId'].baujahrklasseId == 15
        #print type(crit)
        #print query.filter(crit)
        #print query
        
        pathClauses = []
        conjunctions = []
        
        for clause in clauses:
            field = unicode(clause['field'])
            pc = PathClause(field)
            if clause['value'] is not None:
                pc = self.buildPathClause(field, clause['operator'],
                                          clause['value'],
                                          clause['matches'])
                pathClauses.append(pc)
                conjunctions.append(clause['conjunction'])
                #value = unicode(clause['value'])
            #print "%s %s" % (field, value)
        filter=None
        booleanClauses = []
        currentClause = None
        if len(pathClauses) > 1:
            i=0
            for clause in pathClauses:
                if conjunctions[i] is not None:
                    if conjunctions[i] == 'AND':
                        currentClause = AndList()
                    elif conjunctions[i] == 'OR':
                        currentClause = OrList()
                    if i > 0:
                        if len(booleanClauses) >= 1:
                            #booleanClauses[len(booleanClauses)-1].append(currentClause)
                            currentClause.append(booleanClauses[len(booleanClauses)-1])
                        else:
                            currentClause.append(pathClauses[i-1])
                    currentClause.append(clause)
                    booleanClauses.append(currentClause)
                    
                i+=1
            
            filter = booleanClauses[len(booleanClauses)-1]
        elif len(pathClauses) == 1:
            filter = pathClauses[0]
        
        
            
        query = self._queryBuilder.getQuery(self._mapper.session, filter=filter)
            
    def buildPathClause(self, field, operator, value, matches):
        pc = PathClause(field)
        if operator == '=':
            if matches:
                return pc.__eq__(value)
            else:
                return pc.__ne__(value)
        elif operator == '<':
            if matches:
                return pc.__lt__(value)
            else:
                return pc.__ge__(value)
        elif operator == '<=':
            if matches:
                return pc.__le__(value)
            else:
                return pc.__gt__(value)
        elif operator == '>':
            if matches:
                return pc.__gt__(value)
            else:
                return pc.__le__(value)
        elif operator == '>=':
            if matches:
                return pc.__ge__(value)
            else:
                return pc.__lt__(value)
        elif operator == 'LIKE':
            if matches:
                return pc.like(value)
            else:
                return pc.notLike(value)
        elif operator == 'BEFORE':
            if matches:
                return pc.__lt__(value)
            else:
                return pc.__gt__(value)
        elif operator == 'AFTER':
            if matches:
                return pc.__gt__(value)
            else:
                return pc.__lt__(value)