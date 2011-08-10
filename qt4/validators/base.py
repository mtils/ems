'''
Created on 10.08.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSignal, QString
from PyQt4.QtGui import QRegExpValidator, QIntValidator, QDoubleValidator, QValidator


class BaseValidator(QValidator):
    
    validationStateChanged = pyqtSignal(int)
    
    def __init__(self, notEmpty=False, requiresUserInteraction=False,
                  parent=None):
        self.__validationState = 99
        self.errorMsg = self.trUtf8("Dieses ist ein Pflichtfeld")
        QValidator.__init__(self, parent)
        self.notEmpty = notEmpty
        self.requiresUserInteraction = requiresUserInteraction
    
    def _setValidationState(self, state):
        if self.__validationState != state:
            self.validationStateChanged.emit(state)
        self.__validationState = state
    
    @property
    def validationState(self):
        return self.__validationState
    
    def _validate(self, input, pos):
        if isinstance(input, QString):
            inputStr = unicode(input)
            if self.notEmpty:
                if not len(inputStr):
                    return (QValidator.Intermediate, pos)
            return (QValidator.Acceptable, pos)
            
        elif isinstance(input, (int, float)):
            if self.notEmpty:
                if bool(input):
                    return (QValidator.Intermediate, pos)
            return (QValidator.Acceptable, pos)
        elif isinstance(input, bool):
            return (QValidator.Acceptable, pos)
        else:
            raise TypeError("BaseValidator can only handle QString, float, int and bool")
        #print input, pos, type(input), type(pos)
    def validate(self, input, pos):
        res = self._validate(input, pos)
        self._setValidationState(res[0])
        return res

class StringValidator(BaseValidator):
    def __init__(self, minLength=0, maxLength=0, *args, **kwargs):
        super(StringValidator, self).__init__(*args, **kwargs)
        self.minLength = minLength
        self.maxLength = maxLength
    
    def _validate(self, input, pos):
        res = BaseValidator._validate(self, input, pos)
        if res[0] == QValidator.Invalid:
            print "invalid per BaseValidator"
            return res 
        if res[0] == QValidator.Acceptable:
            inputStr = unicode(input)
            strLen = len(inputStr)
            if self.minLength > 0:
                if strLen < self.minLength:
                    return (QValidator.Intermediate, pos)
            if self.maxLength > 0:
                if strLen <= self.maxLength:
                    return (QValidator.Acceptable, pos)
                else:
                    return (QValidator.Invalid, pos)
        return res
        
class RegExpValidator(StringValidator):
    
    validationStateChanged = pyqtSignal(int)
    
    def __init__(self, regExpString,  *args, **kwargs):
        StringValidator.__init__(self, *args, **kwargs)
        self.regExpString = regExpString
        self.qRegExpValidator = QRegExpValidator(self.regExpString, self)
    
    def fixup(self, input):
        return self.qRegExpValidator.fixup(input)
    
    def _validate(self, input, pos):
        res = StringValidator._validate(self, input, pos)
        if res[0] == QValidator.Invalid:
            print "Invalid per QStringValidator"
            return res
        res, pos = self.qRegExpValidator.validate(input, pos)

        return (res, pos)

