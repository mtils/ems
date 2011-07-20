'''
Created on 06.04.2011

@author: michi
'''

from PyQt4.QtCore import QObject, pyqtSignal, Qt, SIGNAL

class DisplayedRowsListener(QObject):
    visibleRowsChanged = pyqtSignal(int,int)
    def __init__(self, parent, itemView):
        super(DisplayedRowsListener, self).__init__(parent)
        self.assignToModel(parent)
        self._dataCache = {}
        self._lastRow = None
        self._itemView = itemView
        self._lastTopVisibleRow = None
        self._lastBottomVisibleRow = None
        self.connect(parent, SIGNAL('modelReset()'),
                     self.onModelReset)
        
    def assignToModel(self, qitemmodel):
        if not hasattr(qitemmodel, 'setDataListener'):
            raise TypeError('The Object has to implement a setDataListener Method')
        
        qitemmodel.setDataListener(self)
    
    def onModelReset(self):
        self._lastRow = None
        self._lastTopVisibleRow = None
        self._lastBottomVisibleRow = None
    
    def data(self, data, role):
        if role == Qt.DisplayRole:
            row = data.row()
            #Reduce Calls
            if self._lastRow == row:
                return
            self._lastRow = row
            rect = self._itemView.rect()
            topVisibleRow = self._itemView.indexAt(rect.topLeft()).row()
            bottomVisibleRow = self._itemView.indexAt(rect.bottomLeft()).row()
            if bottomVisibleRow == -1:
                bottomVisibleRow = (self.parent().rowCount()-1)
            #print "top: %s bottom: %s" % (topVisibleRow, bottomVisibleRow)
            if self._lastTopVisibleRow == topVisibleRow and\
                self._lastBottomVisibleRow == bottomVisibleRow:
                return
            self._lastTopVisibleRow = topVisibleRow
            self._lastBottomVisibleRow = bottomVisibleRow
            self.visibleRowsChanged.emit(topVisibleRow,bottomVisibleRow)