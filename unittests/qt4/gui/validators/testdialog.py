#coding=utf-8
'''
Created on 13.08.2011

@author: michi
'''
import sys

from PyQt4.QtCore import SIGNAL, SLOT, pyqtSlot, QVariant, QString, QRegExp,\
    pyqtSignal, QObject, Qt, QPoint, QEvent, QDateTime, QDate, QTime

from PyQt4.QtGui import QWidget, QLabel, QLineEdit, QTextEdit, QComboBox, \
    QApplication, QFormLayout, QDataWidgetMapper, QPushButton, QItemDelegate,\
    QSpinBox, QDoubleSpinBox, QRegExpValidator, QValidator, QButtonGroup,\
    QVBoxLayout, QRadioButton, QDateTimeEdit, QDateEdit, QTimeEdit,\
    QCheckBox
    
from ems.qt4.gui.widgets.dialogable import DialogableWidget #@UnresolvedImport
from ems.qt4.validators.base import RegExpValidator, IntValidator, FloatValidator, IsInstanceValidator #@UnresolvedImport
from ems.qt4.gui.validation.connection import LineEditConnection, AbstractSpinBoxConnection, ComboBoxConnection #@UnresolvedImport
from ems.qt4.gui.validation.visualizer.standardwidgets import \
    LineEditValidationVisualizer, SpinBoxValidationVisualizer  #@UnresolvedImport
from ems.qt4.gui.validation.visualizer.base import ValidationVisualizer,\
    ButtonGroupVisualizer
from ems.qt4.validators.base import IsInValidator
from ems.qt4.gui.validation.connection import ButtonGroupConnection
from ems.qt4.validators.base import DateTimeValidator, DateValidator,\
    TimeValidator, BoolValidator
from ems.qt4.gui.validation.connection import DateTimeEditConnection,\
    DateEditConnection, TimeEditConnection, CheckBoxConnection
from ems.qt4.gui.inputlistener.standard import LineEditListener,\
    SpinBoxListener, ComboBoxListener, ButtonGroupListener, DateTimeListener



utf8 = QString.fromUtf8



class ValidationGroup(QObject):
    
    isValidStateChanged = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        QObject.__init__(parent)
    
styleSheet = """
QComboBox[validationState="Acceptable"]:focus { background: #bfffbf }
QComboBox[validationState="Intermediate"] { background: #ffffc0 }
QComboBox[validationState="Invalid"] { background: #e86F6B }
QSpinBox[isEmpty="true"] { color: #888}
QSpinBox[validationState="Acceptable"]:focus { background: #bfffbf }
QSpinBox[validationState="Intermediate"] { background: #ffffc0 }
QSpinBox[validationState="Invalid"] { background: #e86F6B }
QDoubleSpinBox[isEmpty="true"] { color: #888}
QDoubleSpinBox[validationState="Acceptable"]:focus { background: #bfffbf }
QDoubleSpinBox[validationState="Intermediate"] { background: #ffffc0 }
QDoubleSpinBox[validationState="Invalid"] { background: #e86F6B }
QLineEdit[validationState="Acceptable"]:focus { background: #bfffbf }
QLineEdit[validationState="Intermediate"] { background: #ffffc0 }
QLineEdit[validationState="Invalid"] { background: #e86F6B }
QLabel[validationState="Intermediate"] { font-style: italic }
QLabel[validationState="Invalid"] { font-style: italic }
QDateTimeEdit[isEmpty="true"] { color: #888}
QDateTimeEdit[validationState="Acceptable"]:focus { background: #bfffbf }
QDateTimeEdit[validationState="Intermediate"] { background: #ffffc0 }
QDateTimeEdit[validationState="Invalid"] { background: #e86F6B }
QDateEdit[isEmpty="true"] { color: #888}
QDateEdit[validationState="Acceptable"]:focus { background: #bfffbf }
QDateEdit[validationState="Intermediate"] { background: #ffffc0 }
QDateEdit[validationState="Invalid"] { background: #e86F6B }
QTimeEdit[isEmpty="true"] { color: #888}
QTimeEdit[validationState="Acceptable"]:focus { background: #bfffbf }
QTimeEdit[validationState="Intermediate"] { background: #ffffc0 }
QTimeEdit[validationState="Invalid"] { background: #e86F6B }

/* QRadioButton[validationState="Intermediate"] { color: #e86F6B } */
"""         
class TestWindow(DialogableWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi()
        self.setupManualValidators()
        self.setStyleSheet(styleSheet)
    
    def setupUi(self):
        self.setMinimumWidth(300)
        self.setMinimumHeight(200)
        
        self.setLayout(QFormLayout(self))
        
        self.qmLabel = QLabel(utf8("Fläche"), self)
        self.qmInput = QSpinBox(self)
        self.qmListener = SpinBoxListener(self.qmInput)
        self.qmInput.setSuffix(utf8(" m²"))
        self.qmInput.setObjectName(utf8("Fläche"))
        self.layout().addRow(self.qmLabel, self.qmInput)
        
        self.euroLabel = QLabel(utf8("Geld"), self)
        self.euroInput = QDoubleSpinBox(self)
        self.euroInput.setSuffix(utf8(" €"))
        self.euroInput.setObjectName(utf8('Geld'))
        self.euroListener = SpinBoxListener(self.euroInput)
        self.layout().addRow(self.euroLabel, self.euroInput)
        
        self.nameLabel = QLabel(utf8("Name"))
        self.nameInput = QLineEdit(self)
        self.nameInput.setObjectName(utf8("Name"))
        self.layout().addRow(self.nameLabel, self.nameInput)
        
        self.anredeLabel = QLabel(utf8("Anrede"), self)
        self.anredeInput = QComboBox(self)
        self.anredeInput.setObjectName("Anrede")
        self.anredeInput.addItem('Auswahl...', userData=QVariant(None))
        for anrede in ('Herr', 'Frau', 'Neutrum', 'Neutron','Aus neu mach alt'):
            self.anredeInput.addItem(utf8(anrede), QVariant(anrede))
        
        self.anredeListener = ComboBoxListener(self.anredeInput)
        self.layout().addRow(self.anredeLabel, self.anredeInput)
        
        self.radioButtonContainer = QWidget(self)
        self.radioButtonContainer.setLayout(QVBoxLayout())
#        self.radioButtonContainer.setObjectName("Eingang Per")
        r = self.radioButtonContainer
        self.radioButtonGroup = QButtonGroup(self)
        layout = self.radioButtonContainer.layout()
        trans = {'POST':'Post','EMAIL':'E-Mail','TELEFON':'Telefon',
                 'TELEFAX':'Fax'}
        
        for eingangPer in ('POST','EMAIL','TELEFON','TELEFAX'):
            button = QRadioButton(trans[eingangPer],r)
            layout.addWidget(button)
            self.radioButtonGroup.addButton(button)
            if eingangPer == 'EMAIL':
                button.setChecked(True)
            button.setProperty('data', QVariant(eingangPer))
        
        self.eingangPerListener = ButtonGroupListener(self.radioButtonGroup)
        button = QRadioButton('Sonstiges',r)
        layout.addWidget(button)
        self.radioButtonGroup.addButton(button)
        self.radioButtonGroup.setObjectName("Eingang per")
        #button.setProperty('data', QVariant(eingangPer))
        
        self.eingangPerLabel = QLabel("Eingang per", self)
        
        self.layout().addRow(self.eingangPerLabel, self.radioButtonContainer)
        
        self.datetimeInput = QDateTimeEdit(self)
        self.datetimeInput.setCalendarPopup(True)
        self.datetimeLabel = QLabel('Datum/Zeit', self)
        self.datetimeInput.setObjectName("Datum/Zeit")
        self.datetimeListener = DateTimeListener(self.datetimeInput)
        
        self.layout().addRow(self.datetimeLabel, self.datetimeInput)
        
        self.dateInput = QDateEdit(self)
        self.dateInput.setCalendarPopup(True)
        self.dateInput.setObjectName("Datum")
        self.dateLabel = QLabel('Datum', self)
        
        self.dateListener = DateTimeListener(self.dateInput)
        
        self.layout().addRow(self.dateLabel, self.dateInput)
        
        self.timeInput = QTimeEdit(self)
        self.timeInput.setObjectName("Zeit")
#        self.timeInput.setCalendarPopup(True)
        self.timeLabel = QLabel('Zeit', self)
        self.timeListener = DateTimeListener(self.timeInput)
        
        self.layout().addRow(self.timeLabel, self.timeInput)
        
        self.checkedInput = QCheckBox(self)
        self.checkedLabel = QLabel(utf8("Geprüft"), self)
        self.checkedInput.setObjectName(utf8("Geprüft"))
        self.layout().addRow(self.checkedLabel, self.checkedInput)
        
        
    
    def setupManualValidators(self):
        #self.qmInput.setV
        #self.nameInput.setValidator()
        v = RegExpValidator(QRegExp("[a-zA-Z]+"),
                                    notEmpty=False,
                                    minLength=1,
                                    maxLength=6,
                                    parent=self.nameInput)
        vv = ValidationVisualizer(v, self.nameInput,
                                  additionalWidgets=(self.nameLabel,))
        
        self.nameVal = LineEditConnection(v, self.nameInput, changeListener=vv)
        
        self.nameListener = LineEditListener(self.nameInput)
        v2 = IntValidator(-10,50, notEmpty=True)
        
        #v2 = IntValidator(notEmpty=True)
        vv2 = ValidationVisualizer(v2, self.qmInput, additionalWidgets=(self.qmLabel,))
        self.qmVal = AbstractSpinBoxConnection(v2, self.qmInput, changeListener=vv2)
        #self.pasteBadText()
        
        v3 = FloatValidator(0.30,1.50,2,notEmpty=True)
        
        vv3 = ValidationVisualizer(v3, self.euroInput, additionalWidgets=(self.euroLabel,))
        self.euroVal = AbstractSpinBoxConnection(v3, self.euroInput, changeListener=vv3)
        
        v4 = IsInstanceValidator(unicode, notEmpty=True)
        vv4 = ValidationVisualizer(v4, self.anredeInput, additionalWidgets=(self.anredeLabel,))
        self.anredeVal = ComboBoxConnection(v4, self.anredeInput, changeListener=vv4)
        
        v5 = IsInValidator(('POST','EMAIL','TELEFON','TELEFAX'), notEmpty=True)
        vv5 = ButtonGroupVisualizer(v5, self.radioButtonGroup, additionalWidgets=(self.eingangPerLabel,))
        self.radioVal = ButtonGroupConnection(v5, self.radioButtonGroup, changeListener=vv5) 
        
        
        v6 = DateTimeValidator(QDateTime(QDate(1976,05,31),QTime(0,0)),notEmpty=True)
        vv6 = ValidationVisualizer(v6, self.datetimeInput, additionalWidgets=(self.datetimeLabel))
        self.datetimeVal = DateTimeEditConnection(v6, self.datetimeInput, changeListener=vv6)
        
        v7 = DateValidator(QDate(1976,05,31))
        vv7 = ValidationVisualizer(v7, self.dateInput, additionalWidgets=self.dateLabel)
        self.dateVal = DateEditConnection(v7, self.dateInput, changeListener=vv7)
        
        v8 = TimeValidator(QTime(14, 00), QTime(19, 00, 59), notEmpty=False)
        vv8 = ValidationVisualizer(v8, self.timeInput, additionalWidgets=self.timeLabel)
        self.dateVal = TimeEditConnection(v8, self.timeInput, changeListener=vv8)
        
        v9 = BoolValidator(notEmpty=False)
        vv9 = ValidationVisualizer(v9, self.checkedInput, additionalWidgets=self.checkedLabel)
        self.checkedVal = CheckBoxConnection(v9, self.checkedInput, changeListener=vv9)
        
#        self.pasteBadThings()
        
    def pasteBadThings(self):
        self.nameInput.setText("dasdlkj89")
        self.qmInput.setValue(-11)
        self.euroInput.setValue(1.51)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = TestWindow()
    dlg.show()
    sys.exit(app.exec_())