'''
Created on 14.06.2011

@author: michi
'''
from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant, QString

from sqlalchemy.orm import object_mapper, ColumnProperty, RelationshipProperty

from ems import qt4
from ems.thirdparty.odict import OrderedDict

class SAOrmSearchModel(QAbstractTableModel):
    def __init__(self,session, queriedObject, querybuilder, columns = []):
        super(SAOrmSearchModel, self).__init__()
        self._session = session
        self._queriedObject = queriedObject
        self._resultCache = {}
        self._columns = columns
        self._mapper = None
        self._ormProperties = None
        self._flagsCache = {}
        self._queryBuilder = querybuilder
        self._headerNameCache = {}
        if not len(self._columns):
            self._columns = self._buildDefaultColumns()
        self._columnName2Index = self._buildReversedColumnLookup(columns)
        self._dirty = True
    
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
    
    
    def _buildDefaultColumns(self):
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
    
    @property
    def session(self):
        return self._session
    
    def rowCount(self, index=QModelIndex()):
        self.perform()
        return len(self._resultCache)
    
    def columnCount(self, index=QModelIndex()):
        self.perform()
        return len(self._columns)
    
    def getPropertyNameByIndex(self, index):
        return self._columns[index]
    
    def getIndexByPropertyName(self, name):
        return self._columnName2Index[name]
    
    def extractValue(self, index, propertyName):
        
        currentObj = self._resultCache[index.row()]
        if hasattr(currentObj, propertyName):
            return currentObj.__getattribute__(propertyName)
        else:
            if propertyName.find('.'):
                stack = propertyName.split('.')
                value = self._extractValue(currentObj, stack)
                if value:
                    return value
                
        return "*Nichts*"
    
    def _extractValue(self, obj, pathStack):
        
        if(hasattr(obj, pathStack[0])):
            if len(pathStack) < 2:
                return obj.__getattribute__(pathStack[0])
            nextObj = obj.__getattribute__(pathStack[0])
            pathStack.pop(0)
            return self._extractValue(nextObj, pathStack)
            
    
    def data(self, index, role=Qt.DisplayRole):
        self.perform()
        columnName = self.getPropertyNameByIndex(index.column())
        #return QVariant()
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()
        if role in (Qt.DisplayRole, Qt.EditRole):
            #print self._resultCache[index.row()]
            #value = self._resultCache[index.row()].__getattribute__(columnName)
            value = self.extractValue(index, columnName)
            #print value
#            if self._queriedObject.__name__ == 'Gruppe':
#                print "row:%s col:%s role:%s value:%s" % (index.row(), index.column(), role, value)
            if isinstance(value, basestring):
                return QVariant(unicode(value))
            elif hasattr(value.__class__,'__ormDecorator__'):
                return QVariant(value.__class__.__ormDecorator__().getReprasentiveString(value))
            return QVariant(value)
        if role == qt4.ColumnNameRole:
            return QVariant(unicode(self._queryBuilder.currentColumnList[index.column()]))
        return QVariant()
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            columnName = unicode(self.getPropertyNameByIndex(section))
            if not self._headerNameCache.has_key(columnName):
                fieldName = columnName.split('.')[-1:][0]
                #print "%s %s" % (columnName, columnName.split('.')[-1:][0])
                try:
                    dec = self._queryBuilder.propertyName2Class[columnName].__ormDecorator__()
                    name = dec.getPropertyFriendlyName(fieldName)
                    
                except KeyError:
                    name = fieldName
                self._headerNameCache[columnName] = QString.fromUtf8(name)

            return QVariant(self._headerNameCache[columnName])
        return QVariant(int(section + 1))
    
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
    
    
    def perform(self):
        if not self._dirty:
            return
        #self.beginResetModel()
        #print "%s : I actually perform" % self._queriedObject
        #print self._session.get_bind(self._queriedObject)
        i = 0
        for obj in self._session.query(self._queriedObject).all():
            self._resultCache[i] = obj
            i += 1
        self._dirty = False