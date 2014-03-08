'''
Created on 20.03.2012

@author: michi
'''

from ems import qt4
from ems.qt4.util import variant_to_pyobject
from ems.qt4.gui.itemdelegate.genericdelegate import GenericDelegate
from ems.qt4.itemmodel.reflectable_mixin import ReflectableMixin #@UnresolvedImport


class MapperItemViewDelegate(GenericDelegate):
    def __init__(self, mapper, parent=None):
        super(MapperItemViewDelegate, self).__init__(parent)
        self._mapper = mapper
        self._columnDelegates = {}
        #self.model.modelReset.connect(self.resetDelegates)
    
    def columnDelegate(self, column):
        if column in self._columnDelegates:
            return self._columnDelegates[column]
    
    def columnDelegates(self):
        return self._columnDelegates
    
    def count(self):
        return len(self._columnDelegates)
    
    def getMapper(self):
        return self._mapper
    
    mapper = property(getMapper)
    
    def _getDelegate(self, index):
        col = index.column()
        if col not in self._columnDelegates:
            model = index.model()
            if isinstance(model, ReflectableMixin):
                type_ = model.columnType(index.column())
            self._columnDelegates[col] = self._mapper.getDelegateForItem(type_)
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

