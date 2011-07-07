'''
Created on 07.07.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSignal, Qt, QVariant, SIGNAL, SLOT, pyqtSlot, QTimer
from PyQt4.QtGui import QWidget, QListWidgetItem

from dragdroplists_ui import Ui_ListDragSelection #@UnresolvedImport

class DragDropLists(QWidget, Ui_ListDragSelection):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi()
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
                     self.onAvailableDataChanged)
        
        self.connect(self.availableView.model(),
                     SIGNAL('rowsMoved(QModelIndex,int,int,QModelIndex,int)'),
                     self.onAvailableDataChanged)
        
        self.connect(self.availableView.model(),
                     SIGNAL('rowsRemoved(QModelIndex,int,int)'),
                     self.onAvailableDataChanged)
    
    def onAvailableDataChanged(self, *args):
        print "Ich werde aufgerufen"
        
    def setupUi(self):
        Ui_ListDragSelection.setupUi(self, self)
    
    @pyqtSlot()
    def unChooseAll(self):
#        print "unChooseAll triggered"
#        print self.choosedItemView.count()
        for index in range(self.choosedItemView.count()):
            self.availableView.addItem(QListWidgetItem(self.choosedItemView.item(index)))
        
        self.choosedItemView.clear()
    
    @pyqtSlot()
    def chooseAll(self):
        for index in range(self.availableView.count()):
            self.choosedItemView.addItem(QListWidgetItem(self.availableView.item(index)))
        
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
        self.choosedItemView.addItem(item)
    
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
        self.choosedItemView.clear()
        self.addChoosedEntries(listOfTextsOrTuples)
        
if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    
    app = QApplication([])
    w = DragDropLists()
    w.addAvailableEntry("text")
    w.choosedItemView.addItem("Und jetzt auch noch rechts")
    w.show()
    
    app.exec_()