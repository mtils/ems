'''
Created on 10.08.2011

@author: michi
'''
from PyQt4.QtCore import QObject, QEvent, Qt, QPoint, QVariant
from PyQt4.QtGui import QWidget, QLabel, QValidator, QButtonGroup

class ValidationVisualizer(QObject):
    
    STATE_PROPERTY = 'validationState'
    MANDATORY_PROPERTY = 'mandatory'
    STATE_ACCEPTABLE = 'Acceptable'
    STATE_INTERMEDIATE = 'Intermediate'
    STATE_INVALID = 'Invalid'
    
    def __init__(self, validator, widget, helpBubbleText="",
                 additionalWidgets=[]):
        
        QObject.__init__(self, widget)
        if not isinstance(widget, QWidget):
            if isinstance(widget, QButtonGroup):
                raise TypeError("The widget parameter has to be QWidget " +
                                "for QButtonGroup use QButtonGroupVisualizer")
            raise TypeError("The widget parameter has to be QWidget")
        
        if isinstance(additionalWidgets, QWidget):
            self.additionalWidgets = [additionalWidgets]
        else:
            self.additionalWidgets = additionalWidgets
        self.widget = widget
        self.validator = validator
        self.widget.setProperty(ValidationVisualizer.STATE_PROPERTY,
                                QVariant())
        self.widget.installEventFilter(self)
        self._helpBubbleText = helpBubbleText
        self.widgetValidator = None
        if isinstance(self.widget.parent(), QWidget):
            self._helpBubble = QLabel(self.widget.parent())
        else:
            self._helpBubble = QLabel(self.widget)
        
        self._helpBubble.setText("Bitte geben Sie nur Buchstaben ein")
        self._helpBubble.setFrameShape(QLabel.Box)
        self._helpBubble.setFocusPolicy(Qt.NoFocus)
        self._helpBubble.setStyleSheet('background-color: #fff')
        self._helpBubble.setWindowFlags(self._helpBubble.windowFlags() | Qt.ToolTip)
        self._helpBubble.hide()
    
    def eventFilter(self, object, event):
        if event.type() == QEvent.FocusOut:
            self.onFocusOut()
        if event.type() == QEvent.FocusIn:
            self.onFocusIn()
        return False
    
    def showHelpBubble(self):
        if not self._helpBubble.isVisible():
            pos = QPoint(0,0-self._helpBubble.height())
            self._helpBubble.move(self.widget.mapToGlobal(pos))
            self._helpBubble.show()
            
    def hideHelpBubble(self):
        if self._helpBubble.isVisible():
            self._helpBubble.hide()
            
    @staticmethod
    def setWidgetStateProperty(widget, state):
#        print widget, state, widget.style()
#        if isinstance(widget, QLabel):
#            widget.setText(unicode(widget.text()) + "*")
        widget.setProperty(ValidationVisualizer.STATE_PROPERTY,QVariant(state))
        widget.style().unpolish(widget)
        #widget.ensurePolished()
        widget.style().polish(widget)
    
    def onAcceptable(self):
        self.setWidgetStateProperty(self.widget, self.STATE_ACCEPTABLE)
        for widget in self.additionalWidgets:
            self.setWidgetStateProperty(widget, self.STATE_ACCEPTABLE)
        #print "Setted {0}".format(self.STATE_ACCEPTABLE)
        self.hideHelpBubble()
    
    def onIntermediate(self):
        self.setWidgetStateProperty(self.widget, self.STATE_INTERMEDIATE)
        for widget in self.additionalWidgets:
            self.setWidgetStateProperty(widget, self.STATE_INTERMEDIATE)
        #print "Setted {0}".format(self.STATE_INTERMEDIATE)
        self.hideHelpBubble()
    
    def onInvalid(self):
        self.setWidgetStateProperty(self.widget, self.STATE_INVALID)
        for widget in self.additionalWidgets:
            self.setWidgetStateProperty(widget, self.STATE_INVALID)
        if self.widget.hasFocus():
            self.showHelpBubble()
    
    def onFocusOut(self):
        self.hideHelpBubble()
    
    def onFocusIn(self):
        if self.validator.validationState == QValidator.Invalid:
            self.showHelpBubble()

class ButtonGroupVisualizer(ValidationVisualizer):
    def __init__(self, validator, buttonGroup, helpBubbleText="",
                  additionalWidgets=[]):
        
        QObject.__init__(self, buttonGroup)
        
        if not isinstance(buttonGroup, QButtonGroup):
            raise TypeError("The buttonGroup parameter has to be QButtonGroup")
        self.buttonGroup = buttonGroup
        self.validator = validator
        if isinstance(additionalWidgets, QWidget):
            self.additionalWidgets = [additionalWidgets]
        else:
            self.additionalWidgets = additionalWidgets
            
        for button in self.buttonGroup.buttons():
            button.setProperty(ValidationVisualizer.STATE_PROPERTY,
                                    QVariant())
            button.installEventFilter(self)
            
        self._helpBubbleText = helpBubbleText
        self.widgetValidator = None
        self.parentWidget = None
        if isinstance(self.buttonGroup.parent(), QWidget):
            self.parentWidget = self.buttonGroup.parent()
        else:
            self.parentWidget = self.buttonGroup.buttons()[0]
        
        #print self.parentWidget
        
        self.hasFocus = False
            
        self._helpBubble = QLabel(self.parentWidget)
        
        self._helpBubble.setText("Bitte geben Sie nur Buchstaben ein")
        self._helpBubble.setFrameShape(QLabel.Box)
        self._helpBubble.setFocusPolicy(Qt.NoFocus)
        self._helpBubble.setStyleSheet('background-color: #fff')
        self._helpBubble.setWindowFlags(self._helpBubble.windowFlags() | Qt.ToolTip)
        self._helpBubble.hide()
    
    def eventFilter(self, object, event):
        if event.type() == QEvent.FocusOut:
            self.focusOutCheck(object)
            
        if event.type() == QEvent.FocusIn:
            self.focusInCheck(object)
        return False
    
    def showHelpBubble(self):
        if not self._helpBubble.isVisible():
            pos = QPoint(0,0-self._helpBubble.height())
            self._helpBubble.move(self.buttonGroup.mapToGlobal(pos))
            self._helpBubble.show()
            
    def hideHelpBubble(self):
        if self._helpBubble.isVisible():
            self._helpBubble.hide()
    
    def onAcceptable(self):
        for button in self.buttonGroup.buttons():
            self.setWidgetStateProperty(button, self.STATE_ACCEPTABLE)
            for widget in self.additionalWidgets:
                self.setWidgetStateProperty(widget, self.STATE_ACCEPTABLE)
#            print "Setted {1} {0}".format(ValidationVisualizer.STATE_ACCEPTABLE,button.text())
        self.hideHelpBubble()
    
    def onIntermediate(self):
        for button in self.buttonGroup.buttons():
            self.setWidgetStateProperty(button, self.STATE_INTERMEDIATE)
#            print "Setted {1} {0}".format(ValidationVisualizer.STATE_INTERMEDIATE, button.text())
        for widget in self.additionalWidgets:
            self.setWidgetStateProperty(widget, self.STATE_INTERMEDIATE)
        self.hideHelpBubble()
    
    def onInvalid(self):
        for button in self.buttonGroup.buttons():
            self.setWidgetStateProperty(button, self.STATE_INVALID)
#            print "Setted {1} {0}".format(ValidationVisualizer.STATE_INVALID, button.text())
        for widget in self.additionalWidgets:
            self.setWidgetStateProperty(widget, self.STATE_INVALID)
        if self.buttonGroup.hasFocus():
            self.showHelpBubble()
    
    def focusInCheck(self, object):
        if not self.hasFocus:
            self.hasFocus = True
            self.onFocusIn(object)
            
    def focusOutCheck(self, object):
        for button in self.buttonGroup.buttons():
            if button.hasFocus():
                return
        self.hasFocus = False
        self.onFocusOut(object)
        
    def onFocusOut(self, object):
#        print "focusOut {0}".format(object)
        self.hideHelpBubble()
    
    def onFocusIn(self, object):
#        print "focusIn {0}".format(object)
        if self.validator.validationState == QValidator.Invalid:
            self.showHelpBubble()