#coding=utf-8
'''
Created on 04.03.2012

@author: michi
'''
import sys
import copy

from PyQt4.QtCore import QString, QObject, Qt, QSize
from PyQt4.QtGui import QTableView, QApplication, QDialog, QVBoxLayout, \
    QPushButton, QTableWidget, QStyledItemDelegate, QStyle, QStyleOptionViewItemV4,\
    QDialog

from ems.qt4.gui.widgets.itemview.itemview_editor import ItemViewEditor
from ems.xtype.base import StringType, NumberType, UnitType, BoolType #@UnresolvedImport
from ems.xtype.base import DictType #@UnresolvedImport
from ems.qt4.itemmodel.xtype.dictmodel import DictModel #@UnresolvedImport
from ems.qt4.gui.mapper.base import BaseMapper #@UnresolvedImport

import pprint


testData = {'vorname':'Leo','nachname':'Tils','alter':1,'gewicht':8.9,'einkommen':850.0,'verheiratet':False}

import ems.unittests.qt4.mapper.baseconfig

class Importer(QObject):
    def __init__(self, model, parent):
        QObject.__init__(self, parent)
        self.model = model
    
    def importData(self):
        self.model.setModelData(copy.copy(testData))
    
    def exportData(self):
        pprint.pprint(self.model.modelData())
        
app = QApplication(sys.argv)

dlg = QDialog()
dlg.setLayout(QVBoxLayout(dlg))
dlg.setWindowTitle("NamedField-Model")

dlg.view = QTableView(dlg)

namenType = StringType()
namenType.minLength=1
namenType.maxLength=12

alterType = UnitType('Jahre', int)
alterType.minValue = 0
alterType.maxValue = 140
alterType.value2UnitSpace = 1
alterType.defaultValue = 18

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

dictType = DictType(canBeNone=True)
dictType.addKey('vorname', namenType)
dictType.addKey('nachname', namenType)
dictType.addKey('alter', alterType)
dictType.addKey('gewicht', gewichtType)
dictType.addKey('einkommen', geldType)
dictType.addKey('verheiratet', verheiratetType)

model = DictModel(dictType, dlg.view)

model.setKeyLabel('vorname', QString.fromUtf8('Name'))
model.setKeyLabel('nachname', QString.fromUtf8('Familienname'))
model.setKeyLabel('alter', QString.fromUtf8('Alter'))
model.setKeyLabel('gewicht', QString.fromUtf8('Gewicht'))
model.setKeyLabel('einkommen', QString.fromUtf8('Einkommen'))
model.setKeyLabel('verheiratet', QString.fromUtf8('Verheiratet'))

model.addRow({'vorname':'Leo','nachname':'Tils','alter':1,'gewicht':8.9,'einkommen':850.0,'verheiratet':True})
#model.addRow(vorname='Fabian',nachname='Tils',alter=29,gewicht=67.2,einkommen=2600.0,verheiratet=False)
#model.addRow

dlg.editor = ItemViewEditor(dlg.view, parent=dlg)
dlg.view.setModel(model)
dlg.view.setMinimumSize(640, 480)
dlg.layout().addWidget(dlg.editor)

dlg.mapper = BaseMapper(model)
dlg.delegate = dlg.mapper.getDelegateForItemView(dlg.view)
dlg.view.setItemDelegate(dlg.delegate)

dlg.exportButton = QPushButton("Export", dlg)
dlg.layout().addWidget(dlg.exportButton)


dlg.importer = Importer(model, dlg)
dlg.importButton = QPushButton("Import", dlg)
dlg.layout().addWidget(dlg.importButton)
dlg.importButton.clicked.connect(dlg.importer.importData)
dlg.exportButton.clicked.connect(dlg.importer.exportData)

sys.exit(dlg.exec_())