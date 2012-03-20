'''
Created on 20.03.2012

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
        self.model.modelReset.connect(self.resetDelegates)
    
    
    def _getDelegate(self, index):
        col = index.column()
        if not self._columnDelegates.has_key(col):
            columnName = variant_to_pyobject(index.data(qt4.ColumnNameRole))
            self._columnDelegates[col] = self.mapper.getDelegateForItem(columnName)
        return self._columnDelegates[col]
    
    def resetDelegates(self):
        #print "Resetting delegates..."
        self._columnDelegates.clear()
    
    '''These two methods have no use inside this functionality until yet '''
    def insertColumnDelegate(self, column, delegate):
        raise TypeError("The mapper chooses a delegate," +
                        " use GenericDelegate instead")
    
    def removeColumnDelegate(self, column):
        raise TypeError("The mapper controls the delegates," + 
                        "use GenericDelegate instead")

