'''
Created on 17.05.2011

@author: michi
'''

from __future__ import division
import platform
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ems.qt4.gui.widgets.stats import TiledBar #@UnresolvedImport

class StatsTest(QDialog):
    def __init__(self, parent=None):
        super(StatsTest, self).__init__(parent)
        self.setupUi()
        
    def setupUi(self):
        self.bar = TiledBar(self)

        
        
        self.mainLayout = QGridLayout(self)
        maxValueInput = QSpinBox(self)
        maxValueInput.setMaximum(5000000)
        maxValueInput.setMinimum(1)
        maxValueInput.setValue(100)
        maxValueInput.setSuffix(" max")
        self.mainLayout.addWidget(maxValueInput, 0, 0, 1, 2)
        self.bar.maxValue = maxValueInput.value()
        self.connect(maxValueInput, SIGNAL("valueChanged(int)"),
                     self.bar,SLOT("setMaxValue(int)"))
        
        valueInputs = []
        colorInputs = []
        for i in range(4):
            valueInput = QSpinBox(self)
            valueInput.setObjectName("val_%s" % i)
            colorInput = ColorButton(self)
            colorInput.setObjectName("col_%s" % i)
            valueInputs.append(valueInput)
            colorInputs.append(colorInput)
            self.mainLayout.addWidget(valueInput, (i+1), 0)
            self.mainLayout.addWidget(colorInput, (i+1), 1)
            self.bar.addValue(valueInput.value(),colorInput.color)
            self.connect(colorInput, SIGNAL('colorChanged(QColor)'),
                         self.on_color_changed)
            self.connect(valueInput, SIGNAL('valueChanged(int)'),
                         self.on_value_changed)
        
        self.mainLayout.addWidget(self.bar, 0, 2, 5, 1)
        
        self.setWindowTitle("Fraction Slider")
        self.resize(QSize(150,200))
        
    def on_color_changed(self, color):
        senderName = unicode(self.sender().objectName())
        index = int(senderName.split("_")[1])
        self.bar.setColor(index,color)
    
    def on_value_changed(self, val):
        senderName = unicode(self.sender().objectName())
        index = int(senderName.split("_")[1])
        self.bar.setValue(index,val)

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
        

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = StatsTest()

    
    form.show()
    app.exec_()