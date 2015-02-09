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

class SpinBoxValidationVisualizer(ValidationVisualizer):
    def __init__(self, widget, validator, helpBubbleText="", parent=None):
        ValidationVisualizer.__init__(self, widget, validator,
                                      helpBubbleText=helpBubbleText,
                                      parent=parent)