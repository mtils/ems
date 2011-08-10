'''
Created on 10.08.2011

@author: michi
'''
from PyQt4.QtCore import QObject, QEvent, Qt, QPoint
from PyQt4.QtGui import QWidget, QLabel, QValidator

class ValidationVisualizer(QObject):
    
    initialColor = 'background: #fff'
    acceptableStyleSheet = 'background: #bfffbf'
    intermediateStyleSheet = 'background: #ffffc0'
    invalidStyleSheet = 'background: #e86F6B'
    
    def __init__(self, widget, validator, helpBubbleText="", parent=None):
        QObject.__init__(self, parent)
        self.widget = widget
        self.validator = validator
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
        self.hideHelpBubble()
    
    def onIntermediate(self):
        self.hideHelpBubble()
    
    def onInvalid(self):
        if self.widget.hasFocus():
            self.showHelpBubble()
    
    def onFocusOut(self):
        self.hideHelpBubble()
    
    def onFocusIn(self):
        if self.validator.validationState == QValidator.Invalid:
            self.showHelpBubble()