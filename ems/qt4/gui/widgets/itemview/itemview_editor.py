#coding=utf-8
'''
Created on 15.09.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSignal, pyqtSlot, QTimer, SLOT
from PyQt4.QtGui import QWidget, QPushButton, QHBoxLayout, QVBoxLayout,\
    QAbstractItemView

def enum(**enums):
    return type('Enum', (), enums)

class ItemViewEditor(QWidget):
    
    INSERT_END = 0
    INSERT_PRIOR_CURRENT = 1
    INSERT_AFTER_CURRENT = 2
    
    isRowSelectedStateChanged = pyqtSignal(bool)
    rowInsertionRequested = pyqtSignal(int,int)
    rowEditingRequested = pyqtSignal(list)
    rowDeletionRequested = pyqtSignal(list)
    firstSelectedRowChanged = pyqtSignal(int)
    
    def __init__(self, itemView, connectOwnMethods=True, parent=None):
        QWidget.__init__(self, parent)
        
        if not isinstance(itemView, QAbstractItemView):
            raise TypeError("itemView has to be instanceof QAbstractItemView")
        self.itemView = itemView
        self._tryToConnectToSelectionModel()
                
        self.insertMode = self.INSERT_END
        self.lastSelectedRow = None
        self._isRowSelected = None 
        self.setupUi()
        self._checkSelection()
        if connectOwnMethods:
            self.rowInsertionRequested.connect(self.addRows)
            self.rowDeletionRequested.connect(self.deleteRows)
    
    def _setIsRowSelected(self, isSelected):
        if self._isRowSelected != isSelected:
            self._isRowSelected = isSelected
            self.isRowSelectedStateChanged.emit(self._isRowSelected)
    
    @pyqtSlot()
    def _tryToConnectToSelectionModel(self):
        if self.itemView.selectionModel() is not None:
            self.itemView.selectionModel().\
                selectionChanged.connect(self._checkSelection)
        else:
            QTimer.singleShot(200, self,
                              SLOT('_tryToConnectToSelectionModel()'))
    
    @property
    def isRowSelected(self):
        return self._isRowSelected
    
    def _checkSelection(self, itemSelection=None, itemDeselection=None):
        hasSelection = False
        
        if self.itemView.selectionModel() is None:
            return
        
        for idx in self.itemView.selectionModel().selection().indexes():
            hasSelection = True
            lastSelectedRow = idx.row()
        if hasSelection:
            self._setIsRowSelected(True)
            if self.lastSelectedRow != lastSelectedRow:
                self.firstSelectedRowChanged.emit(lastSelectedRow)
            self.lastSelectedRow = lastSelectedRow
        else:
            self._setIsRowSelected(False)
            self.lastSelectedRow = None

    @property
    def currentRow(self):
        return self.lastSelectedRow

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
        
        self.standardButton = QPushButton(self.trUtf8(u"Als Standard setzen"), self)
        self.standardButton.clicked.connect(self.onStandardButtonClicked)
        self.isRowSelectedStateChanged.connect(self.standardButton.setEnabled)
        self.buttonContainer.layout().addWidget(self.standardButton)
        self.standardButton.hide()
        
        self.buttonContainer.layout().addStretch()

    @property
    def selectedRows(self):
        rowList = []
        for idx in self.itemView.selectionModel().selection().indexes():
            if idx.row() not in rowList:
                rowList.append(idx.row())
        return rowList

    def onStandardButtonClicked(self):
        if hasattr(self.itemView.model(),'setStandardRow'):
            self.itemView.model().setStandardRow(self.selectedRows[0])
    
    def onAddButtonClicked(self):
        if self.insertMode in (self.INSERT_PRIOR_CURRENT,
                               self.INSERT_AFTER_CURRENT):
            idx = self.itemView.currentIndex()
            if idx.isValid():
                if self.insertMode == self.INSERT_PRIOR_CURRENT:
                    self.rowInsertionRequested.emit(idx.row(), 1)
                    return
                else:
                    self.rowInsertionRequested.emit(idx.row()+1, 1)
                    return
        self.rowInsertionRequested.emit(self.itemView.model().rowCount(), 1)
    
    def addRows(self, targetRow, count):
        self.itemView.model().insertRows(targetRow, count)
    
    def onEditButtonClicked(self):
        if self.isRowSelected:
            self.rowEditingRequested.emit(self.selectedRows)
    
    def onDeleteButtonClicked(self):
        if self.isRowSelected:
            self.rowDeletionRequested.emit(self.selectedRows)
            
    
    def deleteRows(self, rows):
        model = self.itemView.model()
        if hasattr(model, 'removeRowList'):
            model.removeRowList(rows)
        else:
            for row in rows:
                self.itemView.model().removeRows(row,1)
                break
        

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
    #editor.editButton.hide()
#    editor.insertMode = editor.INSERT_PRIOR_CURRENT
    editor.show()
    
    app.exec_()