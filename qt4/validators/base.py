'''
Created on 10.08.2011

@author: michi
'''
import datetime

from PyQt4.QtCore import pyqtSignal, QString, QDateTime, QDate, QTime, QObject
from PyQt4.QtGui import QRegExpValidator, QIntValidator, QDoubleValidator, QValidator



class BaseValidator(QValidator):
    
    validationStateChanged = pyqtSignal(int)
    
    def __init__(self, notEmpty=False, requiresUserInteraction=False,
                  parent=None):
        self.__validationState = 99
        QValidator.__init__(self, parent)
        self.errorMsg = self.trUtf8("Dieses ist ein Pflichtfeld")
        self.notEmpty = notEmpty
        self.requiresUserInteraction = requiresUserInteraction
    
    def _setValidationState(self, state):
        if self.__validationState != state:
            self.validationStateChanged.emit(state)
        self.__validationState = state
    
    @property
    def validationState(self):
        return self.__validationState
    
    def _isEmpty(self, input):
        if isinstance(input, QString):
            return (len(input) < 1)
    
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
        elif input is None:
            if self.notEmpty:
                return (QValidator.Intermediate, pos)
            return (QValidator.Acceptable, pos)
        else:
            raise TypeError("BaseValidator can only handle QString, float, int and bool " +
                            "not {0}".format(input))
    
    def validate(self, input, pos=0, qObject=None):
        
        if isinstance(qObject, QObject):
            if qObject.property('isEmpty').toBool():
                if self.notEmpty:
                    res = (QValidator.Intermediate, pos)
                    self._setValidationState(res[0])
                    return res

        res = self._validate(input, pos)
        #print res, QValidator.Acceptable
        self._setValidationState(res[0])
        return res

class StringValidator(BaseValidator):
    def __init__(self, minLength=0, maxLength=0, *args, **kwargs):
        super(StringValidator, self).__init__(*args, **kwargs)
        self.minLength = minLength
        self.maxLength = maxLength
    
    def _validate(self, input, pos):
        if self._isEmpty(input):
            return (QValidator.Acceptable, pos)
        res = BaseValidator._validate(self, input, pos)
        if res[0] == QValidator.Invalid:
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
        if self._isEmpty(input):
            return (QValidator.Acceptable, pos)
        res = StringValidator._validate(self, input, pos)
        if res[0] == QValidator.Invalid:
            return res
        res, pos = self.qRegExpValidator.validate(input, pos)

        return (res, pos)

class IntValidator(BaseValidator):
    
    defaultMinimum = 0
    defaultMaximum = 2147483647
    
    def __init__(self, minimum=None, maximum=None, *args, **kwargs):
        BaseValidator.__init__(self, *args, **kwargs)
        if minimum is None:
            minimum = self.defaultMinimum
        if maximum is None:
            maximum = self.defaultMaximum
        self.minimum = minimum
        self.maximum = maximum
    
    def _minMaxTest(self, input, pos):
        try:
            intVal = float(unicode(input))
            if intVal < self.minimum:
                if intVal <= self.maximum:
                    return (QValidator.Intermediate, pos)
                else:
                    return (QValidator.Invalid, pos)
            if intVal >= self.minimum:
                if intVal <= self.maximum:
                    return (QValidator.Acceptable, pos)
                else:
                    return (QValidator.Invalid, pos)
        except ValueError:
            return (QValidator.Invalid, pos)
        return (QValidator.Intermediate, pos)
    
    def _validate(self, input, pos):
#        print "input: {0} {1}".format(input, self._isEmpty(input))
        if self._isEmpty(input):
            if self.notEmpty:
                return (QValidator.Intermediate, pos)
            else:
                return (QValidator.Acceptable, pos)
        return self._minMaxTest(input, pos)

class FloatValidator(IntValidator):
    
    defaultMinimum = 0
    defaultMaximum = 2147483647.0
    defaultDecimals = 2
    
    def __init__(self, minimum=None, maximum=None, decimals=None, *args, **kwargs):
        IntValidator.__init__(self, minimum, maximum, *args, **kwargs)
        self.minimum = float(self.minimum)
        self.maximum = float(self.maximum)
        if decimals is None:
            decimals = self.defaultDecimals
        self.decimals = decimals
    
    def _validate(self, input, pos):
#        print "input: {0} {1}".format(input, self._isEmpty(input))
        valInput = QString(str(input).replace(',', '.'))
        if self._isEmpty(valInput):
            if self.notEmpty:
                return (QValidator.Intermediate, pos)
            else:
                return (QValidator.Acceptable, pos)
        splitted = str(valInput).split('.')
        decimals = 0
        if len(splitted) > 1:
            decimals = len(splitted[-1])
        if decimals > self.decimals:
            return (QValidator.Invalid, pos)
        #print "split: {0}".format(decimals)
        return self._minMaxTest(valInput, pos)

class IsInstanceValidator(BaseValidator):
    def __init__(self, class_, *args, **kwargs):
        super(IsInstanceValidator, self).__init__(*args, **kwargs)
        self.class_ = class_
    
    def _validate(self, input, pos=0):
        if not self.notEmpty:
            if input is None:
                return (QValidator.Acceptable, pos)
        if isinstance(input, self.class_):
            return (QValidator.Acceptable, pos)
        return (QValidator.Intermediate, pos)
            
class IsInValidator(BaseValidator):
    def __init__(self, listToTest, *args, **kwargs):
        super(IsInValidator, self).__init__(*args, **kwargs)
        self.listToTest = listToTest
        
    def _validate(self, input, pos=0):
        if not self.notEmpty:
            if input is None:
#                print "Valid because empty"
                return (QValidator.Acceptable, pos)
        if input in self.listToTest:
#            print "Valid because in list"
            return (QValidator.Acceptable, pos)
#        print "Intermediate because end of method"
        return (QValidator.Intermediate, pos)

class DateTimeValidator(BaseValidator):
    
    absMinDateTime = QDateTime(QDate(1752,9,14),QTime(0,0))
    absMaxDateTime = QDateTime(QDate(7999,12,31),QTime(23,59))
    
    def __init__(self, minDateTime=None, maxDateTime=None, *args, **kwargs):
        super(DateTimeValidator, self).__init__(*args, **kwargs)

        if minDateTime is None:
            minDateTime = self.absMinDateTime
        self.minDateTime = minDateTime
        
        if maxDateTime is None:
            maxDateTime = self.absMaxDateTime
        self.maxDateTime = maxDateTime
        
    
    def _validate(self, input, pos=0):
        if input >= self.minDateTime:
            if input <= self.maxDateTime: 
                return (QValidator.Acceptable, pos)
            else:
                return (QValidator.Intermediate, pos)
        
        return (QValidator.Intermediate, pos)

class DateValidator(BaseValidator):
    
    absMinDate = QDate(1752,9,14)
    absMaxDate = QDate(7999,12,31)
    
    def __init__(self, minDate=None, maxDate=None, *args, **kwargs):
        super(DateValidator, self).__init__(*args, **kwargs)

        if minDate is None:
            minDate = self.absMinDate
        self.minDate = minDate
        
        if maxDate is None:
            maxDate = self.absMaxDate
        self.maxDate = maxDate
        
    
    def _validate(self, input, pos=0):
        if input >= self.minDate:
            if input <= self.maxDate: 
                return (QValidator.Acceptable, pos)
            else:
                return (QValidator.Intermediate, pos)
        
        return (QValidator.Intermediate, pos)

class TimeValidator(BaseValidator):
    
    def __init__(self, minTime=None, maxTime=None, *args, **kwargs):
        super(TimeValidator, self).__init__(*args, **kwargs)

        if minTime is None:
            minTime = QTime(0,0)
        self.minTime = minTime
        
        if maxTime is None:
            maxTime = QTime(23,59,59)
        self.maxTime = maxTime
        
    
    def _validate(self, input, pos=0):
        if input >= self.minTime:
            if input <= self.maxTime: 
                return (QValidator.Acceptable, pos)
            else:
                return (QValidator.Intermediate, pos)
        
        return (QValidator.Intermediate, pos)

class BoolValidator(BaseValidator):
    def __init__(self, notEmpty=False, requiresUserInteraction=False, 
        parent=None):
        BaseValidator.__init__(self, notEmpty=notEmpty,
                               requiresUserInteraction=requiresUserInteraction,
                               parent=parent)
    
#    def _validate(self, input, pos=0):
#        return QValidator