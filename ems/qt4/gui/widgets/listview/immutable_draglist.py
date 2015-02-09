'''
Created on 09.07.2011

@author: michi
'''
from PyQt4.QtCore import QObject, Qt, SIGNAL, QTimer
from PyQt4.QtGui import QTreeWidget, QAbstractItemView, QTreeWidgetItemIterator, \
    QPalette, QBrush, QColor, QApplication

from ems.qt4.gui.util import FlatTreeBuilderMixin #@UnresolvedImport

class TreeWidgetIterator(object):
    def __init__(self, parent):
        self.parent = parent
        self._it = QTreeWidgetItemIterator(self.parent)
        
    def __iter__(self):
        return self
        
    def next(self):
        item = self._it.value()
        self._it += 1
        if not item:
            raise StopIteration
        return item
        
class ImmutableTreeWidget(QTreeWidget, FlatTreeBuilderMixin):
    def __init__(self, buddyView=None, immutable=True, uniqueDrag=True, parent=None):
        QTreeWidget.__init__(self, parent)
        self.immutable = immutable
        self.uniqueDrag = uniqueDrag
        self._buddyView = None
        if buddyView is not None:
            self.buddyView = buddyView
        self._modelsConnected = False
        
    
    def addItem(self, item, depth=0):
        FlatTreeBuilderMixin.addItemFlat(self, item, depth)
        
    
    def getBuddyView(self):
        return self._buddyView
    
    def __iter__(self):
        return TreeWidgetIterator(self)
    
    def setBuddyView(self, view):
        
        self._buddyView = view
        if self.uniqueDrag:
            self.connect(self._buddyView.model(),
                         SIGNAL("rowsInserted(QModelIndex,int,int)"),
                         self.onBuddyRowsInserted)
            self.connect(self._buddyView.model(),
                         SIGNAL("rowsAboutToBeRemoved(QModelIndex,int,int)"),
                         self.onBuddyRowsAboutToBeRemoved)
    
    buddyView = property(getBuddyView, setBuddyView)
    
    def reSyncEntries(self):
        itemsUserDatas = []
        for i in range(self._buddyView.model().rowCount()):
            trgIndex = self._buddyView.model().index(i,0)
            #print self._buddyView.model().data(trgIndex, Qt.DisplayRole).toString()
            userData =self._buddyView.model().data(trgIndex, Qt.UserRole)
            
            
            itemsUserDatas.append(userData)
            #print userData.toString()
            
        foundItems = []
        it = QTreeWidgetItemIterator(self)    
        while it.value():
            itemData = it.value().data(0, Qt.UserRole)
            if itemData in itemsUserDatas:
                #print "Hit!!"
                foundItems.append(it.value())
                it.value().setFlags(Qt.ItemFlags(Qt.ItemIsEnabled))
                palette = QApplication.palette("QPushButton")
                it.value().setForeground(0, palette.brush(QPalette.Disabled,
                                                          QPalette.Text))
            else:
                #print "No Hit!! %s" % itemData.toString()
                it.value().setFlags(Qt.ItemFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable |
                                    Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled))
                #palette = it.value().palette().enabled()
                palette = QApplication.palette("QPushButton")
                it.value().setForeground(0, palette.brush(QPalette.Normal,
                                                          QPalette.Text))
            #print "%s %s" % (itemData.toString(), userData == itemData)
            it += 1
    
    def onBuddyRowsInserted(self, index, start, end):
        QTimer.singleShot(50, self.reSyncEntries)
    
    def onBuddyRowsAboutToBeRemoved(self, index, start, end):
        QTimer.singleShot(50, self.reSyncEntries)
    
    def dropEvent(self, event):
#        if isinstance(event.source(), QAbstractItemView):
#            for index in event.source().selectionModel().selection().indexes():
#                displayData = event.source().model().data(index, Qt.DisplayRole)
#                userData = event.source().model().data(index, Qt.UserRole)
#                
#                items = self._findItemsByUserData(userData)
                #print items
#                for item in self.findItems(userData.toString(), Qt.MatchExactly):
#                    print item 
        event.accept()
        
        return None
        result = QTreeWidget.dropEvent(self, event)
        return result
    
    def _findItemsByUserData(self, userData):
        it = QTreeWidgetItemIterator(self)
        foundItems = []
        while it.value():
            itemData = it.value().data(0, Qt.UserRole)
            if itemData == userData:
                foundItems.append(it.value())
            #print "%s %s" % (itemData.toString(), userData == itemData)
            it += 1
        return foundItems
    
    
    def dragMoveEvent(self, event):
        if self.immutable:
            if event.source() is self:
                event.ignore()
                return None
        #print "dragMoveEvent Called %s" % type(event)
        result = QTreeWidget.dragMoveEvent(self, event)
        #print "Event is accepted %s" % event.isAccepted()
        return result
 
if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)
    
    tree = ImmutableTreeWidget()
    tree.show()
    
    app.exec_()
    