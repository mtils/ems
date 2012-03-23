'''
Created on 23.03.2012

@author: michi
'''
from PyQt4.QtCore import QAbstractListModel, QModelIndex, Qt, QVariant

class OneOfAListModel(QAbstractListModel):
    def __init__(self, xType, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.xType = xType
        self.valueNames = {}
    
    def rowCount(self, parentIndex=QModelIndex()):
        return len(self.xType.possibleValues)
    
    def data(self, index, role=Qt.DisplayRole):
        
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()
        
        if role == Qt.EditRole:
            try:
                return QVariant(self.xType.possibleValues[index.row()])
            except KeyError:
                return QVariant()
            except AttributeError:
                return QVariant()
        if role == Qt.DisplayRole:
            
            try:
                value =  self.xType.possibleValues[index.row()]
                if self.valueNames.has_key(value):
                    return QVariant(self.valueNames[value])
                return QVariant(value)
            except KeyError:
                return QVariant()
            except AttributeError:
                return QVariant()
            
        return QVariant()
    
        