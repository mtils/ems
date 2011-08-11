'''
Created on 10.08.2011

@author: michi
'''
from PyQt4.QtGui import QValidator
from base import ValidationVisualizer

class LineEditValidationVisualizer(ValidationVisualizer):
    def __init__(self, widget, validator, helpBubbleText="", parent=None):
        ValidationVisualizer.__init__(self, widget, validator, helpBubbleText,
                                      parent=parent)
    
    def onAcceptable(self):
        self.widget.setStyleSheet(self.acceptableStyleSheet)
        super(LineEditValidationVisualizer, self).onAcceptable()
    
    def onIntermediate(self):
        self.widget.setStyleSheet(self.intermediateStyleSheet)
        super(LineEditValidationVisualizer, self).onIntermediate()
    
    def onInvalid(self):
        self.widget.setStyleSheet(self.invalidStyleSheet)
        super(LineEditValidationVisualizer, self).onInvalid()
    
    def onFocusOut(self):
        if self.validator.validationState == QValidator.Acceptable:
            self.widget.setStyleSheet("")
        super(LineEditValidationVisualizer, self).onFocusOut()
    
    def onFocusIn(self):
        if self.validator.validationState == QValidator.Acceptable:
            self.widget.setStyleSheet(self.acceptableStyleSheet)
        elif self.validator.validationState == QValidator.Intermediate:
            self.widget.setStyleSheet(self.intermediateStyleSheet)
        elif self.validator.validationState == QValidator.Invalid:
            self.widget.setStyleSheet(self.invalidStyleSheet)
        super(LineEditValidationVisualizer, self).onFocusIn()

class SpinBoxValidationVisualizer(ValidationVisualizer):
    def __init__(self, widget, validator, helpBubbleText="", parent=None):
        ValidationVisualizer.__init__(self, widget, validator,
                                      helpBubbleText=helpBubbleText,
                                      parent=parent)
#        self.widget.valueChanged.connect(self.onValueChanged)
    
    def onAcceptable(self):
        self.widget.setStyleSheet(self.acceptableStyleSheet)
        super(SpinBoxValidationVisualizer, self).onAcceptable()
    
    def onIntermediate(self):
        self.widget.setStyleSheet(self.intermediateStyleSheet)
        super(SpinBoxValidationVisualizer, self).onIntermediate()
    
    def onInvalid(self):
        self.widget.setStyleSheet(self.invalidStyleSheet)
        super(SpinBoxValidationVisualizer, self).onInvalid()
    
    def onFocusIn(self):
        if self.validator.validationState == QValidator.Acceptable:
            self.widget.setStyleSheet(self.acceptableStyleSheet)
        elif self.validator.validationState == QValidator.Intermediate:
            self.widget.setStyleSheet(self.intermediateStyleSheet)
        elif self.validator.validationState == QValidator.Invalid:
            self.widget.setStyleSheet(self.invalidStyleSheet)
        super(SpinBoxValidationVisualizer, self).onFocusIn()
    
    def onFocusOut(self):
        if self.validator.validationState == QValidator.Acceptable:
            self.widget.setStyleSheet("")
        super(SpinBoxValidationVisualizer, self).onFocusOut()
        