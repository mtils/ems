#coding=utf-8
'''
Created on 19.11.2011

@author: michi
'''
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog, QFormLayout, QDialogButtonBox, QVBoxLayout,\
    QLineEdit, QComboBox

class SearchDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        formLayout = QFormLayout()
        vbox = QVBoxLayout()
        
        self._searchTermEdit = QLineEdit(self)
        formLayout.addRow("Suche nach", self._searchTermEdit)
        
        self._whereCombo = QComboBox(self)
        self._whereCombo.addItem(self.trUtf8("In der Nähe (<10km)"), 10000)
        self._whereCombo.addItem(self.trUtf8("Innerhalb 30min Fahrt von mir (<25km)"), 25000)
        self._whereCombo.addItem(self.trUtf8("Innerhalb 100km von mir"), 100000)
        self._whereCombo.addItem(self.trUtf8("Irgendwo in der Welt"), -1)
        self._whereCombo.setCurrentIndex(1)
        
        formLayout.addRow("Wo", self._whereCombo)
        
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                              Qt.Horizontal)
        
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        
        vbox.addLayout(formLayout)
        vbox.addWidget(bb)
        self.setLayout(vbox)
        self.setWindowTitle(self.trUtf8("Such nach Ort"))
    
    def radius(self):
        i = self._whereCombo.currentIndex()
        return self._whereCombo.itemData(i).toReal()[0]
    
    def searchTerms(self):
        return self._searchTermEdit.text()
        