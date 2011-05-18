'''
Created on 18.05.2011

@author: michi
'''
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class ColorButton(QPushButton):
    
    colorChanged = pyqtSignal(QColor)
    
    def __init__(self, parent=None):
        super(ColorButton, self).__init__(parent)
        self.color = QColor(Qt.white)
        self.connect(self, SIGNAL("pressed()"),
                     self.selectColor)
        
    
    def buildColorString(self, color):
        
        colorString = "background-color: rgb(%s, %s, %s);" % (color.red(),
                                                              color.green(),
                                                              color.blue())
        styleSheet = 'QPushButton{' + colorString + '}'
        return styleSheet
    
    def selectColor(self):
        color = QColorDialog.getColor(initial=self.color, parent=self)
        self.setColor(color)
    
    @pyqtSlot(QColor)
    def setColor(self, color):
        self.color = color
        self.setStyleSheet(self.buildColorString(color))
        self.colorChanged.emit(color)