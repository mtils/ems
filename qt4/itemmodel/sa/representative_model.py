'''
Created on 20.06.2011

@author: michi
'''
from PyQt4.QtCore import QAbstractListModel, QVariant, Qt, QModelIndex
from sqlalchemy.orm import object_mapper

from ems import qt4

class RepresentativeModel(QAbstractListModel):
    def __init__(self,session, queriedObject, fkColumn):
        super(RepresentativeModel, self).__init__()
        self._fkColumn = fkColumn
        self._session = session
        self._queriedObject = queriedObject
        self._resultCache = {}
        self._dirty = True
    
    def rowCount(self, index=QModelIndex()):
        self.perform()
        return len(self._resultCache)
    
    def data(self, index, role=Qt.DisplayRole):
        self.perform()
        columnName = 'name'
        
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()
        if role == Qt.DisplayRole:
            value = self._resultCache[index.row()].__ormDecorator__().getReprasentiveString(self._resultCache[index.row()])
#            if self._queriedObject.__name__ == 'Gruppe':
#                print "row:%s col:%s role:%s value:%s" % (index.row(), index.column(), role, value)
            if isinstance(value, basestring):
                return QVariant(unicode(value))
            return QVariant(value)
        if role == qt4.ColumnNameRole:
            return QVariant(unicode(self._queryBuilder.currentColumnList[index.column()]))
        if role == qt4.ForeignKeysRole:
            return QVariant(self._resultCache[index.row()].__getattribute__(self._fkColumn))
        return QVariant()
    
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