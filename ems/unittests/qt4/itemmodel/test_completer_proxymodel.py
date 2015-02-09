#coding=utf-8
'''
Created on 22.03.2013

@author: michi
'''
import sys
import copy
import pprint

from PyQt4.QtCore import QString, QObject, Qt, QSize, QModelIndex, QRegExp, \
    QStringList, QAbstractItemModel
from PyQt4.QtGui import QTableView, QApplication, QDialog, QVBoxLayout, \
    QPushButton, QTableWidget, QStyledItemDelegate, QStyle, QStyleOptionViewItemV4,\
    QDialog, QHBoxLayout, QGroupBox, QLineEdit, QCompleter, QComboBox, QSortFilterProxyModel

from ems.qt4.itemmodel.listofdictsmodel import ListOfDictsModel #@UnresolvedImport
from ems.qt4.itemmodel.proxy.stringsummary import StringSummaryProxyModel
from ems.qt4.gui.completer.fuzzy import FuzzyCompleter
from ems.qt4.gui.inputlistener.completer import CompleterListener
from ems.qt4.gui.widgets.itemview.itemview_editor import ItemViewEditor
from ems.xtype.base import StringType, NumberType, UnitType, BoolType #@UnresolvedImport
from ems.qt4.util import variant_to_pyobject
from ems.qt4.gui.mapper.base import BaseMapper #@UnresolvedImport
from ems.xtype.base import SequenceType, DictType #@UnresolvedImport

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
    
    def exportData(self):
        pprint.pprint(self.model.exportModelData())

class IndexListener(QObject):
    def onActivated(self, index):
        print "activated",index.row(), index.column()

app = QApplication(sys.argv)

dlg = QDialog()
dlg.setLayout(QHBoxLayout(dlg))
dlg.setWindowTitle("Completer Proxymodel")

dlg.view = QTableView(dlg)

dlg.sourceGroup = QGroupBox(dlg)
dlg.sourceGroup.setTitle("Source-Model")
dlg.sourceGroup.setLayout(QHBoxLayout())
dlg.layout().addWidget(dlg.sourceGroup)

dlg.proxyGroup = QGroupBox(dlg)
dlg.proxyGroup.setTitle("Proxy-Model")
dlg.proxyGroup.setLayout(QVBoxLayout())
dlg.layout().addWidget(dlg.proxyGroup)




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
dlg.sourceGroup.layout().addWidget(dlg.editor)

dlg.proxyView = QTableView(dlg)
dlg.proxyGroup.layout().addWidget(dlg.proxyView)

dlg.proxyModel = StringSummaryProxyModel(dlg)
dlg.proxyModel.setFormatString('{0} {1} ({3}kg)')

dlg.proxyModel.setFormatString('{0} {1}', Qt.EditRole)

dlg.proxyModel.setSourceModel(model)
dlg.proxyView.setModel(dlg.proxyModel)

dlg.input = QLineEdit(dlg)
dlg.proxyGroup.layout().addWidget(dlg.input)
dlg.completer = FuzzyCompleter(dlg.proxyModel, dlg)
dlg.completer.setFiltering(FuzzyCompleter.Contains)
#dlg.completer.setSourceModel(dlg.proxyModel)
dlg.completer.setCaseSensitivity(Qt.CaseInsensitive)
dlg.input.setCompleter(dlg.completer)

dlg.comboBox = QComboBox(dlg)
dlg.proxyGroup.layout().addWidget(dlg.input)
dlg.proxyGroup.layout().addWidget(dlg.comboBox)

dlg.indexListener = IndexListener(dlg)
dlg.completerListener = CompleterListener(dlg.completer)
dlg.completerListener.activated.connect(dlg.indexListener.onActivated)

#dlg.comboListener = CompleterListener(dlg.completer)
#dlg.comboListener.activated.connect(dlg.indexListener.onActivated)
dlg.comboBox.setEditable(True)
dlg.comboBox.setCompleter(QCompleter(dlg.proxyModel, dlg))


dlg.mapper = BaseMapper(model)
dlg.delegate = dlg.mapper.getDelegateForItemView(dlg.view)
dlg.view.setItemDelegate(dlg.delegate)

sys.exit(dlg.exec_())