'''
Created on 23.06.2011

@author: michi
'''
import sys

from PyQt4.QtCore import QObject, QVariant, SIGNAL, SLOT, pyqtSignal, pyqtSlot
from PyQt4.QtGui import QWidget, QComboBox, QCheckBox, QLineEdit, QGridLayout

class SearchRow(QObject):
    
    rowEnabled = pyqtSignal(bool)
    rowDisabled = pyqtSignal(bool)
    
    def __init__(self, row, parent=None):
        super(SearchRow, self).__init__(parent)
        self._row = row
        if self._row == 0:
            self.logicalInput = QWidget(parent)
            self.logicalInput.setMinimumWidth(80)
        else:
            self.logicalInput = QComboBox(parent)
            self.connect(self.logicalInput, SIGNAL("currentIndexChanged(int)"),
                         self, SLOT("onLogicalCurrentIndexChanged(int)"))
            
        self.fieldInput = QComboBox(parent)
        self.operatorInput = QComboBox(parent)
        self.valueInput = QLineEdit(parent)
        self.matchesInput = QCheckBox(parent)
        self.setupUi()
        self._enabled = True
        if self._row != 0:
            self.setDisabled()
    
    @pyqtSlot(int)
    def onLogicalCurrentIndexChanged(self, index):
        if self.logicalInput.itemData(index).toString() == "NONE":
            self.setDisabled()
        else:
            if not self._enabled:
                self.setEnabled()
    
    def setEnabled(self, enabled=True):
        for widget in (self.fieldInput, self.operatorInput, self.valueInput,
                       self.matchesInput):
            widget.setEnabled(enabled)
        self._enabled = enabled
        self.rowEnabled.emit(self._enabled)
        self.rowDisabled.emit(not self._enabled)
            
    def setDisabled(self, enabled=False):
        return self.setEnabled(enabled)
         
    def setupUi(self):
        if self._row != 0:
            self.logicalInput.addItem(self.tr("Aktivieren"), QVariant("NONE"))
            self.logicalInput.addItem(self.tr("Und"), QVariant("AND"))
            self.logicalInput.addItem(self.tr("Oder"), QVariant("OR"))
        
        self.fieldInput.addItem("Name")
        self.matchesInput.setChecked(True)
        self.matchesInput.setText(self.tr("Trifft zu"))

class RowAddSearch(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self._rows = []
        self.setupUi()
    
    def setupUi(self):
        self.setLayout(QGridLayout(self))
        self.addRow()
        self.addRow()
    
    @pyqtSlot()
    def addRow(self):
        print "addRow"
        currentRow = len(self._rows)
        if currentRow < 0:
            currentRow = 0

        row = SearchRow(currentRow, self)
        layout = self.layout()
        layout.addWidget(row.logicalInput,currentRow,0)
        layout.addWidget(row.fieldInput,currentRow,1)
        layout.addWidget(row.operatorInput,currentRow,2)
        layout.addWidget(row.valueInput,currentRow,3)
        layout.addWidget(row.matchesInput,currentRow,4)
        
        self.connect(row, SIGNAL('rowEnabled(bool)'),
                     self, SLOT('addRow()'))
        self._rows.append(row)

if __name__ == "__main__":
    from PyQt4.QtGui import QApplication
    app = QApplication([])
    ras = RowAddSearch()
    ras.show()
    app.exec_()