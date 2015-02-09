'''
Created on 07.07.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSignal, Qt, QVariant, SIGNAL, SLOT, pyqtSlot, QTimer
from PyQt4.QtGui import QWidget, QListWidgetItem, QTreeWidgetItem, QPushButton

from dragdroplists_ui import Ui_ListDragSelection #@UnresolvedImport
from immutable_draglist import ImmutableTreeWidget #@UnresolvedImport
from ems.qt4.gui.widgets.listview.immutable_draglist import ImmutableTreeWidget #@UnresolvedImport

class DragDropLists(QWidget, Ui_ListDragSelection):
    Tree = 1
    List = 2

    trgItemsChanged = pyqtSignal()
    
    def __init__(self, srcWidgetMode=None, srcWidgetIsReadOnly=False, parent=None):
        QWidget.__init__(self, parent)
        if srcWidgetMode is None:
            srcWidgetMode = self.List
        
        self.srcWidgetMode = srcWidgetMode
        self.srcWidgetIsReadOnly = srcWidgetIsReadOnly
        self.setupUi()
        
        
        self._blockTrgSignal = False
        
        self.connect(self.addAllInput,
                     SIGNAL("clicked()"),
                     self,
                     SLOT('chooseAll()'))
        
        self.connect(self.removeAllInput,
                     SIGNAL("clicked()"),
                     self,
                     SLOT('unChooseAll()'))
        
        self.connect(self.srcInput.model(),
                     SIGNAL('rowsInserted(QModelIndex,int,int)'),
                     self.onSrcItemsInserted)
        
        self.connect(self.srcInput.model(),
                     SIGNAL('rowsMoved(QModelIndex,int,int,QModelIndex,int)'),
                     self.onSrcItemsMoved)
        
        self.connect(self.trgInput.model(),
                     SIGNAL('rowsRemoved(QModelIndex,int,int)'),
                     self.onSrcItemsRemoved)
        
        self.connect(self.trgInput.model(),
                     SIGNAL('rowsInserted(QModelIndex,int,int)'),
                     self.onTrgItemsInserted)
        
        self.connect(self.trgInput.model(),
                     SIGNAL('rowsMoved(QModelIndex,int,int,QModelIndex,int)'),
                     self.onTrgItemsMoved)
        
        self.connect(self.trgInput.model(),
                     SIGNAL('rowsRemoved(QModelIndex,int,int)'),
                     self.onTrgItemsRemoved)
        
        self.connect(self, SIGNAL('trgItemsChanged()'),
                     self.onTrgItemsChangedSignal)
    
    def onSrcItemsChanged(self, *args):
        pass
#        print "onSrcItemsChanged"
    
    def onSrcItemsInserted(self, *args):
        pass
#        print "onSrcItemsInserted"
    
    def onSrcItemsMoved(self, *args):
        pass
#        print "onSrcItemsMoved"
    
    def onSrcItemsRemoved(self, *args):
        pass
#        print "onSrcItemsRemoved"
    
    def onTrgItemsChanged(self, *args):
#        print "onTrgItemsChanged"
        self.trgItemsChangedEmit()
    
    def onTrgItemsInserted(self, *args):
#        print "onTrgItemsInserted"
        self.trgItemsChangedEmit()
    
    def onTrgItemsMoved(self, *args):
#        print "onTrgItemsMoved"
        self.trgItemsChangedEmit()
    
    def onTrgItemsRemoved(self, *args):
#        print "onTrgItemsRemoved"
        self.trgItemsChangedEmit()
    
    def trgItemsChangedEmit(self):
        if not self._blockTrgSignal:
            self.trgItemsChanged.emit()
    
    def onTrgItemsChangedSignal(self):
        return

    def setupUi(self):
        srcWidget = None
        if self.srcWidgetMode == self.Tree:
            srcWidget = ImmutableTreeWidget(parent=self)
            srcWidget.header().setVisible(False)
        Ui_ListDragSelection.setupUi(self, self, srcWidget=srcWidget)
        
        if isinstance(srcWidget, ImmutableTreeWidget):
            srcWidget.setBuddyView(self.trgInput)
        if self.srcWidgetIsReadOnly:
            self.srcInput.setDefaultDropAction(Qt.CopyAction)
        else:
            self.srcInput.setDefaultDropAction(Qt.MoveAction)
    
    @pyqtSlot()
    def unChooseAll(self):
        self._blockTrgSignal = True
#        for index in range(self.trgInput.count()):
#            self.srcInput.addItem(QListWidgetItem(self.trgInput.item(index)))
        if isinstance(self.srcInput, ImmutableTreeWidget):
            QTimer.singleShot(50,self.srcInput.reSyncEntries)
            #self.srcInput.reSyncEntries()
        self._blockTrgSignal = False
        self.trgInput.clear()
        self.trgItemsChanged.emit()
        
    
    @pyqtSlot()
    def chooseAll(self):
        self._blockTrgSignal = True
        if isinstance(self.srcInput, ImmutableTreeWidget):
            for item in self.srcInput:
                if int(item.flags()) & int(Qt.ItemIsSelectable):
                    trgItem = QListWidgetItem(item.text(0))
                    trgItem.setData(Qt.UserRole, item.data(0, Qt.UserRole))
                    self.trgInput.addItem(trgItem)
#        for index in range(self.srcInput.count()):
#            self.trgInput.addItem(QListWidgetItem(self.srcInput.item(index)))
        
        self._blockTrgSignal = False
        #self.srcInput.clear()
        self.trgItemsChanged.emit()
    
    def addSrcEntry(self, text, userData=None, font=None, depth=None,
                    isChoosen=False ):
        if self.srcWidgetMode == self.List:
            item = QListWidgetItem(text)
            if userData is not None:
                item.setData(Qt.UserRole, QVariant(userData))
        else:
            item = QTreeWidgetItem((text,))
            if userData is not None:
                item.setData(0,Qt.UserRole, QVariant(userData))
        
        if font is not None:
            item.setFont(font)
            
        if self.srcWidgetMode == self.List:
            self.srcInput.addItem(item)
            
        else:
            self.srcInput.addItem(item, depth)
        
    def addTrgEntry(self, text, userData=None, font=None):
        item = QListWidgetItem(text)
        if userData is not None:
            item.setData(Qt.UserRole, QVariant(userData))
        if font is not None:
            item.setFont(font)
        self._blockTrgSignal = True
        self.trgInput.addItem(item)
        self._blockTrgSignal = False
    
    def addSrcEntries(self, listOfTextsOrTuples):
        for entry in listOfTextsOrTuples:
            if isinstance(entry, (list, tuple)):
                self.addSrcEntry(*entry)
            else:
                self.addSrcEntry(entry)
    
    def setSrcEntries(self, listOfTextsOrTuples):
        self.srcInput.clear()
        self.addSrcEntries(listOfTextsOrTuples)
    
    def addTrgEntries(self, listOfTextsOrTuples):
        for entry in listOfTextsOrTuples:
            if isinstance(entry, (list, tuple)):
                self.addTrgEntry(*entry)
            else:
                self.addTrgEntry(entry)
    
    def setTrgEntries(self, listOfTextsOrTuples):
        self.trgInput.clear()
        self.addTrgEntries(listOfTextsOrTuples)
    
    def getChoosedUserData(self):
        choosedUserData = []
        for i in range(self.trgInput.count()):
            choosedUserData.append(self.trgInput.item(i).data(Qt.UserRole))
        
        return choosedUserData
    
    @staticmethod
    def toDialog(srcWidgetMode=None, srcWidgetIsReadOnly=False, parent=None):
        from PyQt4.QtGui import QDialog, QDialogButtonBox, QVBoxLayout
        dlg = QDialog(parent)
        dlg.setLayout(QVBoxLayout(dlg))
        dlg.form = DragDropLists(srcWidgetMode=srcWidgetMode,
                                 srcWidgetIsReadOnly=srcWidgetIsReadOnly,
                                 parent=dlg)
        dlg.layout().addWidget(dlg.form)
        dlg.buttonBox = QDialogButtonBox(QDialogButtonBox.Apply | QDialogButtonBox.Cancel,
                                         Qt.Horizontal,
                                         dlg)
        
        dlg.connect(dlg.buttonBox, SIGNAL("rejected()"),dlg, SLOT("reject()"))
        #dlg.connect(dlg.buttonBox, SIGNAL("accepted()"),dlg, SLOT("accept()"))
        #dlg.connect(dlg.buttonBox, SIGNAL("clicked(QAbstractButton)"),dlg.form.testSignal)
        dlg.layout().addWidget(dlg.buttonBox)
        
        return dlg
if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    
    app = QApplication([])
    w = DragDropLists.toDialog(srcWidgetMode=DragDropLists.Tree,
                               srcWidgetIsReadOnly=True)
        
    for i in range(12):
        w.form.addSrcEntry("L Eintrag %s" % i, 'entryL.%s' % i)
        #w.addTrgEntry("R Eintrag %s" % i, 'entryR.%s' % i)
    w.show()
    
    app.exec_()