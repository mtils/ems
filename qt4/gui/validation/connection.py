'''
Created on 10.08.2011

@author: michi
'''
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, SIGNAL, SLOT, QString,\
    Qt
from PyQt4.QtGui import QValidator, QDoubleSpinBox
from lib.ems.qt4.util import variant_to_pyobject

class ValidatorConnection(QObject):
    
    isValidStateChanged = pyqtSignal(bool)
    
    def __init__(self, validator, widget, changeListener=None):
        QObject.__init__(self, widget)
        self.__changeListener = changeListener
        if self.__changeListener is not None:
            self.__changeListener.widgetValidator = self
        self.widget = widget
        self.__validationState = None
        self.validator = validator
        self.validator.validationStateChanged.connect(self._onValidationStateChanged)
    
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
    def __init__(self, validator, widget, changeListener=None):
        ValidatorConnection.__init__(self, validator, widget, changeListener=changeListener)
        self.widget.setValidator(self.validator)

class AbstractSpinBoxConnection(ValidatorConnection):
    
    emptyValueText = u'Nichts'
    
    def __init__(self, validator, widget, changeListener=None, emptyValue=None):
        ValidatorConnection.__init__(self, validator, widget, changeListener=changeListener)
        
        self._emptyValue = emptyValue
        #widget.valueChanged.connect(self.onValueChanged)
        widget.setMinimum(self.emptyValue)
        widget.setMaximum(validator.maximum)
        
        if isinstance(widget, QDoubleSpinBox):
            widget.setDecimals(validator.decimals)
        
        #if self.validator.notEmpty:
        self.widget.setSpecialValueText(self.trUtf8(self.emptyValueText))
        
        self.widget.valueChanged.connect(self.onValueChanged)
        
    
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
            self.validator.validate(QString(""), 0)
        else:
            cleanText = self.widget.cleanText()
            self.validator.validate(cleanText, (len(cleanText)-1))
            #print cleanText, type(cleanText), (len(cleanText)-1)
            
class ComboBoxConnection(ValidatorConnection):
    def __init__(self, validator, widget, changeListener=None):
        ValidatorConnection.__init__(self, validator, widget, changeListener=changeListener)
        self.widget.currentIndexChanged.connect(self.onCurrentIndexChanged)
    
    def onCurrentIndexChanged(self, index):
        itemData = variant_to_pyobject(self.widget.itemData(index, Qt.UserRole))
        self.validator.validate(itemData)
        #print "ComboBoxCon: {0} {1}".format(index, itemData)
