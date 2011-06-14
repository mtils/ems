'''
Created on 14.06.2011

@author: michi
'''
from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant

from ems import qt4

class AlchemyOrmModel(QAbstractTableModel):
    def __init__(self,session, queriedObject, columns):
        super(AlchemyOrmModel, self).__init__()
        self._session = session
        self._queriedObject = queriedObject
        self._resultCache = {}
        self._columns = columns
        self._columnName2Index = self._buildReversedColumnLookup(columns)
        self._dirty = True
    
    def _buildReversedColumnLookup(self, columns):
        i = 0
        reversed = {}
        for column in columns:
            reversed[str(column)] = i
        return reversed
    
    def rowCount(self, index=QModelIndex()):
        self.perform()
        return len(self._resultCache)
    
    def columnCount(self, index=QModelIndex()):
        self.perform()
        return len(self._columns)
    
    def getColumnNameFromIndex(self, index):
        return self._columns[index]
    
    def getIndexFromColumnName(self, name):
        return self._columnName2Index[name]
    
    def data(self, index, role=Qt.DisplayRole):
        self.perform()
        columnName = self.getColumnNameFromIndex(index.column())
        #return QVariant()
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()
        if role in (Qt.DisplayRole, Qt.EditRole):
            value = self._resultCache[index.row()].__getattribute__(columnName)
            if isinstance(value, basestring):
                return QVariant(unicode(value))
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
            columnName = unicode(self.getColumnNameFromIndex(section))
#            if self.columnHeaderTranslated.has_key(columnName):
#                return QVariant(self.columnHeaderTranslated[columnName])
            return QVariant(columnName)
        return QVariant(int(section + 1))
    
    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled
    
    def setData(self, index, value, role=Qt.EditRole):
        columnName = self.getColumnNameFromIndex(index.column())
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
            pyValue = int(value.toInt())
        print pyValue
        print self._session.dirty
        
        self._resultCache[index.row()].__setattr__(columnName, pyValue)
        
        return True
    
    def isDataChanged(self):
        return self._session.dirty
    
    def submit(self):
        print "Ich wurde jetriggert"
        
        return True
    
    def perform(self):
        if not self._dirty:
            return
        #print self._session.get_bind(self._queriedObject)
        i = 0
        for obj in self._session.query(self._queriedObject).all():
            self._resultCache[i] = obj
            i += 1