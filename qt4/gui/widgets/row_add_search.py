'''
Created on 23.06.2011

@author: michi
'''
import sys

from PyQt4.QtCore import QObject, QVariant, SIGNAL, SLOT, pyqtSignal, pyqtSlot
from PyQt4.QtGui import QWidget, QComboBox, QCheckBox, QLineEdit, QGridLayout, QPushButton

class SearchRow(QObject):
    
    rowEnabled = pyqtSignal(bool)
    rowDisabled = pyqtSignal(bool)
    
    def __init__(self, row, parent=None):
        super(SearchRow, self).__init__(parent)
        
        self._row = row
        self._enabled = True
        self.removeButton = None
        self.booleanOperatorButton = None
                    
        self.fieldInput = QComboBox()
        self.operatorInput = QComboBox()
        self.valueInput = QLineEdit()
        self.matchesInput = QCheckBox()
        self.setupUi()
        
        
    def reset(self):
        self.fieldInput.setCurrentIndex(0)
        self.valueInput.setText("")
    
    def setEnabled(self, enabled=True):
        for widget in (self.fieldInput, self.operatorInput,
                       self.valueInput, self.matchesInput):
            widget.setEnabled(enabled)
        self._enabled = enabled
        self.rowEnabled.emit(self._enabled)
        self.rowDisabled.emit(not self._enabled)
            
    def setDisabled(self, enabled=False):
        return self.setEnabled(enabled)
         
    def setupUi(self):
        self.fieldInput.addItem("Name")
        self.matchesInput.setChecked(True)
        self.matchesInput.setText(self.tr("Trifft zu"))
    
    def __del__(self):
        print "Destructor called"
    
    def delete(self):
        print "delete()"
    

class RowAddSearch(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self._rows = []
        self._addRowButton = None
        self.setupUi()
        #self.setStyleSheet("background-color: #fff")
        
    
    def setupUi(self):
        self.setLayout(QGridLayout(self))
#        print "layout.RowCount(%s)" % self.layout().rowCount()
#        self.layout().setColumnStretch(2,1)
#        self.layout().setColumnStretch(4,1)
        
        
        
        self.addRow()
    
    @property
    def addRowButton(self):
        return self.getAddRowButton()
    
    def getAddRowButton(self):
        if self._addRowButton is None:
            self._addRowButton = QPushButton("+",self)
            self.connect(self._addRowButton, SIGNAL("clicked()"),
                         self, SLOT('addRow()'))
        return self._addRowButton
    
    @property
    def booleanOperatorButton(self):
        return self.getBooleanOperatorButton()
    
    def getBooleanOperatorButton(self):
        widget = QComboBox()
        widget.setMinimumWidth(60)
        widget.setMaximumWidth(60)
        widget.addItem("Und", QVariant("AND"))
        widget.addItem("Oder", QVariant("OR"))
        return widget
    
    def getBooleanOperatorPlaceHolder(self):
        widget = QWidget()
        widget.setMinimumWidth(60)
        widget.setMaximumWidth(60)
        return widget
    
    def getRemoveButton(self):
        return QPushButton("-")

        
    @pyqtSlot()
    def _onDeleteClicked(self):
        searchRow = self.sender().row
        i = 0
        for row in self._rows:
            if row is searchRow:
                self.removeRow(i)
                break
            i += 1 
            
    
    @pyqtSlot()
    def addRow(self):
        #print "addRow"
        currentRow = len(self._rows)
        if currentRow < 0:
            currentRow = 0
            
        row = SearchRow(currentRow, self)
        
        layout = self.layout()
        #layoutRow = layout.rowCount()
        layoutRow = currentRow
        
        removeButton = self.getRemoveButton()
        removeButton.row = row
        
        row.removeButton = removeButton
#        print "layout.RowCount(%s)" % self.layout().rowCount()
        
        layout.addWidget(removeButton,layoutRow,0)
        
        if currentRow == 0:
            booleanOperatorButton = self.getBooleanOperatorPlaceHolder()
        else:
            booleanOperatorButton = self.getBooleanOperatorButton()
        
        row.booleanOperatorButton = booleanOperatorButton
            
        layout.addWidget(booleanOperatorButton,layoutRow,1)
        
        
        layout.addWidget(row.fieldInput, layoutRow,2)
        layout.addWidget(row.operatorInput, layoutRow,3)
        row.valueInput.setText("%s" % layoutRow)
        layout.addWidget(row.valueInput, layoutRow,4)
        layout.addWidget(row.matchesInput, layoutRow,5)
        
        layout.addWidget(self.addRowButton, layoutRow+1,0)
        
        self.connect(removeButton, SIGNAL("clicked()"),
                     self, SLOT('_onDeleteClicked()'))
        self._rows.append(row)
#        print "nach addRow RowCount: %s" % self.layout().rowCount()
    
    def _repopulateRows(self):
        layout = self.layout()
        for i in range(len(self._rows)):
            layout.addWidget(self._rows[i].removeButton,i,0)
            if i == 0:
                if isinstance(self._rows[i].booleanOperatorButton, QComboBox):
                    self.layout().removeWidget(self._rows[i].booleanOperatorButton)
                    self._rows[i].booleanOperatorButton.close()
                    self._rows[i].booleanOperatorButton.setParent(None)
                    del self._rows[i].booleanOperatorButton
                    self._rows[i].booleanOperatorButton = self.getBooleanOperatorPlaceHolder()
            layout.addWidget(self._rows[i].booleanOperatorButton,i,1)
            layout.addWidget(self._rows[i].fieldInput, i,2)
            layout.addWidget(self._rows[i].operatorInput, i,3)
            layout.addWidget(self._rows[i].valueInput, i,4)
            layout.addWidget(self._rows[i].matchesInput, i,5)
            
            layout.addWidget(self.addRowButton, i+1,0)
    
    def removeRow(self, idx):
        if len(self._rows) < 2:
            return
        row = self._rows[idx]
#        print "removeRow %s" % idx
        
        for widget in (row.removeButton,row.booleanOperatorButton,
                       row.fieldInput, row.operatorInput, row.valueInput,
                       row.matchesInput):
            
            self.layout().removeWidget(widget)
            widget.setParent(None)
            widget.close()
            del widget
        
        self._rows.remove(row)
        row.delete()
        del row
        
        self._repopulateRows()
        
#        print "removeRow RowCount: %s" % self.layout().rowCount()
        #del row
        

if __name__ == "__main__":
    from PyQt4.QtGui import QApplication
    app = QApplication([])
    ras = RowAddSearch()
    ras.show()
    app.exec_()