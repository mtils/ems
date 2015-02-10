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
from ems.qt4.gui.itemdelegate.xtypedelegate import XTypeDelegate #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.unittype import UnitTypeDelegate #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypemapdelegate import XTypeMapDelegate #@UnresolvedImport
from ems.xtype.base import DictType, SequenceType #@UnresolvedImport
from ems.qt4.gui.mapper.base import BaseMapper, MapperDefaults #@UnresolvedImport
from ems.xtype.base import native2XType #@UnresolvedImport
import datetime

from ems.qt4.gui.mapper.strategies.string_strategy import StringStrategy #@UnresolvedImport
from ems.qt4.gui.mapper.strategies.bool_strategy import BoolStrategy #@UnresolvedImport
from ems.qt4.gui.mapper.strategies.number_strategy import NumberStrategy #@UnresolvedImport
from ems.xtype.base import DateType #@UnresolvedImport
from ems.qt4.gui.mapper.strategies.date_strategy import DateStrategy #@UnresolvedImport
from ems.qt4.gui.mapper.strategies.listofdicts_strategy import ListOfDictsStrategy #@UnresolvedImport
from pprint import pprint

testData = [{'vorname':'Leo','alter':1,'registriert':False},
            {'vorname':'Kristina','alter':31,'registriert':True},
            {'vorname':'Fabian','alter':29,'registriert':False},
            {'vorname':'Sonja','alter':28,'registriert':True},
            {'vorname':'Patrick','alter':29,'registriert':False}]


mapperDefaults = MapperDefaults.getInstance()
mapperDefaults.addStrategy(StringStrategy())
boolStrategy = BoolStrategy()
boolStrategy.valueNames = {True:QString.fromUtf8('Wahr'),
                           False:QString.fromUtf8('Falsch'),
                           None: QString.fromUtf8('Keine Angabe')}
mapperDefaults.addStrategy(boolStrategy)
mapperDefaults.addStrategy(NumberStrategy())
mapperDefaults.addStrategy(DateStrategy())
mapperDefaults.addStrategy(ListOfDictsStrategy())

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

registriertType = BoolType()

stationDatumType = DateType()
stationDatumType.minDate = datetime.date(1900,01,01)
stationDatumType.maxDate = datetime.date.today()

stationTextType = StringType()
stationTextType.maxLength = 64

stationType = DictType()
stationType.addKey('datum',stationDatumType)
stationType.addKey('text',stationTextType)
stationenType = SequenceType(stationType)
#stationenType.defaultLength = 3
stationenType.defaultValue = [{'datum':datetime.date(2011,03,05),'text':'Geburt'},
                              {'datum':datetime.date(2012,02,14),'text':'Laufen'},
                              {'datum':datetime.date.today(),'text':'Fabians Geburtstag'}]
personType = DictType()
personType.addKey('vorname', namenType)
personType.addKey('alter', alterType)
personType.addKey('registriert', registriertType)
personType.addKey('stationen', stationenType)

personenType = SequenceType(personType)

model = ListOfDictsModel(personenType, dlg.view)


model.setKeyLabel('vorname', QString.fromUtf8('Name'))
model.setKeyLabel('alter', QString.fromUtf8('Alter'))
model.setKeyLabel('registriert', label=QString.fromUtf8('Registriert'))
model.setKeyLabel('stationen', label=QString.fromUtf8('Stationen'))
model.setKeyLabel('stationen.datum', label=QString.fromUtf8('Datum'))
model.setKeyLabel('stationen.text', label=QString.fromUtf8('Ergeignis'))

form = QDialog(dlg)
form.l = QFormLayout(form) 
form.setLayout(form.l)

form.vornameLabel = QLabel(model.getKeyLabel('vorname'),form)
form.vornameInput = QLineEdit(form)
form.l.addRow(form.vornameLabel, form.vornameInput)

form.alterLabel = QLabel(model.getKeyLabel('alter'), form)
form.alterInput = QSpinBox(form)
form.l.addRow(form.alterLabel, form.alterInput)

form.registriertLabel = QLabel(model.getKeyLabel('registriert'), form)
form.registriertInput = QCheckBox(form)
form.l.addRow(form.registriertLabel, form.registriertInput)

form.stationenLabel = QLabel('Stationen', form)
form.stationenInput = QTableView(form)
form.l.addRow(form.stationenLabel, form.stationenInput)

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
dlg.view.horizontalHeader().setResizeMode(dlg.view.horizontalHeader().ResizeToContents)
dlg.view.verticalHeader().setResizeMode(dlg.view.verticalHeader().ResizeToContents)

mapper.addMapping(form.vornameInput, 'vorname')
mapper.addMapping(form.alterInput, 'alter')
mapper.addMapping(form.registriertInput,'registriert')
mapper.addMapping(form.stationenInput, 'stationen')



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