'''
Created on 10.08.2011

@author: michi
'''
from PyQt4.QtCore import QObject, QEvent, Qt, QPoint, QVariant
from PyQt4.QtGui import QWidget, QLabel, QValidator

class ValidationVisualizer(QObject):
    
    initialColor = 'background: #fff'
    acceptableStyleSheet = 'background: #bfffbf'
    intermediateStyleSheet = 'background: #ffffc0'
    invalidStyleSheet = 'background: #e86F6B'
    
    STATE_PROPERTY = 'validationState'
    MANDATORY_PROPERTY = 'mandatory'
    STATE_ACCEPTABLE = 'Acceptable'
    STATE_INTERMEDIATE = 'Intermediate'
    STATE_INVALID = 'Invalid'
    
    def __init__(self, widget, validator, helpBubbleText="", parent=None):
        QObject.__init__(self, parent)
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
        self._helpBubble.setWindowFlags(Qt.ToolTip)
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
    
    def onAcceptable(self):
        self.widget.setProperty(self.STATE_PROPERTY,
                                QVariant(self.STATE_ACCEPTABLE))
        self.widget.style().unpolish(self.widget)
        self.widget.ensurePolished()
        #print "Setted {0}".format(self.STATE_ACCEPTABLE)
        self.hideHelpBubble()
    
    def onIntermediate(self):
        self.widget.setProperty(self.STATE_PROPERTY,
                                QVariant(self.STATE_INTERMEDIATE))
        self.widget.style().unpolish(self.widget)
        self.widget.ensurePolished()
        #print "Setted {0}".format(self.STATE_INTERMEDIATE)
        self.hideHelpBubble()
    
    def onInvalid(self):
        self.widget.setProperty(self.STATE_PROPERTY,
                                QVariant(self.STATE_INVALID))
        #print "Setted {0}".format(self.STATE_INVALID)
        self.widget.style().unpolish(self.widget)
        self.widget.ensurePolished()
        
        if self.widget.hasFocus():
            self.showHelpBubble()
    
    def onFocusOut(self):
        self.hideHelpBubble()
    
    def onFocusIn(self):
        if self.validator.validationState == QValidator.Invalid:
            self.showHelpBubble()