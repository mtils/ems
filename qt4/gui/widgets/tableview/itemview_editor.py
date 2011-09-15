#coding=utf-8
'''
Created on 15.09.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSignal, pyqtSlot
from PyQt4.QtGui import QWidget, QPushButton, QHBoxLayout, QVBoxLayout,\
    QAbstractItemView

def enum(**enums):
    return type('Enum', (), enums)

class ItemViewEditor(QWidget):
    
    INSERT_END = 0
    INSERT_PRIOR_CURRENT = 1
    INSERT_AFTER_CURRENT = 2
    
    isRowSelectedStateChanged = pyqtSignal(bool)
    lastSelectedRowChanged = pyqtSignal(int)
    
    def __init__(self, itemView, parent=None):
        QWidget.__init__(self, parent)
        if not isinstance(itemView, QAbstractItemView):
            raise TypeError("itemView has to be instanceof QAbstractItemView")
        self.itemView = itemView
        self.itemView.selectionModel().\
            selectionChanged.connect(self._checkSelection)
        self.insertMode = self.INSERT_END
        self.lastSelectedRow = None
        self._isRowSelected = None 
        self.setupUi()
        self._checkSelection()
    
    def _setIsRowSelected(self, isSelected):
        if self._isRowSelected != isSelected:
            self._isRowSelected = isSelected
            self.isRowSelectedStateChanged.emit(self._isRowSelected)
    
    @property
    def isRowSelected(self):
        return self._isRowSelected
    
    def _checkSelection(self, itemSelection=None, itemDeselection=None):
        hasSelection = False
        for idx in self.itemView.selectionModel().selection().indexes():
            hasSelection = True
            lastSelectedRow = idx.row()
        if hasSelection:
            self._setIsRowSelected(True)
            self.lastSelectedRow = lastSelectedRow
        else:
            self._setIsRowSelected(False)
            self.lastSelectedRow = None
        
    def setupUi(self):
        self.setLayout(QHBoxLayout(self))
        self.layout().addWidget(self.itemView)
        self.buttonContainer = QWidget(self)
        self.layout().addWidget(self.buttonContainer)
        
        self.buttonContainer.setLayout(QVBoxLayout(self.buttonContainer))
        
        self.addButton = QPushButton(self.trUtf8(u"Hinzufügen"), self)
        self.addButton.clicked.connect(self.onAddButtonClicked)
        self.buttonContainer.layout().addWidget(self.addButton)
        
        self.editButton = QPushButton(self.trUtf8(u"Bearbeiten"), self)
        self.editButton.clicked.connect(self.onEditButtonClicked)
        self.isRowSelectedStateChanged.connect(self.editButton.setEnabled)
        self.buttonContainer.layout().addWidget(self.editButton)
        
        self.deleteButton = QPushButton(self.trUtf8(u"Löschen"), self)
        self.deleteButton.clicked.connect(self.onDeleteButtonClicked)
        self.isRowSelectedStateChanged.connect(self.deleteButton.setEnabled)
        self.buttonContainer.layout().addWidget(self.deleteButton)
        
        self.buttonContainer.layout().addStretch()
    
    def onAddButtonClicked(self):
        print "addButtonClicked"
        if self.insertMode in (self.INSERT_PRIOR_CURRENT,
                               self.INSERT_AFTER_CURRENT):
            idx = self.itemView.currentIndex()
            
            if idx.isValid():
                if self.insertMode == self.INSERT_PRIOR_CURRENT:
                    self.itemView.model().insertRow(idx.row())
                    return
                else:
                    self.itemView.model().insertRow(idx.row()+1)
                    return

        self.itemView.model().insertRow(self.itemView.model().rowCount())
    
    def onEditButtonClicked(self):
        print "editButtonClicked"
    
    def onDeleteButtonClicked(self):
        print "deleteButtonClicked"
        

if __name__ == '__main__':
    from PyQt4.QtGui import QApplication, QTableView, QStandardItemModel,\
        QStandardItem
    app = QApplication([])
    view = QTableView()
    model = QStandardItemModel(view)
    view.setModel(model)
    for i in range(4):
        model.appendRow((QStandardItem("Item %s 0" % i),
                         QStandardItem("Item %s 1" % i),
                         QStandardItem("Item %s 2" % i)))
    editor = ItemViewEditor(view, parent=None)
    #editor.insertMode = editor.INSERT_AFTER_CURRENT
    editor.show()
    
    app.exec_()