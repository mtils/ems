#coding=utf-8
'''
Created on 04.03.2012

@author: michi
'''
import sys
import copy
import pprint

from PyQt4.QtCore import QString, QObject, Qt, QSize
from PyQt4.QtGui import QTableView, QApplication, QDialog, QVBoxLayout, \
    QPushButton, QTableWidget, QStyledItemDelegate, QStyle, QStyleOptionViewItemV4,\
    QDialog

from ems.qt4.itemmodel.listofdictsmodel import ListOfDictsModel #@UnresolvedImport
from ems.qt4.gui.widgets.itemview.itemview_editor import ItemViewEditor
from ems.xtype.base import StringType, NumberType, UnitType, BoolType #@UnresolvedImport
from ems.qt4.util import variant_to_pyobject
from ems.qt4.gui.mapper.base import BaseMapper #@UnresolvedImport
from ems.xtype.base import SequenceType, DictType #@UnresolvedImport


testData = [{'vorname':'Leo','nachname':'Tils','alter':1,'gewicht':8.9,'einkommen':850.0,'verheiratet':False},
            {'vorname':'Kristina','nachname':'Bentz','alter':31,'gewicht':68.9,'einkommen':1450.0,'verheiratet':False},
            {'vorname':'Fabian','nachname':'Tils','alter':29,'gewicht':72.9,'einkommen':2850.0,'verheiratet':False},
            {'vorname':'Sonja','nachname':'Bentz','alter':28,'gewicht':65.9,'einkommen':450.0,'verheiratet':True},
            {'vorname':'Patrick','nachname':'Arnold','alter':29,'gewicht':79.6,'einkommen':3850.0,'verheiratet':False}]

#import ems.unittests.qt4.mapper.baseconfig
from examples.qt4.bootstrap.create_app import create_app

class Importer(QObject):
    def __init__(self, model, parent):
        QObject.__init__(self, parent)
        self.model = model
    
    def importData(self):
        self.model.setModelData(copy.copy(testData))
        self.model.setStandardRow(1)
    
    def exportData(self):
        pprint.pprint(self.model.exportModelData())

#app.started

app = create_app(sys.argv, sys.argv[0], 'testing')

def testDialog(app):
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

    itemType = DictType()
    itemType.addKey('vorname', namenType)
    itemType.addKey('nachname', namenType)
    itemType.addKey('alter', alterType)
    itemType.addKey('gewicht', gewichtType)
    itemType.addKey('einkommen', geldType)
    itemType.addKey('verheiratet', verheiratetType)
    itemType.maxLength = 8
    itemType.minLength = 1

    listType = SequenceType(itemType)
    model = ListOfDictsModel(listType, dlg.view)

    model.setKeyLabel('vorname', QString.fromUtf8('Name'))
    model.setKeyLabel('nachname', QString.fromUtf8('Familienname'))
    model.setKeyLabel('alter', QString.fromUtf8('Alter'))
    model.setKeyLabel('gewicht', QString.fromUtf8('Gewicht'))
    model.setKeyLabel('einkommen', QString.fromUtf8('Einkommen'))
    model.setKeyLabel('verheiratet', QString.fromUtf8('Verheiratet'))

    model.addRow({'vorname':'Leo','nachname':'Tils','alter':1,'gewicht':8.9,'einkommen':850.0,'verheiratet':True})
    model.addRow(vorname='Fabian',nachname='Tils',alter=29,gewicht=67.2,einkommen=2600.0,verheiratet=False)
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
    
    dlg.exec_()


app.started += testDialog

sys.exit(app.start(sys.argv[0], sys.argv))