'''
Created on 20.06.2011

@author: michi
'''
import re

from PyQt4.QtCore import QAbstractListModel, QVariant, Qt, QModelIndex
from sqlalchemy.orm import object_mapper, ColumnProperty
from sqlalchemy import String, or_, and_

from ems import qt4

class RepresentativeModel(QAbstractListModel):
    def __init__(self,session, queriedObject, fkColumn, query=None,
                 nullEntry=""):
        super(RepresentativeModel, self).__init__()
        self._fkColumn = fkColumn
        self._session = session
        self._queriedObject = queriedObject
        self._resultCache = {}
        self._dirty = True
        self._fullTextCriteria = ""
        self._fullTextColumns = None
        self.hardLimit = 250
        self.returnHtml = False
        self._nullEntry = nullEntry
        
        if query is None:
            query = self._session.query(self._queriedObject)
        self._query = query
        
        #self._buildFulltextCriteria()
    
    @property
    def session(self):
        return self._session
    
    @property
    def queriedObject(self):
        return self._queriedObject
    
    
    def getQuery(self):
        return self._query
    
    
    def setQuery(self, query):
        self._query = query
        self._dirty = True
        self.perform()
    
    query = property(getQuery, setQuery)
    
    def rowCount(self, index=QModelIndex()):
        self.perform()
        return len(self._resultCache)
    
    @property
    def fulltextColumns(self):
        if self._fullTextColumns is None:
            prototype = self._queriedObject()
            mapper = object_mapper(prototype)
            stringProperties = []
            for prop in mapper.iterate_properties:
                if isinstance(prop, ColumnProperty):
                    cols = prop.columns
                    if len(cols) == 1:
                        col = cols[0]
                        colType = col.type
                        if isinstance(colType, String):
                            stringProperties.append(self._queriedObject.__dict__[prop.key])
            if len(stringProperties):
                self._fullTextColumns = stringProperties
            else:
                self._fullTextColumns = None
        return self._fullTextColumns
                    
    
    def data(self, index, role=Qt.DisplayRole):
        self.perform()
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()
        if role in (Qt.DisplayRole, Qt.EditRole):
            if self._nullEntry and index.row() == 0:
                value = self._nullEntry
            else:
                value = self._resultCache[index.row()].__ormDecorator__().getReprasentiveString(self._resultCache[index.row()])
#            if self._queriedObject.__name__ == 'Gruppe':
#                print "row:%s col:%s role:%s value:%s" % (index.row(), index.column(), role, value)
            if not self.returnHtml or role == Qt.EditRole:
                if isinstance(value, basestring):
                    return QVariant(unicode(value))
                
            else:
                strVal = unicode(value)
                i=0
                
                for cond in unicode(self._fullTextCriteria).split(' '):
                    if len(cond.strip(' ')):
                        strVal = strVal.replace(cond, "<b>%s</b>" % cond.strip())
#                        strVal = re.sub(cond, "<b>%s</b>" % cond.strip(),
#                                        strVal,flags=re.IGNORECASE)
                    i += 1
            return QVariant(strVal)
        if role == Qt.UserRole:
            #value = self._resultCache[index.row()].__getattribute__(self._fkColumn)
            value = self._resultCache[index.row()]
            return QVariant(value)
        if role == qt4.ColumnNameRole:
            return QVariant(unicode(self._queryBuilder.currentColumnList[index.column()]))
        if role == qt4.ForeignKeysRole:
            if self._nullEntry and index.row() == 0:
                return QVariant()
            return QVariant(self._resultCache[index.row()].__getattribute__(self._fkColumn))
        return QVariant()
    
    def _buildFulltextQuery(self):
        query = None
        dec = self._queriedObject.__ormDecorator__()
        query = dec.getFullTextQuery(self._session, unicode(self._fullTextCriteria))
        if query is None:
            criteria = None
            if len(self._fullTextCriteria):
                fulltextCols = self.fulltextColumns
                
                if fulltextCols is not None:
                    if len(fulltextCols) > 1:
                        criteria = or_()
                        for col in fulltextCols:
                            try:
                                criteria.append(col[0].like(unicode(self._fullTextCriteria))+"%")
                            except TypeError:
                                criteria.append(col.like(unicode(self._fullTextCriteria))+"%")
                        
                    else:
                        criteria = fulltextCols[0].like(unicode(self._fullTextCriteria)+"%")
                return self._query.filter(criteria)
            raise TypeError("No FulltextColumns found")
        else:
            return query
    
    def perform(self):
        if not self._dirty:
            return
#        print "%s : I actually perform" % self._queriedObject
        #print self._session.get_bind(self._queriedObject)
        i = 0
        self.beginResetModel()
        self._resultCache.clear()
        if len(self._fullTextCriteria):
            query = self._buildFulltextQuery()
            #query = self._query.filter(criteria)
        else:
            query = self._query
        
        if self._nullEntry:
            self._resultCache[0] = None
            i = 1
        
        for obj in query[0:self.hardLimit]:
            self._resultCache[i] = obj
            i += 1
        self.endResetModel()
        self._dirty = False
    
    def match(self, start, role, value, hits=1, matchFlags=Qt.MatchStartsWith|Qt.MatchWrap):
        self.perform()
        search = unicode(value.toString()).lower()
        indexes = []
        for row in self._resultCache:
            if self._resultCache[row] is not None:
                value = unicode(self._resultCache[row].__ormDecorator__().\
                                getReprasentiveString(self._resultCache[row]))
                if value.lower().startswith(search):
                    indexes.append(self.index(row))
        return indexes
    
    def forceReset(self):
        self._dirty = True
        self.perform()
        
        
class RepresentativeModelMatch(RepresentativeModel):
    def match(self, start, role, value, hits=1, matchFlags=Qt.MatchStartsWith|Qt.MatchWrap):
        self._fullTextCriteria = value.toString()
        self._dirty = True
        self.perform()