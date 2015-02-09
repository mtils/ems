'''
Created on 23.06.2011

@author: michi
'''
import sys
import time
from PyQt4.QtCore import QObject, QVariant, SIGNAL, SLOT, pyqtSignal, pyqtSlot, \
    Qt, QString, QTimer
from PyQt4.QtGui import QWidget, QComboBox, QCheckBox, QLineEdit, QGridLayout, \
    QPushButton, QTreeWidgetItem, QStackedWidget, QIcon, QSpinBox, QDoubleSpinBox

from ems.qt4.gui.widgets.treecombo import TreeComboBox #@UnresolvedImport
from ems.qt4.gui.widgets.bigcombo import BigComboBox #@UnresolvedImport
from ems.qt4.util import variant_to_pyobject #@UnresolvedImport
from ems.model.sa.orm.base_object import OrmBaseObject #@UnresolvedImport

class BuilderBackend(QObject):
    def setSearchWidget(self, widget):
        self._searchWidget = widget
    
    def populateFieldInput(self, fieldInput):
        pass

    def rowAdded(self, row):
        pass
    
    def onFieldInputCurrentFieldChanged(self, searchRow, item):
        pass
    
    def buildQuery(self, criterias):
        raise NotImplementedError("Please create a buildQuery Method")

class SearchRow(QObject):
    
    rowEnabled = pyqtSignal(bool)
    rowDisabled = pyqtSignal(bool)
    
    def __init__(self, builder, parent=None):
        super(SearchRow, self).__init__(parent)
        
        self._builder = builder
        self._enabled = True
        self.removeButton = None
        self.conjunctionButton = None
                    
        self.fieldInput = TreeComboBox()
        self.fieldInput.setMinimumWidth(200)
        self.operatorInput = QComboBox()
        self.operatorInput.setMinimumContentsLength(12)
        self.valueStack = QStackedWidget()
        self.valueStack.setMaximumHeight(50)
        self.valueStack.setMinimumHeight(25)
        self.valueInput = QLineEdit()
        self.valueStack.addWidget(self.valueInput)
        self.matchesInput = QCheckBox()
        
        
        self.connect(self.fieldInput, SIGNAL("currentIndexChanged(int)"),
                     self, SLOT("onFieldInputCurrentIndexChanged(int)"))
        self.setupUi()
        
#        self.connect(self.fieldInput, SIGNAL("currentIndexChanged(QString)"),
#                     self, SLOT("onFieldInputCurrentTextChanged(QString)"))
#        
        #self.onFieldInputCurrentIndexChanged(0)
    
    def replaceValueInput(self, widget):
        self.valueStack.removeWidget(self.valueInput)
        i = self.valueStack.addWidget(widget)
        self.valueStack.setCurrentIndex(i)
        self.valueInput = widget
    
    @pyqtSlot(QString)
    def onFieldInputCurrentTextChanged(self, text):
        pass
    
    @pyqtSlot(int)
    def onFieldInputCurrentIndexChanged(self, index):
        field = unicode(self.fieldInput.itemData(index).toString())
        self._builder.onFieldInputCurrentFieldChanged(self, field)
        
    def reset(self):
        self.fieldInput.setCurrentIndex(0)
        #self.valueInput.setText("")
    
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
        #self.fieldInput.addItem("Name")
        self._builder.populateFieldInput(self.fieldInput)
        self.matchesInput.setChecked(True)
        self.matchesInput.setText(self.tr("Trifft zu"))
    
    def __del__(self):
        pass
    
    def delete(self):
        pass
    

class RowAddSearch(QWidget):
    
    rowAdded = pyqtSignal(int)
    queryChanged = pyqtSignal(object)
    
    modelObjectPrefix = '{{|'
    modelObjectSuffix = '|}}'
    
    def __init__(self, builderBackend=None, parent=None,
                 buttonFactory=None):
        QWidget.__init__(self, parent)
        if builderBackend is None:
            builderBackend = BuilderBackend()
        self._builder = builderBackend
        self._builder.setSearchWidget(self)
        
        self._rows = []
        self._addRowButton = None
        self._buttonFactory = buttonFactory
        self.setupUi()
        
        #self.setStyleSheet("background-color: #fff")
        
    
    def setupUi(self):
        self.setLayout(QGridLayout(self))
        
        self.addRow()
    
    @property
    def addRowButton(self):
        return self.getAddRowButton()
    
    def getAddRowButton(self):
        if self._addRowButton is None:
            if self._buttonFactory is None:
                self._addRowButton = QPushButton("+",self)
            else:
                self._addRowButton = self._buttonFactory('add')
                
            self.connect(self._addRowButton, SIGNAL("clicked()"),
                         self, SLOT('addRow()'))
        return self._addRowButton
    
    @property
    def conjunctionButton(self):
        return self.getConjunctionButton()
    
    def getConjunctionButton(self):
        widget = QComboBox()
        widget.setMinimumWidth(60)
        widget.setMaximumWidth(60)
        widget.addItem("Und", QVariant("AND"))
        widget.addItem("Oder", QVariant("OR"))
        return widget
    
    def getConjunctionPlaceHolder(self):
        widget = QWidget()
        widget.setMinimumWidth(60)
        widget.setMaximumWidth(60)
        return widget
    
    def getRemoveButton(self):
        if self._buttonFactory is None:
            button = QPushButton("-",self)
        else:
            button = self._buttonFactory('remove')
            
        return button
    

        
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
            
        row = SearchRow(self._builder, self)
        
        layout = self.layout()
        #layoutRow = layout.rowCount()
        layoutRow = currentRow
        
        removeButton = self.getRemoveButton()
        removeButton.row = row
        
        row.removeButton = removeButton
#        print "layout.RowCount(%s)" % self.layout().rowCount()
        
        layout.addWidget(removeButton,layoutRow,0)
        
        if currentRow == 0:
            conjunctionButton = self.getConjunctionPlaceHolder()
        else:
            conjunctionButton = self.getConjunctionButton()
        
        row.conjunctionButton = conjunctionButton
            
        layout.addWidget(conjunctionButton,layoutRow,1)
        
        
        layout.addWidget(row.fieldInput, layoutRow,2)
        layout.addWidget(row.operatorInput, layoutRow,3)
        #row.valueInput.setText("%s" % layoutRow)
        #layout.addWidget(row.valueInput, layoutRow,4)
        layout.addWidget(row.valueStack, layoutRow,4)
        layout.addWidget(row.matchesInput, layoutRow,5)
        
        layout.addWidget(self.addRowButton, layoutRow+1,0)
        
        self.connect(removeButton, SIGNAL("clicked()"),
                     self, SLOT('_onDeleteClicked()'))
        self._rows.append(row)
        self._builder.rowAdded(row)
        self.rowAdded.emit(currentRow)
#        print "nach addRow RowCount: %s" % self.layout().rowCount()
    
    def _repopulateRows(self):
        layout = self.layout()
        for i in range(len(self._rows)):
            layout.addWidget(self._rows[i].removeButton,i,0)
            if i == 0:
                if isinstance(self._rows[i].conjunctionButton, QComboBox):
                    self.layout().removeWidget(self._rows[i].conjunctionButton)
                    self._rows[i].conjunctionButton.close()
                    self._rows[i].conjunctionButton.setParent(None)
                    del self._rows[i].conjunctionButton
                    self._rows[i].conjunctionButton = self.getConjunctionPlaceHolder()
            layout.addWidget(self._rows[i].conjunctionButton,i,1)
            layout.addWidget(self._rows[i].fieldInput, i,2)
            layout.addWidget(self._rows[i].operatorInput, i,3)
            layout.addWidget(self._rows[i].valueStack, i,4)
            layout.addWidget(self._rows[i].matchesInput, i,5)
            
            layout.addWidget(self.addRowButton, i+1,0)
    
    @pyqtSlot()
    def removeRow(self, idx=0):
        if len(self._rows) < 2:
            return
        row = self._rows[idx]
#        print "removeRow %s" % idx
        
        for widget in (row.removeButton,row.conjunctionButton,
                       row.fieldInput, row.operatorInput, row.valueStack,
                       row.matchesInput):
            
            self.layout().removeWidget(widget)
            widget.setParent(None)
            widget.close()
            del widget
        
        self._rows.remove(row)
        row.delete()
        del row
        
        self._repopulateRows()
    
    def buildQuery(self,**kwargs):
        #print "buildQuery called"
        clauses = []
        for row in self._rows:
            
            clauses.append({
                            'conjunction': self.extractValueOfWidget(row.conjunctionButton),
                            'field': self.extractValueOfWidget(row.fieldInput),
                            'operator': self.extractValueOfWidget(row.operatorInput),
                            'value': self.extractValueOfWidget(row.valueInput),
                            'matches': self.extractValueOfWidget(row.matchesInput)
                            })
        
        query = self._builder.buildQuery(clauses,**kwargs)
        self.queryChanged.emit(query)
        return query
    
    def extractValueOfWidget(self, widget):
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        if isinstance(widget, TreeComboBox):
            return variant_to_pyobject(widget.value())
        if isinstance(widget, BigComboBox):
            return variant_to_pyobject(widget.value())
        if isinstance(widget, QComboBox):
            return variant_to_pyobject(widget.itemData(widget.currentIndex(), Qt.UserRole))
        if hasattr(widget, 'value') and callable(widget.value):
            return widget.value()
        if hasattr(widget, 'text') and callable(widget.text):
            return widget.text()
    
    def setValueOfWidget(self, widget, value):
        if value is None:
            return
        if isinstance(widget, QCheckBox) and isinstance(value, bool):
            widget.setChecked(value)
            return
        if isinstance(widget, TreeComboBox):
            widget.setValue(value)
            return
        if isinstance(widget, BigComboBox) and isinstance(value, basestring):
            #widget.setEditText(value)
            return
        if isinstance(widget, QComboBox):
            index = widget.findText(value)
            widget.setCurrentIndex(index)
            return
        if hasattr(widget, 'setValue') and callable(widget.setValue):
            widget.setValue(value)
            return
        if hasattr(widget, 'setText') and callable(widget.setText) and isinstance(value, basestring):
            widget.setText(QString.fromUtf8(value))
            return
    
    def getConfig(self):
        config = []
        for row in self._rows:
            value = self.extractValueOfWidget(row.valueInput)
            if isinstance(value, QString):
                value = unicode(value)
            if isinstance(value, OrmBaseObject):
                value = value.__ormDecorator__().getReprasentiveString(value)
            config.append({
                            'conjunction': self.extractValueOfWidget(row.conjunctionButton),
                            'field': unicode(self.extractValueOfWidget(row.fieldInput)),
                            'operator': self.extractValueOfWidget(row.operatorInput),
                            'value': value,
                            'matches': self.extractValueOfWidget(row.matchesInput)
                            })
        return config
    
    def clear(self):
        timeBetween = 150
        for i in range(len(self._rows)):
            nextTime = i*timeBetween
            QTimer.singleShot(nextTime, self, SLOT('removeRow()'))
        return nextTime
    
    def setConfigValues(self, config):
        msecs = self.clear()
        QTimer.singleShot(msecs, self, SLOT("_applyCurrentConfig()"))
        self._currentConfig = config
        
    @pyqtSlot()
    def _applyCurrentConfig(self):
        i = 0
        c = self._currentConfig
        for row in c:
            if i > 0:
                self.addRow()
            if isinstance(self._rows[i].conjunctionButton, QComboBox):
                index = self._rows[i].conjunctionButton.findData(QVariant(row['conjunction']))
                self._rows[i].conjunctionButton.setCurrentIndex(index)
            
            if isinstance(self._rows[i].fieldInput, TreeComboBox):
                self._rows[i].fieldInput.setValue(row['field'])
            
            if isinstance(self._rows[i].operatorInput, QComboBox):
                index = self._rows[i].operatorInput.findData(QVariant(row['operator']))
                self._rows[i].operatorInput.setCurrentIndex(index)
            
            self.setValueOfWidget(self._rows[i].valueInput, row['value'])
            
            if isinstance(self._rows[i].matchesInput, QCheckBox) and isinstance(row['matches'], bool):
                self._rows[i].matchesInput.setChecked(row['matches'])
            else:
                self._rows[i].matchesInput.setChecked(True)
                
            
            i += 1
        

if __name__ == "__main__":
    from PyQt4.QtGui import QApplication
    app = QApplication([])
    ras = RowAddSearch()
    ras.show()
    app.exec_()