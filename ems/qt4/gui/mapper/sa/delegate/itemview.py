'''
Created on 19.09.2011

@author: michi
'''

from ems import qt4
from ems.qt4.util import variant_to_pyobject
from ems.qt4.gui.itemdelegate.genericdelegate import GenericDelegate


class MapperItemViewDelegate(GenericDelegate):
    def __init__(self, ormObj, model, mapper, parent=None):
        super(MapperItemViewDelegate, self).__init__(parent)
        self.ormObj = ormObj
        self.model = model
        self.mapper = mapper
        self._columnDelegates = {}
        self._overwrittenDelegates = {}
        self._columnNameCache = {}
        self.model.modelReset.connect(self.resetDelegates)
    
    
    def _getDelegate(self, index):
        col = index.column()

        if col not in self._columnDelegates:

            if col not in self._columnNameCache:
                self._columnNameCache[col] = variant_to_pyobject(index.data(qt4.ColumnNameRole))

            columnName = self._columnNameCache[col]

            if columnName in self._overwrittenDelegates:
                return self._overwrittenDelegates[columnName]

            self._columnDelegates[col] = self.mapper.getDelegateForItem(columnName)

        return self._columnDelegates[col]
    
    def resetDelegates(self):
        #print "Resetting delegates..."
        self._columnDelegates.clear()
        self._columnNameCache.clear()

    def overWriteColumnDelegate(self, colName, delegate):
        self._overwrittenDelegates[colName] = delegate

    '''These two methods have no use inside this functionality until yet '''
    def insertColumnDelegate(self, column, delegate):
        raise TypeError("The mapper chooses a delegate," +
                        " use GenericDelegate instead")
    
    def removeColumnDelegate(self, column):
        raise TypeError("The mapper controls the delegates," + 
                        "use GenericDelegate instead")
    
    