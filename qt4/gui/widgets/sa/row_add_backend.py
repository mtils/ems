#coding=utf-8
'''
Created on 26.06.2011

@author: michi
'''
from PyQt4.QtCore import QVariant, QString, Qt
from PyQt4.QtGui import QSpinBox, QDoubleSpinBox, QLineEdit

from sqlalchemy.orm import RelationshipProperty, ColumnProperty
from sqlalchemy.types import AbstractType, String, Integer, Float, Boolean

from ems.qt4.gui.widgets.row_add_search import BuilderBackend #@UnresolvedImport
from ems.model.sa.orm.querybuilder import SAQueryBuilder #@UnresolvedImport

class SABuilderBackend(BuilderBackend):
    def __init__(self, ormObj, mapper):
        self._ormObj = ormObj
        self._mapper = mapper
        self._decorators = {}
        self._queryBuilder = SAQueryBuilder(ormObj)
        self._orderedProperties = []
        self._shownPropertiesByClassName = {}
    
    def populateFieldInput(self, fieldInput):
        
        i=0
        for property in self.orderedProperties:
            depth = len(property[0].split('.')) - 1
            fieldInput.addItemFlat(depth, (QString.fromUtf8(property[1]),
                                           property[0]))
            print property
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
                    if isinstance(type_,Integer):
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
    def displayValueWidget(self, searchRow, currentProperty):
        propertyKey = currentProperty.split('.')[-1:][0]
        class_ = self._queryBuilder.propertyName2Class[currentProperty]
        newWidget = self._mapper.getWidget(class_(), propertyKey)
        searchRow.replaceValueInput(newWidget)
        