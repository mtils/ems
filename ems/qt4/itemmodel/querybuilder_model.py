'''
Created on 04.08.2011

@author: michi
'''

from PyQt4.QtCore import QAbstractItemModel, QModelIndex, Qt, QVariant, \
    pyqtSlot

from PyQt4.QtGui import QColor, QBrush

from ems.qt4.util import variant_to_pyobject #@UnresolvedImport

class QueryBuilderRow(object):
    def __init__(self):
        self.parent = None
        self.conjunction = QVariant('AND')
        self.column = QVariant('')
        self.operator = QVariant('=')
        self.value = QVariant('NULL')
        self.matches = QVariant(True)
    
    def isValid(self):
        return (len(self.column.toString()) > 0)
    
    def __str__(self):
        return "%s %s %s %s %s" % (variant_to_pyobject(self.conjunction),
                                   variant_to_pyobject(self.column),
                                   variant_to_pyobject(self.operator),
                                   variant_to_pyobject(self.value),
                                   variant_to_pyobject(self.matches))
        

class QueryBuilderModel(QAbstractItemModel):
    def __init__(self, parent=None):
        QAbstractItemModel.__init__(self, parent)
        self._returnedCols = ['conjunction','column','operator','value']#,'matches']
        self._clauses = []
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._clauses)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self._returnedCols)
    
    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column, object=0)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()
        colName = self._returnedCols[index.column()]
        #print role
        
        if role in (Qt.BackgroundRole, Qt.ToolTipRole):
            valid = self._clauses[index.row()].isValid()
            if role == Qt.BackgroundRole:
                if not valid:
                    return QBrush(QColor(255,211,123))
            if role == Qt.ToolTipRole:
                if not valid:
                    return QVariant("Diese Zeile ist nicht valide")
                
        if role == Qt.DisplayRole:
            #print self._clauses[index.row()].isValid()
            return self._clauses[index.row()].__getattribute__(colName)
        
        return QVariant()
    
    def setData(self, index, value, role=Qt.EditRole):
        colName = self._returnedCols[index.column()]
        self._clauses[index.row()].__setattr__(colName, value) 
        #print "setData called %s = %s" % (colName, value.toString())
        
        return False
    
    def validateRow(self, row):
        pass
    
    def parent(self, index):
        return QModelIndex()
    
    def flags(self, index):
        if (index.row() == 0) and (index.column() == 0):
            return Qt.NoItemFlags
        return Qt.ItemIsEditable | Qt.ItemIsEnabled
    
    @pyqtSlot()
    def appendRow(self, row=None):
        if row is not None:
            if isinstance(row, QueryBuilderRow):
                self.beginResetModel()
                self._clauses.append(row)
                self.endResetModel()
            else:
                raise TypeError("row has to be None or instanceof QueryBuilderRow")
        else:
            row = QueryBuilderRow()
            self.beginResetModel()
            self._clauses.append(row)
            self.endResetModel()
    
    @pyqtSlot(int)
    def removeRow(self, row, parent=QModelIndex()):
        self.beginResetModel()
        del self._clauses[row]
        self.endResetModel()
    
    def getClausesAsDicts(self):
        clauses = []
        for clause in self._clauses:
            clauseDict = {}
            for att in ('conjunction','column','operator','value','matches'):
                clauseDict[att] = variant_to_pyobject(clause.__getattribute__(att))
            clauses.append(clauseDict)
        return clauses
    
    def getClauses(self):
        return self._clauses
    
    clauses = property(getClauses)
    
    def setClausesAsDicts(self, clausesDicts):
        self.beginResetModel()
        clauses = []
        for clauseDict in clausesDicts:
            clause = QueryBuilderRow()
#            if clauseDict.has_key('field') and len(clauseDict['field']):
            if clauseDict.has_key('field'):
                clause.column = QVariant(clauseDict['field'])
#            else:
#                continue
            for att in ('conjunction','column','operator','value','matches'):
                if clauseDict.has_key(att):
                    clause.__setattr__(att, QVariant(clauseDict[att]))
                    #clauseDict[att] = variant_to_pyobject(clause.__getattribute__(att))
            clauses.append(clause)
#        for row in clauses:
#            print row
        self._clauses = clauses
        self.endResetModel()
        #return clauses