'''
Created on 14.06.2011

@author: michi
'''

from collections import OrderedDict

from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant

from sqlalchemy.orm import object_mapper, ColumnProperty, RelationshipProperty

from ems import qt4

class AlchemyOrmModel(QAbstractTableModel):
    def __init__(self,session, queriedObject, columns = []):
        super(AlchemyOrmModel, self).__init__()
        self._session = session
        self._queriedObject = queriedObject
        self._resultCache = {}
        self._columns = columns
        self._mapper = None
        self._ormProperties = None
        self._flagsCache = {}
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
            for property in self.mapper.iterate_properties:
                self._ormProperties[property.key] = property
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
    
    def getPropertyNameByIndex_(self, index):
        return self._columns[index]
    
    def getIndexByPropertyName_(self, name):
        return self._columnName2Index[name]

    def nameOfColumn(self, index):
        return self._columns[index]
   
    def columnOfName(self, name):
        return self._columnName2Index[name]
    
    def data(self, index, role=Qt.DisplayRole):
        self.perform()
        columnName = self.nameOfColumn(index.column())
        #return QVariant()
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()
        if role in (Qt.DisplayRole, Qt.EditRole):
            value = self._resultCache[index.row()].__getattribute__(columnName)
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
            columnName = unicode(self.nameOfColumn(section))
#            if self.columnHeaderTranslated.has_key(columnName):
#                return QVariant(self.columnHeaderTranslated[columnName])
            return QVariant(columnName)
        return QVariant(int(section + 1))
    
    def isPrimaryKey(self, index):
        self._flagsCache

    def flags(self, index):
        
        propertyName = self.nameOfColumn(index.column())
        if not self._flagsCache.has_key(propertyName):
            isPk = False
            if isinstance(self.ormProperties[propertyName], ColumnProperty):
                for col in self.ormProperties[propertyName].columns:
                    if col.primary_key:
                        isPk = True
                if not isPk:
                    self._flagsCache[propertyName] = Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled
                else:
                    self._flagsCache[propertyName] = Qt.ItemIsSelectable | Qt.ItemIsEnabled
            else:
                self._flagsCache[propertyName] = Qt.ItemIsSelectable | Qt.ItemIsEnabled
                
        return self._flagsCache[propertyName]
    
    def setData(self, index, value, role=Qt.EditRole):
        columnName = self.nameOfColumn(index.column())
        pyValue = None
        if value.isNull():
            pyValue = None
        elif value.type() in (QVariant.Char,QVariant.String):
            pyValue = unicode(value.toString())
        elif value.type() == QVariant.Bool:
            pyValue = bool(value.toBool())
        elif value.type() == QVariant.Double:
            pyValue = float(value.toDouble())
        elif value.type() == QVariant.Int:
            pyValue = int(value.toInt()[0])

        self._resultCache[index.row()].__setattr__(columnName, pyValue)

        return True
    
    def isDataChanged(self):
        return self._session.dirty
    
    def submit(self):
        self._dirty = True
        return True
    
    def perform(self):
        if not self._dirty:
            return
        #print "%s : I actually perform" % self._queriedObject
        #print self._session.get_bind(self._queriedObject)
        i = 0
        for obj in self._session.query(self._queriedObject).all():
            self._resultCache[i] = obj
            i += 1
        self._dirty = False