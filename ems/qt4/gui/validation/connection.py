'''
Created on 10.08.2011

@author: michi
'''
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, SIGNAL, SLOT, QString,\
    Qt, QDate, QTime, QDateTime, QVariant
from PyQt4.QtGui import QValidator, QDoubleSpinBox, QAbstractButton

from ems.qt4.util import variant_to_pyobject
from ems.qt4.gui.inputlistener.standard import *

class ValidatorConnection(QObject):
    
    isValidStateChanged = pyqtSignal(bool)
    
    ISNULL_PROPERTY = 'isEmpty'
    ISDIRTY_PROPERTY = 'isDirty'
    
    def __init__(self, validator, widget, mandatory=False, inputListener=None,
                 changeListener=None):
        QObject.__init__(self, widget)
        self.__changeListener = changeListener
        self.widget = widget
        self.validator = validator
        
        if self.__changeListener is not None:
            self.__changeListener.widgetValidator = self
        
        if inputListener is None:
            inputListener = self._loadInputListener()
        self.inputListener = inputListener
        
        self.mandatory = mandatory
        self.__validationState = None
        
        self.validator.validationStateChanged.connect(self._onValidationStateChanged)
    
    
    def _loadInputListener(self):
        raise NotImplementedError()
    
    def getChangeListener(self):
        return self.__changeListener
    
    def setChangeListener(self, changeListener):
        self.__changeListener = changeListener
    
    changeListener = property(getChangeListener, setChangeListener)
    
    @property
    def validationState(self):
        return self.__validationState
    
    def _onAcceptable(self):
        pass
    
    def _onIntermediate(self):
        pass
    
    def _onInvalid(self):
        pass
    
    @pyqtSlot(int)
    def _onValidationStateChanged(self, state):
        if state == QValidator.Acceptable:
            boolState = True
        else:
            boolState = False
        if self.__validationState != boolState:
            self.isValidStateChanged.emit(boolState)
            self.__validationState = boolState
            
        if state == QValidator.Acceptable:
            self._onAcceptable()
            if hasattr(self.__changeListener,'onAcceptable'):
                self.__changeListener.onAcceptable()
            else:
                pass
        elif state == QValidator.Intermediate:
            self._onIntermediate()
            if hasattr(self.__changeListener,'onIntermediate'):
                self.__changeListener.onIntermediate()
        elif state == QValidator.Invalid:
            self._onInvalid()
            if hasattr(self.__changeListener,'onInvalid'):
                self.__changeListener.onInvalid()
        else:
            raise TypeError("Unknown ValidationState %s" % state)
    
class LineEditConnection(ValidatorConnection):
    def __init__(self, *args, **kwargs):
        ValidatorConnection.__init__(self, *args, **kwargs)
        self.widget.setValidator(self.validator)
    
    def _loadInputListener(self):
        return LineEditListener(self.widget)

class AbstractSpinBoxConnection(ValidatorConnection):
    
    emptyValueText = u'Nichts'
    
    def __init__(self, validator, widget, mandatory=False, inputListener=None,
                  changeListener=None, emptyValue=None):
        ValidatorConnection.__init__(self, validator, widget, mandatory,
                                     inputListener,changeListener)
        
        self._emptyValue = emptyValue
        #widget.valueChanged.connect(self.onValueChanged)
        widget.setMinimum(self.emptyValue)
        widget.setMaximum(validator.maximum)
        
        if isinstance(widget, QDoubleSpinBox):
            widget.setDecimals(validator.decimals)
        
        #if self.validator.notEmpty:
        self.widget.setSpecialValueText(self.trUtf8(self.emptyValueText))
        
        self.widget.valueChanged.connect(self.onValueChanged)
        
    
    def _loadInputListener(self):
        return SpinBoxListener(self.widget)
    
    def getEmptyValue(self):
        if self._emptyValue is not None:
            return self._emptyValue
        if isinstance(self.widget, QDoubleSpinBox):
            return self.validator.minimum - 0.1
        return self.validator.minimum - 1
    
    def setEmptyValue(self, val):
        self._emptyValue = val
    
    def delEmptyValue(self):
        self._emptyValue = None
    
    emptyValue = property(getEmptyValue, setEmptyValue, delEmptyValue)
    
    def onValueChanged(self, value):
        if value < self.validator.minimum:
            self.widget.setProperty(self.ISNULL_PROPERTY,QVariant(True))
            self.validator.validate(QString(""), 0, self.widget)
        else:
            cleanText = self.widget.cleanText()
            self.widget.setProperty(self.ISNULL_PROPERTY,QVariant(False))
            self.validator.validate(cleanText, (len(cleanText)-1), self.widget)
            #print cleanText, type(cleanText), (len(cleanText)-1)
            
class ComboBoxConnection(ValidatorConnection):
    def __init__(self, *args, **kwargs):
        ValidatorConnection.__init__(self, *args, **kwargs)
        self.widget.currentIndexChanged.connect(self.onCurrentIndexChanged)
    
    def _loadInputListener(self):
        return ComboBoxListener(self.widget)
    
    def onCurrentIndexChanged(self, index):
        itemData = variant_to_pyobject(self.widget.itemData(index, Qt.UserRole))
        if itemData is None:
            self.widget.setProperty(self.ISNULL_PROPERTY,QVariant(True))
        else:
            self.widget.setProperty(self.ISNULL_PROPERTY,QVariant(False))
        self.validator.validate(itemData, qObject=self.widget)
        #print "ComboBoxCon: {0} {1}".format(index, itemData)

class ButtonGroupConnection(ValidatorConnection):
    def __init__(self, validator, widget, mandatory=False, inputListener=None,
                 changeListener=None, dataProperty='data'):
        ValidatorConnection.__init__(self, validator, widget, mandatory,
                                     inputListener,changeListener)
        self.dataProperty = dataProperty
        noDataPropertyCount = 0
        
        for button in widget.buttons():
            propertyNames = []
            for qtName in button.dynamicPropertyNames():
                propertyNames.append(str(qtName))
                
            if not self.dataProperty in propertyNames:
                noDataPropertyCount += 1
        if noDataPropertyCount > 1:
            raise ValueError("I need a {0} property on every button minus " +
                             "the 'no-selection' Button".format(dataProperty))
        self.widget.buttonClicked.connect(self.onButtonClicked)
        
#        self.connect(self.widget, SIGNAL("buttonClicked(QAbstractButton)"),
#                     self.onButtonClicked)#, SLOT('onButtonClicked(QAbstractButton)'))
        
        #self.validator.validationStateChanged.connect(self._onValidationStateChanged)
        
    def _loadInputListener(self):
        return ButtonGroupListener(self.widget)
    
    @pyqtSlot("QAbstractButton")
    def onButtonClicked(self, button):
        nonChecked = True
        for anyButton in self.widget.buttons():
            if anyButton.isChecked():
                nonChecked = False
        
        
        validateVal = variant_to_pyobject(button.property(self.dataProperty))
        
        if validateVal is None:
            self.widget.setProperty(self.ISNULL_PROPERTY, QVariant(True))
        else:
            self.widget.setProperty(self.ISNULL_PROPERTY, QVariant(nonChecked))
            
        self.validator.validate(validateVal, qObject=self.widget)
        
class DateTimeEditConnection(ValidatorConnection):
    def __init__(self, validator, widget, mandatory=False, inputListener=None,
                  changeListener=None, emptyDateTime = -1):
        super(DateTimeEditConnection, self).__init__(validator, widget,
                                                     mandatory,
                                                     inputListener,
                                                     changeListener)
        
        if isinstance(emptyDateTime, QDateTime):
            self.emptyDateTime = emptyDateTime
        elif isinstance(emptyDateTime, int):
            self.emptyDateTime = self.validator.minDateTime.addDays(emptyDateTime)
        
        #self.validator.minDate = self.emptyDateTime
        #print self.emptyDateTime
#        print self.emptyDateTime
        self.widget.setMinimumDateTime(self.emptyDateTime)
        self.widget.setMaximumDateTime(self.validator.maxDateTime)
        self.widget.dateTimeChanged.connect(self.onDateTimeChanged)
    
    def _loadInputListener(self):
        return DateTimeListener(self.widget)
    
    def onDateTimeChanged(self, dateTime):
        if dateTime < self.validator.minDateTime:
            self.widget.setProperty(self.ISNULL_PROPERTY, True)
        else:
            self.widget.setProperty(self.ISNULL_PROPERTY, False)
            
        self.validator.validate(dateTime, qObject=self.widget)
        #print dateTime
        #self.validator.validate(dateTime)

class DateEditConnection(ValidatorConnection):
    def __init__(self, validator, widget, mandatory=False, inputListener=None,
                  changeListener=None, emptyDate = -1):
        super(DateEditConnection, self).__init__(validator, widget, mandatory,
                                                 inputListener, changeListener)
        
        if isinstance(emptyDate, QDate):
            self.emptyDate = emptyDate
        elif isinstance(emptyDate, int):
            self.emptyDate = self.validator.minDate.addDays(emptyDate)
        
        #self.validator.minDate = self.emptyDateTime
        #print self.emptyDateTime
#        print self.emptyDateTime
        self.widget.setMinimumDate(self.emptyDate)
        self.widget.setMaximumDate(self.validator.maxDate)
        self.widget.dateChanged.connect(self.onDateChanged)
    
    def _loadInputListener(self):
        return DateTimeListener(self.widget)
    
    def onDateChanged(self, date):
        if date < self.validator.minDate:
            self.widget.setProperty(self.ISNULL_PROPERTY, True)
        else:
            self.widget.setProperty(self.ISNULL_PROPERTY, False)
            
        self.validator.validate(date, qObject=self.widget)
        #print dateTime
        #self.validator.validate(dateTime)

class TimeEditConnection(ValidatorConnection):
    def __init__(self, validator, widget, mandatory=False, inputListener=None, 
                 changeListener=None, emptyTime = -1):
        super(TimeEditConnection, self).__init__(validator, widget, mandatory,
                                                 inputListener, changeListener)
        
        if isinstance(emptyTime, QTime):
            self.emptyTime = emptyTime
        elif isinstance(emptyTime, int):
            self.emptyTime = self.validator.minTime.addSecs(emptyTime)

        self.widget.setMinimumTime(self.emptyTime)
        self.widget.setMaximumTime(self.validator.maxTime)
        self.widget.timeChanged.connect(self.onTimeChanged)

    def _loadInputListener(self):
        return DateTimeListener(self.widget)
    
    def onTimeChanged(self, time):
        #print time
        if time < self.validator.minTime:
            self.widget.setProperty(self.ISNULL_PROPERTY, True)
        else:
            self.widget.setProperty(self.ISNULL_PROPERTY, False)
            
        self.validator.validate(time, qObject=self.widget)
        #print dateTime

class CheckBoxConnection(ValidatorConnection):
    def __init__(self, validator, widget, mandatory=False, inputListener=None,
                  changeListener=None):
        ValidatorConnection.__init__(self, validator, widget, mandatory,
                                     inputListener, changeListener)
        if not self.validator.notEmpty:
            self.widget.setTristate(True)
        self.widget.stateChanged.connect(self.onStateChanged)
    
    def _loadInputListener(self):
        return CheckBoxListener(self.widget)
    
    def onStateChanged(self, state):
        if state == Qt.PartiallyChecked:
            self.widget.setProperty(self.ISNULL_PROPERTY, True)
            boolState = None 
        else:
            self.widget.setProperty(self.ISNULL_PROPERTY, False)
            boolState = self.widget.isChecked()
        self.validator.validate(boolState,qObject=self.widget)