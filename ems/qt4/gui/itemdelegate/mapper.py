'''
Created on 20.03.2012

@author: michi
'''

from PyQt4.QtGui import QStyledItemDelegate

from ems import qt4
from ems.qt4.util import variant_to_pyobject as py
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
            xtype = py(index.data(qt4.XTypeRole))
            if xtype is None:
                return QStyledItemDelegate()
            self._columnDelegates[col] = self._mapper.getDelegateForItem(xtype)

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

class XTypeViewDelegate(GenericDelegate):
    def __init__(self, mapper, parent=None):
        super(XTypeViewDelegate, self).__init__(parent)
        self._mapper = mapper
        self._typeDelegates = {}

    def count(self):
        return len(self._typeDelegates)

    def getMapper(self):
        return self._mapper

    mapper = property(getMapper)

    def _getDelegate(self, index):

        xtype = py(index.data(qt4.XTypeRole))
        cacheId = id(xtype)

        if cacheId not in self._typeDelegates:
            self._typeDelegates[cacheId] = self._mapper.getDelegateForItem(xtype)

        return self._typeDelegates[cacheId]

    def resetDelegates(self):
        self._typeDelegates.clear()

    '''These two methods have no use inside this functionality until yet '''
    def insertColumnDelegate(self, column, delegate):
        raise TypeError("The mapper chooses a delegate," +
                        " use GenericDelegate instead")
    def removeColumnDelegate(self, column):
        raise TypeError("The mapper controls the delegates," + 
                        "use GenericDelegate instead")