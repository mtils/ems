#coding=utf-8
'''
Created on 26.06.2011

@author: michi
'''
import inspect

from PyQt4.QtCore import QVariant, QString, Qt, pyqtSignal, QObject
from PyQt4.QtGui import QSpinBox, QDoubleSpinBox, QLineEdit, QCheckBox,\
    QComboBox

from sqlalchemy import and_, or_
from sqlalchemy.orm import RelationshipProperty, ColumnProperty
from sqlalchemy.orm.query import Query
from sqlalchemy.types import AbstractType, String, Integer, Float, Boolean
from sqlalchemy.ext.hybrid import hybrid_property #@UnresolvedImport
from sqlalchemy.sql.operators import ColumnOperators

from ems.qt4.gui.widgets.tableview.querybuilder_tableview import RowBuilderBackend #@UnresolvedImport
from ems.model.sa.orm.querybuilder import SAQueryBuilder, PathClause, AndList, OrList #@UnresolvedImport
from ems.qt4.gui.widgets.treecombo import TreeComboBox #@UnresolvedImport
from ems.qt4.gui.widgets.bigcombo import BigComboBox #@UnresolvedImport
from ems.qt4.util import variant_to_pyobject #@UnresolvedImport
from ems.model.sa.orm import base_object

class SABuilderBackend(RowBuilderBackend):
    
    
    
    def __init__(self, ormObj, mapper, parent=None, queryBuilder=None):
        self._ormObj = ormObj
        self._mapper = mapper
        self._decorators = {}
        if queryBuilder is None:
            queryBuilder = SAQueryBuilder(ormObj)
        self._queryBuilder = queryBuilder
        self._orderedProperties = []
        self._shownPropertiesByClassName = {}
        self._queryListeners = []
        self._fieldPathNames = {}
        self._operatorTranslation = {'LIKE':u'enthält',
                                     'BEFORE':u'ist alpabetisch vor',
                                     'AFTER':u'ist alpabetisch nach'}
        self._loadFieldPathNames()
        RowBuilderBackend.__init__(self, parent)
    
    def getDisplayedOperatorText(self, data):
        try:
            return self._operatorTranslation[unicode(data.toString())]
        except KeyError:
            return unicode(data.toString())
    
    def _loadFieldPathNames(self):
        for property in self.orderedProperties:
            stack = property[0].split('.')
            #print property[0]
            translatedStack = []
            currentStack = []
            for node in stack:
                currentStack.append(node)
                friendlyName = self.getFieldFriendlyName(".".join(currentStack))
                translatedStack.append(unicode(friendlyName))
            self._fieldPathNames[property[0]] =  u" > ".join(translatedStack)
#        print self._fieldPathNames
            
    def getDisplayedFieldText(self, data):
        #if not len()
        fieldName = unicode(data.toString())
        try:
            return self._fieldPathNames[fieldName]
        except KeyError:
            return fieldName
    
    def getDisplayedValueText(self, property, value):
        if property:
            cls = self._queryBuilder.propertyName2Class[property]
            if hasattr(cls,'__ormDecorator__'):
                dec = cls.__ormDecorator__()
                return QString.fromUtf8(dec.valueToFormattedString(property.split('.')[-1:][0],
                                                 variant_to_pyobject(value)))
            
        return value.toString()
    
    @property
    def queryBuilder(self):
        
        return self._queryBuilder
    
    def addQueryListener(self, listener):
        
        self._queryListeners.append(listener)
    
    def populateFieldInput(self, fieldInput):
        
        i=0
        for property in self.orderedProperties:
            depth = len(property[0].split('.')) - 1
            fieldInput.addItemFlat(depth, (QString.fromUtf8(property[1]),
                                           property[0]))
#            print property
            i += 1
        
        
        fieldInput.itemTreeView.expandAll()
    
    def setEditorData(self, editor, index):
        widget = editor
        
        value = variant_to_pyobject(index.data())
        
        if value is None:
            return
        if isinstance(widget, QCheckBox) and isinstance(value, bool):
            widget.setChecked(value)
            return
        if isinstance(widget, TreeComboBox):
            widget.setValue(value)
            return
        if isinstance(widget, BigComboBox):
            if isinstance(value, basestring):
                widget.setEditText(value)
            else:
                if hasattr(value, '__ormDecorator__'):
                    valueStr = value.__ormDecorator__().getReprasentiveString(value)
                    widget.setEditText(QString.fromUtf8(valueStr))
                
            return
        if isinstance(widget, QComboBox):
            if isinstance(value, basestring):
                index = widget.findText(value)
                widget.setCurrentIndex(index)
            if isinstance(value, int):
                if widget.count() > value:
                    widget.setCurrentIndex(value)
            if hasattr(value, '__ormDecorator__'):
                for i in range(widget.count()):
                    if variant_to_pyobject(widget.itemData(i)) is value:
                        widget.setCurrentIndex(i)
                        return
            
            return
        if hasattr(widget, 'setValue') and callable(widget.setValue):
            if isinstance(widget, QSpinBox) and isinstance(value, int):
                widget.setValue(value)
            if isinstance(widget, QDoubleSpinBox) and isinstance(value, float):
                widget.setValue(value)
            return
        if hasattr(widget, 'setText') and callable(widget.setText) and isinstance(value, basestring):
            widget.setText(QString.fromUtf8(value))
            return
    
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
                if isinstance(self._queryBuilder.properties[propertyPath],
                              hybrid_property):
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
    
    def onFieldInputCurrentFieldChanged(self, searchRow, field):
        self.refillOperatorCombo(searchRow, field)
        self.displayValueWidget(searchRow, field)
        
    def populateOperatorCombo(self, operatorInput, currentProperty):
        #print "refill: %s" % currentProperty
        if not self._queryBuilder.properties.has_key(currentProperty):
            operatorInput.clear()
            return
        property = self._queryBuilder.properties[currentProperty]
        if isinstance(property, ColumnProperty):
            cols = property.columns
            if len(cols) == 1:
                col = cols[0]
                colType = col.type
                if isinstance(colType, AbstractType):
                    type_ = col.type
                    if isinstance(type_,(Integer, Float)):
                        operatorInput.clear()
                        operatorInput.addItem('=',QVariant('='))
                        operatorInput.addItem('>',QVariant('>'))
                        operatorInput.addItem('>=',QVariant('>='))
                        operatorInput.addItem('<',QVariant('<'))
                        operatorInput.addItem('<=',QVariant('<='))
                    
                    if isinstance(type_,String):
                        operatorInput.clear()
                        operatorInput.addItem(QString.fromUtf8(self._operatorTranslation['LIKE']),
                                              QVariant('LIKE'))
                        operatorInput.addItem(QString.fromUtf8(self._operatorTranslation['BEFORE']),
                                              QVariant('BEFORE'))
                        operatorInput.addItem(QString.fromUtf8(self._operatorTranslation['AFTER']),
                                              QVariant('AFTER'))
                else:
                    raise TypeError("Could not determine Type of %s" % \
                                    property)
            else:
                raise NotImplementedError("ColumnProperties with more than " +
                                          "one Column are not supported")
        elif isinstance(property, hybrid_property):
            prototype = self._queryBuilder.ormObj
            #print prototype.__class__.__getattr__()
            operatorInput.clear()
            cmp = property.expr(prototype).comparator

            #Don't rely on base methods in ColumnOperators
            def has_method(cm, methodName):
                for cls in inspect.getmro(cm.__class__):
                    if cls is ColumnOperators:
                        return False
                    if methodName in cls.__dict__:
                        return True

            if has_method(cmp,'__eq__'):
                operatorInput.addItem(QString.fromUtf8('='),QVariant('='))
            if has_method(cmp, '__ne__'):
                operatorInput.addItem(QString.fromUtf8('!='),QVariant('!='))
            if has_method(cmp,'__le__'):
                operatorInput.addItem(QString.fromUtf8('<='),QVariant('<='))
            if has_method(cmp,'__lt__'):
                operatorInput.addItem(QString.fromUtf8('<'),QVariant('<'))
            if has_method(cmp,'__ge__'):
                operatorInput.addItem(QString.fromUtf8('>='),QVariant('>='))
            if has_method(cmp,'__gt__'):
                operatorInput.addItem(QString.fromUtf8('>'),QVariant('>'))
            #if has_method(cmp,'__nonzero__'):
                #operatorInput.addItem(QString.fromUtf8('>'),QVariant('>'))
            #if has_method(cmp,'in_'):
                #operatorInput.addItem(QString.fromUtf8('in'),QVariant('in'))
            if has_method(cmp,'like'):
                operatorInput.addItem(QString.fromUtf8(self._operatorTranslation['LIKE']),
                                      QVariant('LIKE'))

        else:
            operatorInput.clear()
            operatorInput.addItem(QString.fromUtf8('='),QVariant('='))
            
    def getValueEditor(self, parent, currentProperty):
        try:
            return self._mapper.getWidget(currentProperty, parent)
        except KeyError:
            return QLineEdit(parent)
    
    def buildFilter(self, clauses):
        
        #crit = self._queryBuilder.propertyName2Class['zustand.baujahrklasseId'].baujahrklasseId == 15
        #print type(crit)
        #print query.filter(crit)
        #print query
        
        pathClauses = []
        conjunctions = []
        
        for clause in clauses:
            field = unicode(clause.column.toString())
            pc = PathClause(field)
            if not clause.value.isNull():
                col = variant_to_pyobject(clause.column)
                if isinstance(col, basestring) and len(col):
                    pc = self.buildPathClause(col,
                                              variant_to_pyobject(clause.operator),
                                              variant_to_pyobject(clause.value),
                                              variant_to_pyobject(clause.matches))
                    pathClauses.append(pc)
                    if not clause.conjunction.isNull():
                        conjunctions.append(variant_to_pyobject(clause.conjunction))
                    else:
                        conjunctions.append('AND')
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
        else:
            filter = None
        return filter
        #return self._queryBuilder.getQuery(self._mapper.session, filter=filter, **kwargs)
        
            
    def buildPathClause(self, field, operator, value, matches):
        pc = PathClause(field)
        if isinstance(value, basestring):
            value = value.replace("%",'[%]')
            value = value.replace("*",'%')
            
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