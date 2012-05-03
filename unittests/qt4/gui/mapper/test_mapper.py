#coding=utf-8
'''
Created on 04.03.2012

@author: michi
'''
import sys
import copy

from PyQt4.QtCore import QString, QObject, QVariant
from PyQt4.QtGui import QTableView, QApplication, QDialog, QVBoxLayout, \
    QPushButton, QWidget, QFormLayout, QLineEdit, QLabel, QSpinBox, \
    QDoubleSpinBox, QDateEdit, QComboBox, QCheckBox
    

from ems.qt4.itemmodel.listofdictsmodel import ListOfDictsModel #@UnresolvedImport
from ems.qt4.gui.widgets.itemview.itemview_editor import ItemViewEditor
from ems.xtype.base import StringType, NumberType, UnitType, BoolType #@UnresolvedImport
from ems.xtype.base import DictType, SequenceType #@UnresolvedImport
from ems.qt4.gui.mapper.base import BaseMapper, MapperDefaults #@UnresolvedImport
import datetime

from ems.qt4.gui.mapper.strategies.string_strategy import StringStrategy #@UnresolvedImport
from ems.qt4.gui.mapper.strategies.bool_strategy import BoolStrategy #@UnresolvedImport
from ems.qt4.gui.mapper.strategies.number_strategy import NumberStrategy #@UnresolvedImport
from ems.xtype.base import DateType #@UnresolvedImport
from ems.qt4.gui.mapper.strategies.date_strategy import DateStrategy #@UnresolvedImport
from pprint import pprint

testData = [{'vorname':'Leo','nachname':'Tils','alter':1,'gewicht':8.9,'einkommen':850.0,'verheiratet':False},
            {'vorname':'Kristina','nachname':'Bentz','alter':31,'gewicht':68.9,'einkommen':1450.0,'verheiratet':False},
            {'vorname':'Fabian','nachname':'Tils','alter':29,'gewicht':72.9,'einkommen':2850.0,'verheiratet':False},
            {'vorname':'Sonja','nachname':'Bentz','alter':28,'gewicht':65.9,'einkommen':450.0,'verheiratet':True},
            {'vorname':'Patrick','nachname':'Arnold','alter':29,'gewicht':79.6,'einkommen':3850.0,'verheiratet':False}]


mapperDefaults = MapperDefaults.getInstance()
mapperDefaults.addStrategy(StringStrategy())
boolStrategy = BoolStrategy()
boolStrategy.valueNames = {True:QString.fromUtf8('Wahr'),
                           False:QString.fromUtf8('Falsch'),
                           None: QString.fromUtf8('Keine Angabe')}
mapperDefaults.addStrategy(boolStrategy)
mapperDefaults.addStrategy(NumberStrategy())
mapperDefaults.addStrategy(DateStrategy())

class Importer(QObject):
    def __init__(self, model, parent):
        QObject.__init__(self, parent)
        self.model = model
        self.lastCurrentRow = None
    
    def importData(self):
        self.model.setModelData(copy.copy(testData))
        self.model.setStandardRow(1)
    
    def printExportedData(self):
        pprint(self.model.exportModelData())
    
    def onSelectionChanged(self, curIndex, prevIndex):
        if curIndex.row() != self.lastCurrentRow:
            self.mapper.dataWidgetMapper.setCurrentIndex(curIndex.row())
            self.lastCurrentRow = curIndex.row()
        
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

birthdayType = DateType()
birthdayType.minDate = datetime.date(1900,1,1)
birthdayType.maxDate = datetime.date.today()

registriertType = BoolType()

personType = DictType()


personType.addKey('vorname', namenType)
personType.addKey('nachname', namenType)
personType.addKey('alter', alterType)
personType.addKey('gewicht', gewichtType)
personType.addKey('einkommen', geldType)
personType.addKey('verheiratet', verheiratetType)
personType.addKey('geburtstag', birthdayType)
personType.addKey('registriert', registriertType)

personenType = SequenceType(personType)

model = ListOfDictsModel(personenType, dlg.view)


model.setKeyLabel('vorname', QString.fromUtf8('Name'))
model.setKeyLabel('nachname', QString.fromUtf8('Familienname'))
model.setKeyLabel('alter', QString.fromUtf8('Alter'))
model.setKeyLabel('gewicht', QString.fromUtf8('Gewicht'))
model.setKeyLabel('einkommen', QString.fromUtf8('Einkommen'))
model.setKeyLabel('verheiratet', label=QString.fromUtf8('Verheiratet'))
model.setKeyLabel('geburtstag', label=QString.fromUtf8('Geburtstag'))
model.setKeyLabel('registriert', label=QString.fromUtf8('Registriert'))

form = QDialog(dlg)
form.l = QFormLayout(form) 
form.setLayout(form.l)

form.vornameLabel = QLabel(model.getKeyLabel('vorname'),form)
form.vornameInput = QLineEdit(form)
form.l.addRow(form.vornameLabel, form.vornameInput)

form.nachnameLabel = QLabel(model.getKeyLabel('nachname'), form)
form.nachnameInput = QLineEdit(form)
form.l.addRow(form.nachnameLabel, form.nachnameInput)

form.alterLabel = QLabel(model.getKeyLabel('alter'), form)
form.alterInput = QSpinBox(form)
form.l.addRow(form.alterLabel, form.alterInput)

form.gewichtLabel = QLabel(model.getKeyLabel('gewicht'), form)
form.gewichtInput = QDoubleSpinBox(form)
form.l.addRow(form.gewichtLabel, form.gewichtInput)

form.einkommenLabel = QLabel(model.getKeyLabel('einkommen'), form)
form.einkommenInput = QDoubleSpinBox(form)
form.l.addRow(form.einkommenLabel, form.einkommenInput)

form.verheiratetLabel = QLabel(model.getKeyLabel('verheiratet'), form)
form.verheiratetInput = QComboBox(form)
form.verheiratetInput.setProperty('name', QVariant('formCombo'))
form.l.addRow(form.verheiratetLabel, form.verheiratetInput)

form.geburtstagLabel = QLabel(model.getKeyLabel('geburtstag'), form)
form.geburtstagInput = QDateEdit(form)
form.l.addRow(form.geburtstagLabel, form.geburtstagInput)

form.registriertLabel = QLabel(model.getKeyLabel('registriert'), form)
form.registriertInput = QCheckBox(form)
form.l.addRow(form.registriertLabel, form.registriertInput)

form.show()




model.addRow({'vorname':'Leo','nachname':'Tils','alter':1,'gewicht':8.9,'einkommen':850.0,'verheiratet':True})
model.addRow(vorname='Fabian',nachname='Tils',alter=29,gewicht=67.2,einkommen=2600.0,verheiratet=False)

dlg.editor = ItemViewEditor(dlg.view, parent=dlg)
dlg.view.setModel(model)
dlg.view.setMinimumSize(640, 480)
dlg.layout().addWidget(dlg.editor)

'''##########################################################################
 FROM HERE
#############################################################################'''

mapper = BaseMapper(model, dlg)


'''##########################################################################'''

dlg.view.setItemDelegate(mapper.getDelegateForItemView())

mapper.addMapping(form.vornameInput, 'vorname')
mapper.addMapping(form.nachnameInput, 'nachname')
mapper.addMapping(form.alterInput, 'alter')
mapper.addMapping(form.gewichtInput, 'gewicht')
mapper.addMapping(form.einkommenInput, 'einkommen')
mapper.addMapping(form.verheiratetInput, 'verheiratet')
mapper.addMapping(form.geburtstagInput,'geburtstag')
mapper.addMapping(form.registriertInput,'registriert')



#mapper.dataWidgetMapper.setCurrentIndex(0)

#dlg.view.setItemDelegate(XTypeMapDelegate(dlg.view))
#dlg.view.itemDelegate().setXTypeMap(dlg.view.model().xTypeMap())

dlg.exportButton = QPushButton("Export", dlg)
dlg.layout().addWidget(dlg.exportButton)


dlg.importer = Importer(model, dlg)
dlg.importer.mapper = mapper
dlg.importButton = QPushButton("Import", dlg)
dlg.layout().addWidget(dlg.importButton)
dlg.importButton.clicked.connect(dlg.importer.importData)
dlg.exportButton.clicked.connect(dlg.importer.printExportedData)

dlg.view.selectionModel().currentChanged.connect(dlg.importer.onSelectionChanged)

sys.exit(dlg.exec_())