'''
Created on 14.06.2011

@author: michi
'''
import datetime

from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant,\
     QString, QDateTime

from sqlalchemy.orm import object_mapper, ColumnProperty, RelationshipProperty
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.util import NamedTuple
from ems import qt4
from ems.thirdparty.odict import OrderedDict

class SAOrmSearchModel(QAbstractTableModel):
    def __init__(self,session, queriedObject, querybuilder, filter=None,
                 columns = [],
                 dataListener=None,
                 appendOptions = None):
        super(SAOrmSearchModel, self).__init__()
        self._session = session
        self.__dataListener = dataListener
        self._queriedObject = queriedObject
        self._resultCache = {}
        self._objectCache = {}
        self._headerCache = {}
        self._columns = columns
        if not len(self._columns):
            self._columns = self.possibleColumns
        self._appendOptions = appendOptions
        self._mapper = None
        self._ormProperties = None
        self._flagsCache = {}
        self._queryBuilder = querybuilder
        self._filter = filter
        self._askCount = 0
        
        try:
            self._queryBuilder.propertyNames
        except KeyError, e:
            print e
            print "Mein Objekt: %s" % self._queriedObject
            raise e    
        
        self._query = None
        self._headerNameCache = {}
        self._defaultColumns = []
        
        self._columnName2Index = self._buildReversedColumnLookup(columns)
        self._dirty = True
    
    @property
    def queryBuilder(self):
        return self._queryBuilder
    
    def getQuery(self):
        return self._query
    
    def setQuery(self, query):
        #TODO: Dirty Fix wegen eagerload, welches nicht beim Setzen der Columns ausgefuehrt wird
        raise NotImplementedError("This feature has been throwed out")
        self._query = query
        self._dirty = True
        self.perform()
    
    query = property(getQuery, setQuery)
    
    def getFilter(self):
        return self._filter
    
    def setFilter(self, filter):
        self._filter = filter
        self._dirty = True
        self.perform()
    
    filter = property(getFilter, setFilter)
    
    @property
    def mapper(self):
        if self._mapper is None:
            self._mapper = object_mapper(self._queriedObject())
        return self._mapper
    
    
    @property
    def ormProperties(self):
        if self._ormProperties is None:
            self._ormProperties = OrderedDict()
            for propertyName in self._queryBuilder.propertyNamesDecorated:
                self._ormProperties[propertyName] = \
                    self._queryBuilder.properties[propertyName]
                #self._ormProperties.append(property)
        return self._ormProperties
    
    @property
    def possibleColumns(self):
        if not len(self._defaultColumns):
            self._defaultColumns = self.__buildDefaultColumns()
        return self._defaultColumns
        
    def __buildDefaultColumns(self):
        columns = []
        for property in self.ormProperties.keys():
            columns.append(property)
        return columns
    
    def _buildReversedColumnLookup(self, columns):
        i = 0
        reversed = {}
        for column in columns:
            reversed[str(column)] = i
            i += 1
        return reversed
    
    def getColumns(self):
        return self._columns
    
    def setColumns(self, cols):
        self._columns = cols
        self._dirty = True
        self.perform()
    
    columns = property(getColumns, setColumns)
    
    @property
    def session(self):
        return self._session
    
    def rowCount(self, index=QModelIndex()):
        self.perform()
        return len(self._objectCache)
    
    def columnCount(self, index=QModelIndex()):
        self.perform()
        return len(self._columns)
    
    def getPropertyNameByIndex(self, index):
        return self._columns[index]
    
    def getIndexByPropertyName(self, name):
        return self._columnName2Index[name]
    
    def extractValue(self, index, propertyName):
        
        currentObj = self._objectCache[index.row()]
        
        if hasattr(currentObj, propertyName):
            return currentObj.__getattribute__(propertyName)
        else:
            if propertyName.find('.'):
                stack = propertyName.split('.')
                value = self._extractValue(currentObj, stack)
                if value is not None:
                    return value
#                else:
#                    print propertyName,type(value)
                
        return "*Nichts*"
    
    def _extractValue(self, obj, pathStack):
        
        if(hasattr(obj, pathStack[0])):
            if len(pathStack) < 2:
                return obj.__getattribute__(pathStack[0])
            nextObj = obj.__getattribute__(pathStack[0])
            pathStack.pop(0)
            return self._extractValue(nextObj, pathStack)
    
    def _preloadMultipleRowsResult(self, res, multiRowProperties):
        i = 0
        
        nonMultiCols = []
        multicols = []
        if len(multiRowProperties) > 1:
            raise NotImplementedError("At the moment I can only handle 1 1:n or m:n relation")
        
        for col in self.columns:
            for mProp in multiRowProperties:
                if col.startswith(mProp):
                    multicols.append(col)
                else:
                    nonMultiCols.append(col)
#        print nonMultiCols
#        print '-----------'
#        print multicols
#        
        #return
        
        for obj in res:
#            print "Next Object %s----------------" % i
            multipleRowsObjects = []
            

            self._resultCache[i] = {}
            
            for colName in nonMultiCols:
                if hasattr(obj, colName):
                    value = obj.__getattribute__(colName)
                    self._resultCache[i][self._columns.index(colName)] = self._castToVariant(value)
                    
                    #print colName,value
                else:
                    if colName.find('.'):
                        stack = colName.split('.')
                        
                        value = self._extractMultiValue(obj, stack)
                        self._resultCache[i][self._columns.index(colName)] = self._castToVariant(value)
#                        if isinstance(value, InstrumentedList):
#                            print colName, type(value)
#                            for ormObj in value:
#                                print ormObj.name,self._extractMultiValue(ormObj,stack)
#                                i2 += 1
            self._objectCache[i] = obj
            #Create ResultCache Structure
            
            
            for joinName in multiRowProperties:
                stack = joinName.split('.')
                childs = self._extractMultiValue(obj, stack)
                if isinstance(childs, InstrumentedList):
                    childCount = 0
                    for child in childs:
                        if childCount > 0:
                            i += 1
                            self._objectCache[i] = obj
                            self._resultCache[i] = {}
                            
                        for childCol in multicols:
                            if childCol == joinName:
                                childColName = ""
                                value = child
                            else:
                                childColName = childCol.replace(joinName + '.',"")
                                value = self._extractMultiValue(child, childColName.split('.'))
                            self._resultCache[i][self._columns.index(childCol)] = self._castToVariant(value)
#                            print "%childCol %s value: %s" % (childCol,value)
#                        print "%s has %s Childs" % (obj.id,childCount)
                        childCount += 1
#                        print child
                #print "joinStack: %s %s" % (stack, value)
            i += 1
            
        
        #print "%s Objekte mit 1:n %s" % (i, i2)
#                        else:
#                            print colName,type(value)
#        else:
#            print "%s has no %s" % (obj, pathStack[0])
    
    def _extractMultiValue(self, obj, pathStack):
        
        
        if(hasattr(obj, pathStack[0])):
#            print pathStack
            if len(pathStack) < 2:
                value = obj.__getattribute__(pathStack[0])
#                if isinstance(value, InstrumentedList):
#                    print value
                return value
            nextObj = obj.__getattribute__(pathStack[0])
#            print "nextObj %s" % obj.__class__.__name__
            pathStack.pop(0)
#            if len(pathStack):
#                if hasattr(nextObj, pathStack[0]):
#                    next2Obj = nextObj.__getattribute__(pathStack[0])
#                    if isinstance(next2Obj, InstrumentedList):
#                        print "next2Obj %s" % pathStack
            return self._extractMultiValue(nextObj, pathStack)
        elif isinstance(obj, InstrumentedList):
#            print "{0} is multiple".format(pathStack)
            return obj
            
    def getDataListener(self):
        return self.__dataListener
    
    def setDataListener(self, dataListener):
        self.__dataListener = dataListener
    
    def delDataListener(self):
        self.__dataListener = None
        
    dataListener = property(getDataListener,setDataListener,delDataListener)
    
    def _castToVariant(self, value):
        if isinstance(value, basestring):
            return QVariant(unicode(value)) 
        elif hasattr(value.__class__,'__ormDecorator__'):
            return QVariant(value.__class__.__ormDecorator__().getReprasentiveString(value))
        elif isinstance(value, datetime.datetime):
            return QVariant(QDateTime(value.year, value.month, value.day,
                                      value.hour, value.minute, value.second)) 
        return QVariant(value)
    
    def data(self, index, role=Qt.DisplayRole):
        #return QVariant()
        self._askCount += 1
        if self.__dataListener is not None:
            self.__dataListener.data(index, role)
        self.perform()
        
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()
        
        if role in (Qt.DisplayRole, Qt.EditRole):
            if self._resultCache[index.row()].has_key(index.column()):
                #print "cacheHit %s" % self._askCount
                return self._resultCache[index.row()][index.column()]
#            else:
#                print "no cacheHit %s" % self._askCount
            
            columnName = self.getPropertyNameByIndex(index.column())
#            print "Hole %s" % columnName
            value = self.extractValue(index, columnName)
            
#            print columnName, value, type(value)
            self._resultCache[index.row()][index.column()] = self._castToVariant(value)
            return self._resultCache[index.row()][index.column()]
        
        if role == qt4.ColumnNameRole:
#            print "columnNameRole"
            return QVariant(unicode(self._queryBuilder.currentColumnList[index.column()]))
        return QVariant()
    
    def getObject(self, row):
        if self._objectCache.has_key(row):
            return self._objectCache[row]
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        #print "headerData"
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            columnName = unicode(self.getPropertyNameByIndex(section))
            name = self.getPropertyFriendlyName(columnName)

            return QVariant(name)
        return QVariant(int(section + 1))
    
    def getPropertyFriendlyName(self, propertyPath):
        if not self._headerNameCache.has_key(propertyPath):
            fieldName = propertyPath.split('.')[-1:][0]
            #print "%s %s" % (columnName, columnName.split('.')[-1:][0])
            try:
                dec = self._queryBuilder.propertyName2Class[propertyPath].__ormDecorator__()
                name = dec.getPropertyFriendlyName(fieldName)
                
            except KeyError:
                name = fieldName
            self._headerNameCache[propertyPath] = QString.fromUtf8(name)
            
        return self._headerNameCache[propertyPath]
    
    def isPrimaryKey(self, index):
        self._flagsCache
        
        print 
    
#    def flags(self, index):
#        
#        propertyName = self.getPropertyNameByIndex(index.column())
#        if not self._flagsCache.has_key(propertyName):
#            isPk = False
#            if isinstance(self.ormProperties[propertyName], ColumnProperty):
#                for col in self.ormProperties[propertyName].columns:
#                    if col.primary_key:
#                        isPk = True
#                if not isPk:
#                    self._flagsCache[propertyName] = Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled
#                else:
#                    self._flagsCache[propertyName] = Qt.ItemIsSelectable | Qt.ItemIsEnabled
#            else:
#                self._flagsCache[propertyName] = Qt.ItemIsSelectable | Qt.ItemIsEnabled
#                
#        return self._flagsCache[propertyName]

    
    def isDataChanged(self):
        return self._session.dirty
    
    def forceReset(self):
        self._dirty = True
        self.perform()
    
    def perform(self):
        
        if not self._dirty:
            return
        #self.beginResetModel()
        #print "%s : I actually perform" % self._queriedObject
        #print self._session.get_bind(self._queriedObject)
        i = 0
        
        self.beginResetModel()
        
        self._resultCache.clear()
        self._objectCache.clear()
        self._headerCache.clear()
        self._askCount = 0
        query = self._queryBuilder.getQuery(self._session,
                                            propertySelection=self._columns,
                                            filter=self._filter,
                                            appendOptions=self._appendOptions)
        
        multipleRowsPerObject = self._queryBuilder.hasMultipleRowProperties(self._columns)
        #Check if multiple Objects per row are requested (1:n,m:n,...)
        if multipleRowsPerObject:
            self._preloadMultipleRowsResult(query.all(), multipleRowsPerObject)
        else:
            for obj in query.all():
    #            if isinstance(obj, NamedTuple):
    #                self._objectCache[i] = obj[0]
    #            else:
                self._objectCache[i] = obj
                #Create ResultCache Structure
                self._resultCache[i] = {}
                i += 1
        self._dirty = False
        self.endResetModel()