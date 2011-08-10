'''
Created on 10.08.2011

@author: michi
'''
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt4.QtGui import QValidator

class ValidatorConnection(QObject):
    
    isValidStateChanged = pyqtSignal(bool)
    
    def __init__(self, validator, widget, changeListener=None):
        QObject.__init__(self, widget)
        self.__changeListener = changeListener
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
