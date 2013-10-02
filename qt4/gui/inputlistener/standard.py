'''
Created on 14.08.2011

@author: michi
'''
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, SIGNAL, SLOT, QString,\
    Qt, QDate, QTime, QDateTime, QVariant, QEvent
from PyQt4.QtGui import QValidator, QDoubleSpinBox, QAbstractButton, \
    QAbstractSpinBox, QLineEdit, QDateTimeEdit, QDateEdit, QTimeEdit, QSpinBox,\
    QComboBox, QButtonGroup, QCheckBox
from ems.qt4.util import variant_to_pyobject


class InputListener(QObject):
    
    dirtyStateChanged = pyqtSignal(bool)
    hasBeenEditedStateChanged = pyqtSignal(bool)
    hadFocusStateChanged = pyqtSignal(bool)
    hasFocusStateChanged = pyqtSignal(bool)
    
    PROP_DIRTY = 'isDirty'
    PROP_HASBEENEDITED = 'hasBeenEdited'
    PROP_HADFOCUS = 'hadFocus'
    
    def __init__(self, qObject, parent=None):
        QObject.__init__(self, parent)
        self._dirty = False
        self._hasBeenEdited = False
        self._hadFocus = False
        self.qObject = qObject
        self._installEventFilter(self.qObject)
        self._hasFocus = False
        if not isinstance(qObject, self.supportedClasses):
            raise TypeError("{0} only supports {1}", self.supportedClasses)
    
    @property
    def supportedClasses(self):
        raise NotImplementedError("Please implement {0}.supportedClasses"\
                                  .format(self.__class__.__name__))
    
    @property
    def hasFocus(self):
        return self._hasFocus
    
    def _setDirty(self, state):
        if self._dirty != state:
            self._dirty = state
            self.qObject.setProperty(self.PROP_DIRTY, QVariant(state))
            self.dirtyStateChanged.emit(state)
            #print "{0}._setDirty {1}".format(self.qObject.objectName(), state)
    
    def _installEventFilter(self, qObject):
        qObject.installEventFilter(self)
    
    def eventFilter(self, qObject, event):
        if event.type() == QEvent.FocusIn:
            self._hasFocus = True
            self._setHadFocus(True)
            self.hasFocusStateChanged.emit(True)
        if event.type() == QEvent.FocusOut:
            self._hasFocus = False
            self.hasFocusStateChanged.emit(False)
        return False
            
    @property
    def dirty(self):
        return self._dirty
    
    def _setHasBeenEdited(self, state):
        if self._hasBeenEdited != state:
            self._hasBeenEdited = state
            self.qObject.setProperty(self.PROP_HASBEENEDITED, QVariant(state))
            self.hasBeenEditedStateChanged.emit(state)
#            print "{0}._setHasBeenEdited {1}".format(self.qObject.objectName(),
#                                                     state)
    
    @property
    def hasBeenEdited(self):
        return self._hasBeenEdited
    
    def _setHadFocus(self, state):
        if self._hadFocus != state:
            self._hadFocus = state
            self.qObject.setProperty(self.PROP_HADFOCUS, QVariant(state))
            self.hadFocusStateChanged.emit(state)
#            print "{0}._setHadFocus {1}".format(self.qObject.objectName(),
#                                                state)
            
    @property
    def hadFocus(self):
        return self._hadFocus
    
    @pyqtSlot()
    def reset(self):
        self._setDirty(False)
        self._setHasBeenEdited(False)
        self._setHadFocus(False)

class AbstractLineEditListener(InputListener):
    def __init__(self, qObject, parent=None):
        InputListener.__init__(self, qObject, parent)
        self._initialValue = None
        self._setInitValue(self.qObject)
        self._connectWidget(self.qObject)
    
    def _connectWidget(self, widget):
        raise NotImplementedError()
    
    def _setInitValue(self, widget):
        raise NotImplementedError()
        
    def onValueChanged(self, value):
        if value != self._initialValue:
            self._setDirty(True)
        else:
            self._setDirty(False)
        self._setHasBeenEdited(True)
#        if self.qObject.hasFocus():
#            self._setHadFocus(True)
    
    @pyqtSlot()
    def reset(self):
        InputListener.reset(self)
        self._setInitValue(self.qObject)

class SpinBoxListener(AbstractLineEditListener):
    
    @property
    def supportedClasses(self):
        return (QSpinBox, QDoubleSpinBox)
    
    def _instanceCheck(self):
        if not isinstance(self.qObject, ()):
            raise TypeError("")
    def _connectWidget(self, widget):
        widget.valueChanged.connect(self.onValueChanged)
        
    def _setInitValue(self, widget):
        self._initialValue = widget.value()

class LineEditListener(AbstractLineEditListener):
    
    @property
    def supportedClasses(self):
        return (QLineEdit,)
    
    def _connectWidget(self, widget):
        widget.textEdited.connect(self.onValueChanged)
        
    def _setInitValue(self, widget):
        self._initialValue = widget.text()

class DateTimeListener(AbstractLineEditListener):
    
    @property
    def supportedClasses(self):
        return (QDateTimeEdit, QDateEdit, QTimeEdit)
    
    def _connectWidget(self, widget):
        if isinstance(self.qObject, QDateTimeEdit):
            widget.dateTimeChanged.connect(self.onValueChanged)
        elif isinstance(self.qObject, QDateEdit):
            widget.dateChanged.connect(self.onValueChanged)
        elif isinstance(self.qObject, QTimeEdit):
            widget.timeChanged.connect(self.onValueChanged)
        
    def _setInitValue(self, widget):
        if isinstance(self.qObject, QDateTimeEdit):
            self._initialValue = widget.dateTime()
        elif isinstance(self.qObject, QDateEdit):
            self._initialValue = widget.date()
        elif isinstance(self.qObject, QTimeEdit):
            self._initialValue = widget.time()

class CheckBoxListener(AbstractLineEditListener):
    
    @property
    def supportedClasses(self):
        return (QCheckBox,)
    
    def _connectWidget(self, widget):
        widget.stateChanged.connect(self.onValueChanged)
    
    def _setInitValue(self, widget):
        self._initialValue = widget.checkState()


class ComboBoxListener(InputListener):
    def __init__(self, qObject, parent=None):
        InputListener.__init__(self, qObject, parent=parent)
        self._initialIndex = self.qObject.currentIndex()
        self.qObject.currentIndexChanged.connect(self.onCurrentIndexChanged)
    
    @property
    def supportedClasses(self):
        return (QComboBox,)
    
    def onCurrentIndexChanged(self, index):
        if self._initialIndex != index:
            self._setDirty(True)
        else:
            self._setDirty(False)
        self._setHasBeenEdited(True)
#        if self.qObject.hasFocus():
#            self._setHadFocus(True)
    
    @pyqtSlot()
    def reset(self):
        InputListener.reset(self)
        self._initialIndex = self.qObject.currentIndex()

class ButtonGroupListener(InputListener):
    def __init__(self, qObject, parent=None):
        InputListener.__init__(self, qObject, parent=parent)
        self._hasFocus = False
        self._setInitialCheckedButtons()
        self.qObject.buttonClicked.connect(self.onButtonClicked)
    
    @property
    def supportedClasses(self):
        return (QButtonGroup,)
    
    def onButtonClicked(self, button):
        self._setDirty(self._checkedButtonsChanged())
        self._setHasBeenEdited(True)
    
    def _setInitialCheckedButtons(self):
        self._initialCheckedButtons = []
        for button in self.qObject.buttons():
            if button.isChecked():
                self._initialCheckedButtons.append(button)
    
    def _checkedButtonsChanged(self):
        for button in self.qObject.buttons():
            if button.isChecked():
                if button not in self._initialCheckedButtons:
                    return True
            if not button.isChecked():
                if button in self._initialCheckedButtons:
                    return True
        return False
    
    def _installEventFilter(self, widget):
        for button in widget.buttons():
            button.installEventFilter(self)
    
    def eventFilter(self, qObject, event):
        if event.type() == QEvent.FocusOut:
            self.focusOutCheck(qObject)
            
        if event.type() == QEvent.FocusIn:
            self.focusInCheck(qObject)
            
        return False
    
    def focusInCheck(self, object):
        if not self._hasFocus:
            self._hasFocus = True
            self._setHadFocus(True)
            self.hasFocusStateChanged.emit(True)
            
    def focusOutCheck(self, object):
        for button in self.qObject.buttons():
            if button.hasFocus():
                return
        self._hasFocus = False
        self.hasFocusStateChanged.emit(False)
    
    @pyqtSlot()
    def reset(self):
        InputListener.reset(self)
        self._hasFocus = False
        self._setInitialCheckedButtons()
        
    
        