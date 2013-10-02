#coding=utf-8
'''
Created on 04.03.2012

@author: michi
'''
import sys
import copy

from PyQt4.QtCore import QString, QObject
from PyQt4.QtGui import QTableView, QApplication, QDialog, QVBoxLayout, QPushButton

from ems.qt4.itemmodel.listofdictsmodel import ListOfDictsModel #@UnresolvedImport
from ems.qt4.gui.widgets.itemview.itemview_editor import ItemViewEditor
from ems.xtype.base import StringType, NumberType, UnitType, BoolType #@UnresolvedImport
from ems.qt4.itemmodel.addrow_proxymodel import AddRowProxyModel #@UnresolvedImport
from ems.xtype.base import DictType, SequenceType #@UnresolvedImport
from ems.qt4.gui.mapper.base import BaseMapper #@UnresolvedImport

import ems.unittests.qt4.mapper.baseconfig


testData = [{'vorname':'Leo','nachname':'Tils','alter':1,'gewicht':8.9,'einkommen':850.0,'verheiratet':False},
            {'vorname':'Kristina','nachname':'Bentz','alter':31,'gewicht':68.9,'einkommen':1450.0,'verheiratet':False},
            {'vorname':'Fabian','nachname':'Tils','alter':29,'gewicht':72.9,'einkommen':2850.0,'verheiratet':False},
            {'vorname':'Sonja','nachname':'Bentz','alter':28,'gewicht':65.9,'einkommen':450.0,'verheiratet':True},
            {'vorname':'Patrick','nachname':'Arnold','alter':29,'gewicht':79.6,'einkommen':3850.0,'verheiratet':False}]


class Importer(QObject):
    def __init__(self, model, parent):
        QObject.__init__(self, parent)
        self.model = model
    
    def importData(self):
        self.model.setModelData(copy.copy(testData))
        self.model.setStandardRow(1)
    
    def onIndexActivated(self, index):
        print 'activated:',index.row(), index.column()
    
    def onIndexDoubleClicked(self, index):
        print 'doubleClicked:',index.row(), index.column()
    
    def onIndexEntered(self, index):
        print 'entered:',index.row(), index.column()
    
    def onIndexPressed(self, index):
        print 'pressed:',index.row(), index.column()
        
    def onIndexClicked(self, index):
        print 'clicked:',index.row(), index.column()
    
    
        
app = QApplication(sys.argv)

dlg = QDialog()
dlg.setLayout(QVBoxLayout(dlg))
dlg.setWindowTitle("List of Dicts Model")

dlg.view = QTableView(dlg)

namenType = StringType()
namenType.minLength=1
namenType.maxLength=12

alterType = UnitType('Jahre', int)
alterType.minValue = 0
alterType.maxValue = 140
alterType.value2UnitSpace = 1

gewichtType = UnitType('kg', float)
gewichtType.minValue = 1
gewichtType.maxValue = 300
gewichtType.value2UnitSpace = 1
gewichtType.decimalsCount = 1
gewichtType.thousandsSeparator = '.'
gewichtType.decimalsSeparator = ','

geldType = UnitType(u'€', float)
geldType.minValue = 400.0
geldType.maxValue = 15000.0
geldType.value2UnitSpace = 1
geldType.decimalsCount = 2
geldType.thousandsSeparator = '.'
geldType.decimalsSeparator = ','

verheiratetType = BoolType()

lType = DictType()

lType.addKey('vorname', namenType)
lType.addKey('nachname', namenType)
lType.addKey('alter', alterType)
lType.addKey('gewicht', gewichtType)
lType.addKey('einkommen', geldType)
lType.addKey('verheiratet', verheiratetType)

lsType = SequenceType(lType)

model = ListOfDictsModel(lsType, dlg.view)

model.addRow({'vorname':'Leo','nachname':'Tils','alter':1,'gewicht':8.9,'einkommen':850.0,'verheiratet':True})
model.addRow(vorname='Fabian',nachname='Tils',alter=29,gewicht=67.2,einkommen=2600.0,verheiratet=False)

dlg.editor = ItemViewEditor(dlg.view, parent=dlg)

dlg.sourceModel = model
dlg.addModel = AddRowProxyModel(dlg)
dlg.addModel.setSourceModel(model)
dlg.view.setModel(dlg.addModel)
dlg.view.setMinimumSize(640, 480)
dlg.layout().addWidget(dlg.editor)


mapper = BaseMapper(dlg.sourceModel)
dlg.view.setItemDelegate(mapper.getDelegateForItemView(dlg.view))
#dlg.view.itemDelegate().setXTypeMap(dlg.view.model().xTypeMap())

dlg.exportButton = QPushButton("Export", dlg)
dlg.layout().addWidget(dlg.exportButton)
dlg.exportButton.clicked.connect(model.exportModelData)

dlg.importer = Importer(model, dlg)

dlg.view.pressed.connect(dlg.addModel.onIndexPressed)

#dlg.view.activated.connect(dlg.importer.onIndexActivated)
#dlg.view.clicked.connect(dlg.importer.onIndexClicked)
#dlg.view.doubleClicked.connect(dlg.importer.onIndexDoubleClicked)
#dlg.view.entered.connect(dlg.importer.onIndexEntered)
#dlg.view.pressed.connect(dlg.importer.onIndexPressed)


dlg.importButton = QPushButton("Import", dlg)
dlg.layout().addWidget(dlg.importButton)
dlg.importButton.clicked.connect(dlg.importer.importData)





sys.exit(dlg.exec_())