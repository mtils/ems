'''
Created on 04.04.2011

@author: michi
'''

from sqlalchemy import Table, select, Column
from sqlalchemy.sql.expression import _UnaryExpression,Alias
from sqlalchemy.sql.operators import asc_op,desc_op
import sqlalchemy.schema
from sqlalchemy.sql import func


class FromCalculator(object):
    def __init__(self, fromConstruct):
        self._fromConstruct = fromConstruct
        
    def getFromObj(self, columnList=[], where=None, orderBy=None):
        return self._fromConstruct
    
    def getFromConstruct(self):
        return self._fromConstruct
    
    def setFromConstruct(self, fromConstruct):
        self._fromConstruct = fromConstruct

class FromCalculatorMinimal(FromCalculator):
    def __init__(self, mainTable):
        self._mainTable = mainTable
        self._joins = {}
    
    def addJoin(self,tableOrAlias,onClause=None,dependency=None,name=None):
        if name is None:
            name = tableOrAlias.description
        
        self._joins[name] = {'table':tableOrAlias,
                             'onClause':onClause,
                             'dependency':dependency}
    @property
    def joins(self):
        return self._joins
    
    @property
    def mainTable(self):
        return self._mainTable
    
    def _searchExpressionTables(self, exp, tables):
        if isinstance(exp, Column):
                colName = str(exp)
                tables.append(colName.split(".")[0])
        elif hasattr(exp, 'get_children'):
            for child in exp.get_children():
                if isinstance(child, Column):
                    colName = str(child)
                    tables.append(colName.split(".")[0])
                else:
                    self._searchExpressionTables(child, tables)
        
    def getCompleteFromObj(self):
        completeColumnList = []
        for name in self._joins:
            for col in self._joins[name]['table'].c:
                completeColumnList.append(col)
        return self.getFromObj(completeColumnList, None, None)
            
    def getFromObj(self, columnList=[], where=None, orderBy=None):
        
        neededTableNames = []
        for c in columnList:
            tableName = unicode(c).split('.')[0]
            if tableName not in neededTableNames:
                neededTableNames.append(tableName)
        
        whereTables = []
        self._searchExpressionTables(where, whereTables)
        for tableName in whereTables:
            if tableName not in neededTableNames:
                neededTableNames.append(tableName)
        
        orderByTables = []
        if orderBy is not None:
            for ob in orderBy:
                self._searchExpressionTables(ob, orderByTables)
            
        for tableName in orderByTables:
            if tableName not in neededTableNames:
                neededTableNames.append(tableName)
                
        fromObj = self._mainTable
        addedJoins = []
        for tableName in neededTableNames:
            if tableName != self._mainTable:
                fromObj = self._addJoin(fromObj, tableName, addedJoins)

        return fromObj
    
    def _addJoin(self, fromObj, tableName, addedJoins):
        
        if tableName in addedJoins:
            return fromObj
        
        if self._joins.has_key(tableName):
            
            if self._joins[tableName]['dependency'] is not None:
                fromObj = self._addJoin(fromObj, self._joins[tableName]['dependency'], addedJoins)
            
            if self._joins[tableName]['onClause'] is None:
                fromObj = fromObj.join(self._joins[tableName]['table'])
                addedJoins.append(tableName)
            else:
                fromObj = fromObj.join(self._joins[tableName]['table'],
                                       onclause=self._joins[tableName]['onClause'])
                addedJoins.append(tableName)
        return fromObj

class QueryBuilder(object):
    def __init__(self,  fromCalculator=None, fromObj=None, where=None,
                 orderBy=None, currentColumnlist=[], possibleColumns=None,
                 dirtyListener=None):
        self.__fromObj = fromObj
        self.__dirty = True
        self.__currentColumnList = currentColumnlist
        self.__possibleColumns = possibleColumns
        self.__where = where
        self._dirtyListener = dirtyListener
        if orderBy is not None:
            self.orderBy = orderBy
        else:
            self.__orderBy = orderBy
        
        self.__query = None
        
        if fromCalculator is None:
            if fromObj is None:
                raise TypeError("Either assign fromObj or FromCalculator")
            self.__fromCalculator = FromCalculator(fromObj)
        else:
            self.__fromCalculator = fromCalculator
    
    def setDirtyListener(self, clbl):
        self._dirtyListener = clbl
    
    def setFromObj(self, fromObj):
        self.__fromCalculator.setFromConstruct(fromObj)
        self.__fromObj = fromObj
    
    def getFromObj(self):
#        return self.__fromObj
        return self.__fromCalculator.getFromObj(self.currentColumnList,
                                                self.where,self.orderBy)
    
    fromObj = property(getFromObj,setFromObj,None,"Set from Part of query")
    
    def getWhere(self):
        return self.__where
    
    def setWhere(self,whereCondition):
        self.__where = whereCondition
        self._setDirty()
    
    def delWhere(self):
        self.__where = None
        self._setDirty()
    
    where = property(getWhere,setWhere,delWhere,"Set where part of tplQuery")
    
    def getOrderBy(self):
        return self.__orderBy
    
    def setOrderBy(self, orderBy):
        if isinstance(orderBy,tuple):
            self.__orderBy = orderBy
        else:
            self.__orderBy = (orderBy,)
        self._setDirty()
    
    def delOrderBy(self):
        self.__orderBy = None
        self._setDirty()
    
    orderBy = property(getOrderBy, setOrderBy, delOrderBy,
                       "Set order_by part of tplQuery")
    def getPossibleColumns(self):
        if self.__possibleColumns is None:
            self.__possibleColumns = self.getCompleteColumnList()
        return self.__possibleColumns
    
    def setPossibleColumns(self,columns):
        self.__possibleColumns = columns
    
    possibleColumns = property(getPossibleColumns,setPossibleColumns,None,"")
    
    def getCompleteColumnList(self):
        completeColumnList = []
        for fromCond in select(from_obj=self.__fromObj).locate_all_froms():
            if isinstance(fromCond, Table):
                for column in fromCond.columns:
                    completeColumnList.append(column)
            elif isinstance(fromCond,Alias):
                if isinstance(fromCond.original,Table):
                    for column in fromCond.c:
                        completeColumnList.append(column)
        return completeColumnList
    
    completeColumnList = property(getCompleteColumnList,None,None,'')
    
    def getCurrentColumnList(self):
        if not len(self.__currentColumnList):
            return self.possibleColumns
        return self.__currentColumnList
    
    def setCurrentColumnList(self, cList):
        self.__currentColumnList = cList
        self._setDirty()
    
    def delCurrentColumnList(self):
        self.__currentColumnList = []
        self._setDirty()
    
    currentColumnList = property(getCurrentColumnList,setCurrentColumnList,
                                 delCurrentColumnList,"Set current columnlist")
    
    def _setDirty(self):
        self.__dirty = True
        if self._dirtyListener is not None:
            self._dirtyListener()
    @property
    def dirty(self):
        return self.__dirty
    
    def getQuery(self):
        if self.__dirty:
            query = select(from_obj=self.getFromObj()).with_only_columns(self.currentColumnList)
            if self.__where is not None:
                query = query.where(self.__where)
            
            if self.__orderBy is not None:
                query = query.order_by(*self.__orderBy)

            self.__query = query
            self.__dirty = False
        return self.__query