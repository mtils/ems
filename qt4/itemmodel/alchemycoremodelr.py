'''
Created on 09.01.2011

@author: michi
'''

from PyQt4.QtCore import QAbstractTableModel,QVariant, Qt, QModelIndex

from sqlalchemy import Table
from sqlalchemy.sql.expression import _UnaryExpression,Alias
from sqlalchemy.sql.operators import asc_op,desc_op
import sqlalchemy.schema
from sqlalchemy.sql import func

from ems import qt4


class AlchemyCoreModelR(QAbstractTableModel):
    
    asc = 1
    desc = 2
    
    def __init__(self,con,queryBuilder,dataListener=None):
        '''
        die originale Query beinhaltet:
        from
        where
        KEIN order_by
        KEIN offset
        KEIN limit
        '''
        queryBuilder.setDirtyListener(self.forceReset)
        self._queryBuilder = queryBuilder
        self._connection = con
        self.__labeled2DottedColumn = None
        self._resultCache = {}
        super(AlchemyCoreModelR, self).__init__()
        self._dirty = True
        self.__lastSortByIndex = None
        self.__lastSortByOrder = None
        self._inResetProgress = False
        self.__dataListener = dataListener

        self.__limit = None
        self.__offset = None
        self.columnHeaderTranslated = {}
    
    @property
    def queryBuilder(self):
        return self._queryBuilder
    
    def getLimit(self):
        return self.__limit
    
    def setLimit(self,limit,skipReset=False):
        if isinstance(limit, tuple):
            self.__offset = limit[0]
            self.__limit = limit[1]
        else:
            self.__limit = limit
            
        if not skipReset:
            self.forceReset()
        
    def delLimit(self):
        self.__limit = None
        self.forceReset()
    
    limit = property(getLimit, setLimit, delLimit,
                     "Set limit (and offset) part of tplQuery")
    
    def getOffset(self):
        return self.__offset
    
    def setOffset(self,offset,skipReset=False):
        if isinstance(offset,tuple):
            self.__offset = offset[0]
            self.__limit = offset[1]
        else:
            self.__offset = offset
        if not skipReset:
            self.forceReset()
    
    def delOffset(self):
        self.__offset = None
        self.forceReset()
    
    offset = property(getOffset, setOffset, delOffset,
                      "Set offset (and limit) part of tplQuery")
    
    def getDottedColumnNameOfLabeled(self,labeledName):
        if self.__labeled2DottedColumn is None:
            self.__labeled2DottedColumn = {}
            for column in self._queryBuilder.possibleColumns:
                columnName = str(column)
                self.__labeled2DottedColumn[columnName.replace('.', '_')] = \
                    str(columnName)
        return self.__labeled2DottedColumn[labeledName]
    
    def buildQuery(self,skipLimit=False,skipOffset=False):
        query = self._queryBuilder.getQuery()

        if self.__offset is not None and not skipOffset:
            query = query.offset(self.__offset)
            
        if self.__limit is not None and not skipLimit:
            query = query.limit(self.__limit)
        
        return query
    
    def getDataListener(self):
        return self.__dataListener
    
    def setDataListener(self, dataListener):
        self.__dataListener = dataListener
    
    def delDataListener(self):
        self.__dataListener = None
        
    dataListener = property(getDataListener,setDataListener,delDataListener)    
    
    def data(self, index, role=Qt.DisplayRole):
        if self.__dataListener is not None:
            self.__dataListener.data(index, role)
        self.perform()
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()
        if role == Qt.DisplayRole:
            value = self._resultCache[index.row()][index.column()]
            if isinstance(value, basestring):
                return QVariant(unicode(value))
            return QVariant(value)
        if role == qt4.ColumnNameRole:
            return QVariant(unicode(self._queryBuilder.currentColumnList[index.column()]))
        return QVariant()
    
    def rowCount(self, index=QModelIndex()):
        self.perform()
        return len(self._resultCache)
    
    def columnCount(self, index=QModelIndex()):
        self.perform()
        return len(self._queryBuilder.currentColumnList)
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
#            labeled = str(self.currentColumnList[section])
#            return QVariant(self.getDottedColumnNameOfLabeled(labeled))
            columnName = unicode(self._queryBuilder.currentColumnList[section])
            if self.columnHeaderTranslated.has_key(columnName):
                return QVariant(self.columnHeaderTranslated[columnName])
            return QVariant(columnName)
        return QVariant(int(section + 1))
    
    def perform(self):
        if not self._dirty and not self._queryBuilder.dirty:
            return
        
        self._inResetProgress = True
        lastPerformedQuery = self.buildQuery()
        labeledQuery = lastPerformedQuery.apply_labels()
        #print labeledQuery
        sqlResult = self._connection.execute(labeledQuery)
        self._resultCache.clear()
        
        i=self.getCacheIndexOffset()
        for row in sqlResult:
            self._resultCache[i] = row
            i += 1
        
#        self.currentColumnList = []
#        for column in labeledQuery.inner_columns:
#            self.currentColumnList.append(column)
            
        self._dirty = False
        self._inResetProgress = False
        self.reset()
    
    def getCacheIndexOffset(self):
        return 0
    
    def sort(self,columnIndex,order):
        #Fast lookup to not poll any methods
        if self.__lastSortByIndex == columnIndex and \
            self.__lastSortByOrder == order:
            return
        self.__lastSortByIndex = columnIndex
        self.__lastSortByOrder = order
        
        column = self._queryBuilder.currentColumnList[columnIndex]
        
        orderByTuple = self._queryBuilder.orderBy
        
        #Look if previously the query was ordered and if so, the direction
        prevColumn = None
        prevDirection = None
        
        
        #No ORDER BY was set
        if orderByTuple is None:
            pass
        #Simple ORDER BY by Column Name
        elif isinstance(orderByTuple[0],sqlalchemy.schema.Column):
            prevColumn = orderByTuple[0]
            prevDirection = 'ASC'
        #ORDER BY desc() or asc()
        elif isinstance(orderByTuple[0],_UnaryExpression):
            prevColumn = orderByTuple[0].element
            if orderByTuple[0].modifier is asc_op:
                prevDirection = 'ASC'
            if orderByTuple[0].modifier is desc_op:
                prevDirection = 'DESC'
        
        #if new Col is the same as old, switch direction    
        if unicode(column) == unicode(prevColumn):
            if prevDirection == 'ASC':
                self._queryBuilder.setOrderBy(column.desc())
            else:
                self._queryBuilder.setOrderBy(column.asc())
        else:
            self._queryBuilder.setOrderBy(column.asc())
        
    def _cacheReset(self):
        self._dirty = True
        self.perform()
    
    def forceReset(self):
        return self._cacheReset()

class AlchemyCoreModelRBuffered(AlchemyCoreModelR):
    def __init__(self,con,queryBuilder,dataListener=None,distance=50):
        super(AlchemyCoreModelRBuffered, self).__init__(con,queryBuilder,
                                                        dataListener)
        self._dirty = False
        self.distance = distance
        self.__countQuery = None
        self.__totalCount = None;

    def getDistance(self):
        return self.__distance

    def setDistance(self, value):
        self.__distance = value
        self.__distanceHalf = value/2
        self.__distanceDouble = value*2

    def delDistance(self):
        del self.__distance

    def getCountQuery(self):
        if self.__countQuery is None:
            for row in self._queryBuilder.possibleColumns:
                col = row
                break
            return self.buildQuery(skipLimit=True,skipOffset=True)\
                .with_only_columns(
                     [func.count(col)]
                     )
        return self.__countQuery
    
    def rowCount(self, index=QModelIndex()):
        if self.__totalCount is None:
            self.__totalCount = self._connection.execute(self.countQuery).\
                                first()[0]
        return self.__totalCount

    def setCountQuery(self, value):
        self.__countQuery = value

    def delCountQuery(self):
        del self.__countQuery

    countQuery = property(getCountQuery, setCountQuery, delCountQuery, "countQuery's docstring")
    
    def data(self, index, role=Qt.DisplayRole):
        try:
            return super(AlchemyCoreModelRBuffered, self).data(index,role)
        except KeyError:
            if self._queryBuilder.dirty:
                self.__totalCount = None
                self.__countQuery = None
            self.fillCacheEntries(index.row())
            return super(AlchemyCoreModelRBuffered, self).data(index,role)
            
    def fillCacheEntries(self, notFoundRowNumber):
        if self._inResetProgress:
            return
#        print "###Row %s not found" % notFoundRowNumber
        limit = self.calculateLimit(notFoundRowNumber)
        self.setOffset(limit[0],True)
        self.setLimit(limit[1],True)
        
        sqlResult = self._connection.execute(self.buildQuery().apply_labels())
        i = limit[0]
        for row in sqlResult:
            self._resultCache[i] = row
            i += 1
        self._dirty = False
        self.reset()
        
    def getCacheIndexOffset(self):
        if self.offset is not None:
            return self.offset
        return 0
            
    
    def calculateLimit(self, notFoundIndex):
        lowerBoundary = notFoundIndex - (self.__distanceHalf)
        distanceFactor = lowerBoundary/self.__distance
        if distanceFactor < 0:
            distanceFactor = 0
        limitOffset = distanceFactor*self.__distance
        limit = self.__distanceDouble
        if limitOffset in self._resultCache:
            limitOffset += self.__distance
            limit = self.__distance
        return (limitOffset,limit)
    
    def forceReset(self):
        self.__countQuery = None
        self.__totalCount = None
        return super(AlchemyCoreModelRBuffered, self).forceReset()
    
    distance = property(getDistance, setDistance, delDistance, "distance's docstring")
    
    