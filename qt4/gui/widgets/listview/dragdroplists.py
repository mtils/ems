'''
Created on 07.07.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSignal, Qt, QVariant, SIGNAL, SLOT, pyqtSlot, QTimer
from PyQt4.QtGui import QWidget, QListWidgetItem

from dragdroplists_ui import Ui_ListDragSelection #@UnresolvedImport

class DragDropLists(QWidget, Ui_ListDragSelection):
    
    choosedItemsChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi()
        
        self._blockChoosedSignal = False
        
        self.connect(self.addAllInput,
                     SIGNAL("clicked()"),
                     self,
                     SLOT('chooseAll()'))
        
        self.connect(self.removeAllInput,
                     SIGNAL("clicked()"),
                     self,
                     SLOT('unChooseAll()'))
        
        self.connect(self.availableView.model(),
                     SIGNAL('rowsInserted(QModelIndex,int,int)'),
                     self.onAvailableItemsInserted)
        
        self.connect(self.availableView.model(),
                     SIGNAL('rowsMoved(QModelIndex,int,int,QModelIndex,int)'),
                     self.onAvailableItemsMoved)
        
        self.connect(self.choosedView.model(),
                     SIGNAL('rowsRemoved(QModelIndex,int,int)'),
                     self.onAvailableItemsRemoved)
        
        self.connect(self.choosedView.model(),
                     SIGNAL('rowsInserted(QModelIndex,int,int)'),
                     self.onChoosedItemsInserted)
        
        self.connect(self.choosedView.model(),
                     SIGNAL('rowsMoved(QModelIndex,int,int,QModelIndex,int)'),
                     self.onChoosedItemsMoved)
        
        self.connect(self.choosedView.model(),
                     SIGNAL('rowsRemoved(QModelIndex,int,int)'),
                     self.onChoosedItemsRemoved)
        
        self.connect(self, SIGNAL('choosedItemsChanged()'),
                     self.onChoosedItemsChangedSignal)
    
    def onAvailableItemsChanged(self, *args):
        pass
#        print "onAvailableItemsChanged"
    
    def onAvailableItemsInserted(self, *args):
        pass
#        print "onAvailableItemsInserted"
    
    def onAvailableItemsMoved(self, *args):
        pass
#        print "onAvailableItemsMoved"
    
    def onAvailableItemsRemoved(self, *args):
        pass
#        print "onAvailableItemsRemoved"
    
    def onChoosedItemsChanged(self, *args):
#        print "onChoosedItemsChanged"
        self.choosedItemsChangedEmit()
    
    def onChoosedItemsInserted(self, *args):
#        print "onChoosedItemsInserted"
        self.choosedItemsChangedEmit()
    
    def onChoosedItemsMoved(self, *args):
#        print "onChoosedItemsMoved"
        self.choosedItemsChangedEmit()
    
    def onChoosedItemsRemoved(self, *args):
#        print "onChoosedItemsRemoved"
        self.choosedItemsChangedEmit()
    
    def choosedItemsChangedEmit(self):
        if not self._blockChoosedSignal:
            self.choosedItemsChanged.emit()
    
    def onChoosedItemsChangedSignal(self):
        print "choosedItemsChanged emitted"
        
    def setupUi(self):
        Ui_ListDragSelection.setupUi(self, self)
    
    @pyqtSlot()
    def unChooseAll(self):
#        print "unChooseAll triggered"
#        print self.choosedView.count()
        for index in range(self.choosedView.count()):
            self.availableView.addItem(QListWidgetItem(self.choosedView.item(index)))
        
        self.choosedView.clear()
    
    @pyqtSlot()
    def chooseAll(self):
        for index in range(self.availableView.count()):
            self.choosedView.addItem(QListWidgetItem(self.availableView.item(index)))
        
        self.availableView.clear()
    
    def addAvailableEntry(self, text, userData=None, font=None ):
        item = QListWidgetItem(text)
        if userData is not None:
            item.setData(Qt.UserRole, QVariant(userData))
        if font is not None:
            item.setFont(font)
        
        self.availableView.addItem(item)
    
    def addChoosedEntry(self, text, userData=None, font=None):
        item = QListWidgetItem(text)
        if userData is not None:
            item.setData(Qt.UserRole, QVariant(userData))
        if font is not None:
            item.setFont(font)
        self._blockChoosedSignal = True
        self.choosedView.addItem(item)
        self._blockChoosedSignal = False
    
    def addAvailableEntries(self, listOfTextsOrTuples):
        for entry in listOfTextsOrTuples:
            if isinstance(entry, (list, tuple)):
                self.addAvailableEntry(*entry)
            else:
                self.addAvailableEntry(entry)
    
    def setAvailableEntries(self, listOfTextsOrTuples):
        self.availableView.clear()
        self.addAvailableEntries(listOfTextsOrTuples)
    
    def addChoosedEntries(self, listOfTextsOrTuples):
        for entry in listOfTextsOrTuples:
            if isinstance(entry, (list, tuple)):
                self.addChoosedEntry(*entry)
            else:
                self.addChoosedEntry(entry)
    
    def setChoosedEntries(self, listOfTextsOrTuples):
        self.choosedView.clear()
        self.addChoosedEntries(listOfTextsOrTuples)
        
if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    
    app = QApplication([])
    w = DragDropLists()
        
    for i in range(12):
        w.addAvailableEntry("L Eintrag %s" % i)
        w.addChoosedEntry("R Eintrag %s" % i)
    w.show()
    
    app.exec_()