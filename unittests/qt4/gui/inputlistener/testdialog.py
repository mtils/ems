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
    QCheckBox, QHBoxLayout, QGridLayout
    
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
    SpinBoxListener, ComboBoxListener, ButtonGroupListener, DateTimeListener,\
    CheckBoxListener



utf8 = QString.fromUtf8

class ListenerDisplayRow(QWidget):
    def __init__(self, listener, parent=None):
        super(ListenerDisplayRow, self).__init__(parent)
        self.listener = listener
        self.setLayout(QHBoxLayout(self))
        
        self.focusButton = self._getButton('F', 'hasFocus')
        self.listener.hasFocusStateChanged.connect(self.focusButton.setChecked)
        self.layout().addWidget(self.focusButton)
        
        self.hadFocusButton = self._getButton('HF', 'hadFocus')
        self.listener.hadFocusStateChanged.connect(self.hadFocusButton.setChecked)
        self.layout().addWidget(self.hadFocusButton)
        
        self.hasBeenEditedButton = self._getButton('E', 'hasBeenEdited')
        self.listener.hasBeenEditedStateChanged.connect(self.hasBeenEditedButton.setChecked)
        self.layout().addWidget(self.hasBeenEditedButton)
        
        self.dirtyButton = self._getButton('D', 'dirty')
        self.listener.dirtyStateChanged.connect(self.dirtyButton.setChecked)
        self.layout().addWidget(self.dirtyButton)
        
        
    def _getButton(self, text, tooltip):
        button = QPushButton(text, self)
        button.setToolTip(tooltip)
        button.setCheckable(True)
        button.setFocusPolicy(Qt.NoFocus)
        
        return button
        

    
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
        self.listeners = []
        self.setupUi()
        self.addLastRow()
        #self.setupManualValidators()
        self.setStyleSheet(styleSheet)
        
    
    def addLastRow(self):
        self.resetButton = QPushButton("Reset", self)
        self.layout().addWidget(self.resetButton,self.layout().rowCount(),
                                0,1,3)
        
        self.resetButton.clicked.connect(self.resetListeners)
    
    def resetListeners(self):
        for listener in self.listeners:
            listener.reset()
    
    def setupUi(self):
        self.setMinimumWidth(300)
        self.setMinimumHeight(200)
        
        self.setLayout(QGridLayout(self))
        
        self.qmLabel = QLabel(utf8("Fläche"), self)
        self.qmInput = QSpinBox(self)
        self.qmListener = SpinBoxListener(self.qmInput)
        self.listeners.append(self.qmListener)
        self.qmInput.setSuffix(utf8(" m²"))
        self.qmInput.setObjectName(utf8("Fläche"))
        
        self.alignment = Qt.AlignLeft | Qt.AlignVCenter
        self.layout().addWidget(self.qmLabel,0,0,self.alignment)
        self.layout().addWidget(self.qmInput,0,1,self.alignment)
        self.layout().addWidget(ListenerDisplayRow(self.qmListener),0,2,
                                self.alignment)
        
        
        self.euroLabel = QLabel(utf8("Geld"), self)
        self.euroInput = QDoubleSpinBox(self)
        self.euroInput.setSuffix(utf8(" €"))
        self.euroInput.setObjectName(utf8('Geld'))
        self.euroListener = SpinBoxListener(self.euroInput)
        self.listeners.append(self.euroListener)
        
        
        self.layout().addWidget(self.euroLabel,1,0,self.alignment)
        self.layout().addWidget(self.euroInput,1,1,self.alignment)
        self.layout().addWidget(ListenerDisplayRow(self.euroListener),1,2,
                                self.alignment)
        
        self.nameLabel = QLabel(utf8("Name"))
        self.nameInput = QLineEdit(self)
        self.nameInput.setObjectName(utf8("Name"))
        self.nameListener = LineEditListener(self.nameInput)
        self.listeners.append(self.nameListener)
        
        self.layout().addWidget(self.nameLabel,2, 0,self.alignment)
        self.layout().addWidget(self.nameInput,2, 1,self.alignment)
        self.layout().addWidget(ListenerDisplayRow(self.nameListener),2,2,
                                self.alignment)
        
        self.anredeLabel = QLabel(utf8("Anrede"), self)
        self.anredeInput = QComboBox(self)
        self.anredeInput.setObjectName("Anrede")
        self.anredeInput.addItem('Auswahl...', userData=QVariant(None))
        for anrede in ('Herr', 'Frau', 'Neutrum', 'Neutron','Aus neu mach alt'):
            self.anredeInput.addItem(utf8(anrede), QVariant(anrede))
        
        self.anredeListener = ComboBoxListener(self.anredeInput)
        self.listeners.append(self.anredeListener)
        
        self.layout().addWidget(self.anredeLabel, 3, 0,self.alignment)
        self.layout().addWidget(self.anredeInput, 3, 1,self.alignment)
        self.layout().addWidget(ListenerDisplayRow(self.anredeListener),3,2,
                                self.alignment)
        
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
        self.listeners.append(self.eingangPerListener)
        
        button = QRadioButton('Sonstiges',r)
        layout.addWidget(button)
        self.radioButtonGroup.addButton(button)
        self.radioButtonGroup.setObjectName("Eingang per")
        #button.setProperty('data', QVariant(eingangPer))
        
        self.eingangPerLabel = QLabel("Eingang per", self)
        
        self.layout().addWidget(self.eingangPerLabel,4,0,self.alignment)
        self.layout().addWidget(self.radioButtonContainer,4,1,self.alignment)
        self.layout().addWidget(ListenerDisplayRow(self.eingangPerListener),4,2,
                                self.alignment)
        
        self.datetimeInput = QDateTimeEdit(self)
        self.datetimeInput.setCalendarPopup(True)
        self.datetimeLabel = QLabel('Datum/Zeit', self)
        self.datetimeInput.setObjectName("Datum/Zeit")
        self.datetimeListener = DateTimeListener(self.datetimeInput)
        self.listeners.append(self.datetimeListener)
        
        self.layout().addWidget(self.datetimeLabel,5,0,self.alignment)
        self.layout().addWidget(self.datetimeInput,5,1,self.alignment)
        self.layout().addWidget(ListenerDisplayRow(self.datetimeListener),5,2,
                                self.alignment)
        
        self.dateInput = QDateEdit(self)
        self.dateInput.setCalendarPopup(True)
        self.dateInput.setObjectName("Datum")
        self.dateLabel = QLabel('Datum', self)
        
        self.dateListener = DateTimeListener(self.dateInput)
        self.listeners.append(self.dateListener)
        
        self.layout().addWidget(self.dateLabel,6,0,self.alignment)
        self.layout().addWidget(self.dateInput,6,1,self.alignment)
        self.layout().addWidget(ListenerDisplayRow(self.dateListener),6,2,
                                self.alignment)
        
        
        self.timeInput = QTimeEdit(self)
        self.timeInput.setObjectName("Zeit")
#        self.timeInput.setCalendarPopup(True)
        self.timeLabel = QLabel('Zeit', self)
        self.timeListener = DateTimeListener(self.timeInput)
        self.listeners.append(self.timeListener)
        
        self.layout().addWidget(self.timeLabel,7,0,self.alignment)
        self.layout().addWidget(self.timeInput,7,1,self.alignment)
        self.layout().addWidget(ListenerDisplayRow(self.timeListener),7,2,
                                self.alignment)
        
        self.checkedInput = QCheckBox(self)
        self.checkedInput.setTristate(True)
        self.checkedLabel = QLabel(utf8("Geprüft"), self)
        self.checkedInput.setObjectName(utf8("Geprüft"))
        self.checkedListener = CheckBoxListener(self.checkedInput)
        self.listeners.append(self.checkedListener)
        
        self.layout().addWidget(self.checkedLabel,8,0,self.alignment)
        self.layout().addWidget(self.checkedInput,8,1,self.alignment)
        self.layout().addWidget(ListenerDisplayRow(self.checkedListener),8,2,
                                self.alignment)
        
    def pasteBadThings(self):
        self.nameInput.setText("dasdlkj89")
        self.qmInput.setValue(-11)
        self.euroInput.setValue(1.51)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = TestWindow()
    dlg.show()
    sys.exit(app.exec_())