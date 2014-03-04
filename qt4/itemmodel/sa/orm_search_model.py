'''
Created on 14.06.2011

@author: michi
'''
import datetime, logging

from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant,\
     QString, QDateTime, pyqtSlot, pyqtSignal

from PyQt4.QtGui import QColor

from sqlalchemy.orm import object_mapper
from sqlalchemy.orm.collections import InstrumentedList
from ems import qt4
from ems.thirdparty.odict import OrderedDict
from ems.model.sa.orm.querybuilder import SAQueryBuilder, OrderByClause
from ems.qt4.util import variant_to_pyobject, VariantContainer
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError

class SAOrmSearchModel(QAbstractTableModel):
    
    error = pyqtSignal(Exception)
    
    def __init__(self,session, queriedObject, querybuilder=None, filter=None,
                 columns = [],
                 appendOptions = None,
                 editable = False,
                 orderBy=None,
                 groupBy=None):
        super(SAOrmSearchModel, self).__init__()
        self._session = session
        
        if querybuilder is None:
            querybuilder = SAQueryBuilder(queriedObject)
        self._queryBuilder = querybuilder
        
        self.__didPerform = False
        self._queriedObject = queriedObject
        self._currentlyEditedRow = None
        self._resultCache = {}
        self._objectCache = {}
        self._headerCache = {}
        self.sectionFriendlyNames = {}
        self._defaultColumns = [] 
        self._columns = columns
        self._ormProperties = None
        self.editable = editable
        self._unsubmittedRows = []
        self._lastCreatedHash = None

        if not len(self._columns):
            self._columns = self.possibleColumns
            
        self._appendOptions = appendOptions
        self._mapper = None
        
        self._flagsCache = {}
        self._filter = filter
        self._orderBy = orderBy
        self._groupBy = groupBy
        
        try:
            self._queryBuilder.propertyNames
        except KeyError, e:
            logging.getLogger(__name__).warning(unicode(e))
            logging.getLogger(__name__).warning("Mein Objekt: {0}".format(self._queriedObject))
            raise e    
        
        self._query = None
        self._headerNameCache = {}
        
        
        self._columnName2Index = self._buildReversedColumnLookup(columns)
        self._dirty = True
        self.unsubmittetColor = QColor('#ffff00')
    
    @property
    def lastCreatedHash(self):
        return self._lastCreatedHash
    
    @property
    def queriedObject(self):
        return self._queriedObject
    
    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column, object=0)
    
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
        #only update if data/rowCount/... was called
        if self.__didPerform:
            self.perform()
    
    filter = property(getFilter, setFilter)
    
    def getOrderBy(self):
        return self._orderBy
    
    def setOrderBy(self, *args):
        if len(args) < 1:
            raise TypeError("setOrderBy needs 1 parameter as minimum")
        self._orderBy = args
        self._dirty = True
        #only update if data/rowCount/... was called
        if self.__didPerform:
            self.perform()
    
    orderBy = property(getOrderBy, setOrderBy)
            
    
    def sort(self, column, sortOrder=Qt.AscendingOrder):
        col = self.getPropertyNameByIndex(column)
        if sortOrder == Qt.AscendingOrder:
            self.orderBy = col
        else:
            self.orderBy = OrderByClause(col, OrderByClause.DESC)
    
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
        #Only perform is someome has called data()/rowCount()/etc...
        if self.__didPerform:
            self.perform()
    
    columns = property(getColumns, setColumns)
    
    @property
    def session(self):
        return self._session
    
    def rowCount(self, index=QModelIndex()):
        self.perform()
        #print "rowCount called %s" % len(self._objectCache)
        return len(self._objectCache)
    
    def columnCount(self, index=QModelIndex()):
        self.perform()
        return len(self._columns)
    
    def getPropertyNameByIndex(self, index):
        return self._columns[index]
    
    def getIndexByPropertyName(self, name):
        return self._columnName2Index[name]
    
    def extractObject(self, currentObj, index, propertyName):
        if hasattr(currentObj, propertyName):
            return currentObj
        else:
            if propertyName.find('.'):
                stack = propertyName.split('.')
                value = self._extractObject(currentObj, stack)
                if value is not None:
                    return value
                
    def _extractObject(self, obj, pathStack):
        if(hasattr(obj, pathStack[0])):
            if len(pathStack) < 2:
                return obj.__getattribute__(pathStack[0])
            nextObj = obj.__getattribute__(pathStack[0])
            pathStack.pop(0)
            if len(pathStack) == 1:
                if(hasattr(nextObj,pathStack[0])):
                    return nextObj
            if len(pathStack) > 1:
                return self._extractObject(nextObj, pathStack)
    
    def extractValue(self, currentObj, index, propertyName):
        
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
                
        return None
    
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
    
    def _castToVariant(self, value):
        if isinstance(value, basestring):
            return QVariant(unicode(value)) 
#        elif hasattr(value.__class__,'__ormDecorator__'):
#            return QVariant(value.__class__.__ormDecorator__().getReprasentiveString(value))
        elif isinstance(value, datetime.datetime):
            return QVariant(QDateTime(value.year, value.month, value.day,
                                      value.hour, value.minute, value.second))
        elif isinstance(value, (dict, list)):
            return QVariant(VariantContainer((value,)))
        return QVariant(value)
    
    def data(self, index, role=Qt.DisplayRole):
        
        self.perform()
        
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()
        
        if role in (Qt.DisplayRole, Qt.EditRole):
            if self._objectCache.has_key(index.row()):
                #Not currently inserted
                if self._resultCache.has_key(index.row()):
                    if self._resultCache[index.row()].has_key(index.column()):
                        return self._resultCache[index.row()][index.column()]
                    
                    columnName = self.getPropertyNameByIndex(index.column())
                    value = self.extractValue(self._objectCache[index.row()], index,
                                              columnName)
                    
                    self._resultCache[index.row()][index.column()] = self._castToVariant(value)
                    return self._resultCache[index.row()][index.column()]
                #currently inserted
                else:
                    columnName = self.getPropertyNameByIndex(index.column())
                    return self.extractValue(self._objectCache[index.row()],
                                         index, columnName)
        
        if role == qt4.ColumnNameRole:
            return QVariant(unicode(self.getPropertyNameByIndex(index.column())))
        if role == qt4.RowObjectRole:
            return QVariant(self.getObject(index.row()))
        
        return QVariant()
    
    def setData(self, index, value, role=Qt.EditRole):
        self.perform()
        columnName = self.getPropertyNameByIndex(index.column())
        val = variant_to_pyobject(value)
        #print "setData {0} {1} {2}".format(columnName, val, type(val))
        
        #oldValue = self._objectCache[index.row()].__getattribute__(columnName)
        currentObj = self._objectCache[index.row()]
        
        targetObj = self.extractObject(currentObj, index, columnName)
        targetProperty = columnName.split('.')[-1:][0]
        
#        print "targetObject: {0} {1} {2}".format(targetObj, type(targetObj),
#                                                     targetProperty)
        if targetObj is None:
            #if it is a new object, try to create the foreign object
            
            #retrieve the parent object
            nameStack = columnName.split('.')
            currentStackObj = currentObj
            lastStackObj = currentObj
            tmpStack = []
            for node in nameStack:
                tmpStack.append(node)
                currentStackObj = self.extractObject(currentStackObj,
                                                     index,
                                                     node)
                if currentStackObj is None:
                    currentStackObj = lastStackObj.createRelatedObject(lastStackObj, tmpStack[-2])
                    if not currentStackObj:
                        break
                    
                lastStackObj = currentStackObj
            
            if lastStackObj:
                targetObj = lastStackObj
                
#            try:
#                parentName = '.'.join(columnName.split('.')[:-1])
#                if '.' in parentName:
#                    parentNode = parentName.split('.')[-1]
#                else:
#                    parentNode = parentName
#                 
#                #print "parentName: %s" % parentName
#                parentObj = self.extractObject(currentObj, index, parentName)
#                result = parentObj.createRelatedObject(parentObj, parentNode)
#                if result:
#                    targetObj = parentObj.__getattribute__(parentNode)
#            except IndexError:
#                pass
        
        if not hasattr(targetObj,targetProperty):
            msg = "TargetObj {0} has no attribute {1}".format(targetObj,
                                                              targetProperty)
            raise AttributeError(msg)
        else:
            oldValue = targetObj.__getattribute__(targetProperty)
            
            if oldValue != val:
                targetObj.__setattr__(targetProperty, val)
                try:
                    del self._resultCache[index.row()][index.column()]
                except KeyError:
                    pass
                self.dataChanged.emit(index, index)
#                print self._session.dirty
                return True
            return False
    
    @pyqtSlot()
    def submit(self):
        try:
            self._session.commit()
            self._unsubmittedRows = []
            return True
        except SQLAlchemyError as e:

            self._session.rollback()
            for row in self._unsubmittedRows:
                self._session.add(self._objectCache[row])
            
            self.error.emit(e)
            return False
    
    @pyqtSlot()
    def revert(self):
        #print "reject called"
        self._session.rollback()
        if len(self._unsubmittedRows):
            self._unsubmittedRows.reverse()
            for row in self._unsubmittedRows:
                self.removeRow(row)
        super(SAOrmSearchModel, self).revert()
        self.forceReset()
    
    def _createNewOrmObject(self):
        srcClass = self._queriedObject.__class__

        newObj = srcClass.__new__(srcClass)
        newObj.__init__()

        return newObj

    def insertRows(self, row, count, parent=QModelIndex()):
        if count > 1:
            raise NotImplementedError("Currently only one row can be inserted")
        rowCount = self.rowCount(parent)
        if row != rowCount:
            raise NotImplementedError("Currently the row can be inserted at the end")

        newObj = self._createNewOrmObject()
        self.beginInsertRows(parent, row, row)
        self._currentlyEditedRow = row
        self._session.add(newObj)
        self._objectCache[row] = newObj
        self._unsubmittedRows.append(row)
        self._lastCreatedHash = hash(newObj)
        self.endInsertRows()
        return True
    
    def removeRows(self, row, count, parentIndex=QModelIndex()):
        if count > 1:
            raise NotImplementedError("Currently only one row can be removed")
        self.beginRemoveRows(parentIndex, row, row)
        #self._session.delete()
        obj = self._objectCache[row]
        try:
            self._session.delete(obj)
        except InvalidRequestError:
            pass
        del self._objectCache[row]
        
        if row in self._unsubmittedRows:
            self._unsubmittedRows.remove(row)
            
        try:
            del self._resultCache[row]
        except KeyError:
            pass
        #print obj.benutzer
        self.endRemoveRows()
        self.submit()
        
        return True
    
    def didPerform(self):
        return self.__didPerform
    
    def getObject(self, row):
        self.perform()
        if self._objectCache.has_key(row):
            return self._objectCache[row]

    def getObjectByHash(self, objectHash):
        self.perform()
        for row in self._objectCache:
            if hash(self._objectCache[row]) == objectHash:
                return self._objectCache[row]

    def getRowByHash(self, objectHash):
        self.perform()
        for row in self._objectCache:
            if hash(self._objectCache[row]) == objectHash:
                return row


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))

        if role == qt4.ColumnNameRole and orientation == Qt.Horizontal:
            return QVariant(self.getPropertyNameByIndex(section))

        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            if self.sectionFriendlyNames.has_key(section):
                return self.sectionFriendlyNames[section]
            columnName = unicode(self.getPropertyNameByIndex(section))
            name = self.getPropertyFriendlyName(columnName)

            return QVariant(name)
#        else:
#            print "headerData: {0}".format(variant_to_pyobject(QVariant(int(section + 1))))
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
    
    
    def flags(self, index):
        if not self.editable:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        
#            return Qt.ItemIsSelectable | Qt.ItemIsEnabled  | Qt.ItemIsEditable
        
        
        
        if not self._flagsCache.has_key(index.column()):
            propertyName = self.getPropertyNameByIndex(index.column())
            if self._queryBuilder.isAutoProperty(propertyName):
                flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
            else:
                flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
            self._flagsCache[index.column()] = flags
        return self._flagsCache[index.column()]
        
    def isDataChanged(self):
        return self._session.dirty
    
    def forceReset(self):
        self._dirty = True
        self.perform()
    
    def perform(self):
        
        if not self._dirty:
            return

        self.__didPerform = True
        #self.beginResetModel()
        #print "%s : I actually perform" % self._queriedObject
        #print self._session.get_bind(self._queriedObject)
        i = 0

        self.beginResetModel()

        self._resultCache.clear()
        self._objectCache.clear()
        self._headerCache.clear()
        self._flagsCache.clear()

        query = self._queryBuilder.getQuery(self._session,
                                            propertySelection=self._columns,
                                            filter=self._filter,
                                            appendOptions=self._appendOptions,
                                            orderBy=self._orderBy,
                                            groupBy=self._groupBy)
#        print query
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
        self.layoutChanged.emit()
        self.headerDataChanged.emit(Qt.Vertical, 0, self.rowCount(QModelIndex()))
        
    