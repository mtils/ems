'''
Created on 17.05.2011

@author: michi
'''

from __future__ import division
import platform
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ems.qt4.gui.widgets.stats import TiledBar, Ruler, MultiBarRulered #@UnresolvedImport
from ems.qt4.gui.widgets.graphical import ColorButton #@UnresolvedImport

class StatsTest(QDialog):
    def __init__(self, parent=None):
        super(StatsTest, self).__init__(parent)
        self.setupUi()
        
    def setupUi(self):
        self.bar = MultiBarRulered(parent=self)
        self.mainLayout = QHBoxLayout(self)
        maxValueInput = QSpinBox(self)
        maxValueInput.setMaximum(5000000)
        maxValueInput.setMinimum(1)
        maxValueInput.setValue(100)
        maxValueInput.setSuffix(" max")
        self.mainLayout.addWidget(maxValueInput)
        self.bar.maxValue = maxValueInput.value()
        self.connect(maxValueInput, SIGNAL("valueChanged(int)"),
                     self.bar,SLOT("setMaxValue(int)"))
        
        valueInputs = []
        colorInputs = []
        labels = ('Verlust','Erzeugung','Einsatz')
        for b in range(3):
            print b
            group = QGroupBox(labels[b],self)
            self.mainLayout.addWidget(group)
            group.bLayout = QGridLayout(group)
            
            for i in range(4):
                valueInput = QSpinBox(self)
                valueInput.setObjectName("val_%s_%s" % (b,i))
                colorInput = ColorButton(self)
                colorInput.setObjectName("col_%s_%s" % (b,i))
                valueInputs.append(valueInput)
                colorInputs.append(colorInput)
                group.bLayout.addWidget(valueInput, 3-i, 0)
                group.bLayout.addWidget(colorInput, 3-i, 1)
                self.bar.addValue(b,valueInput.value(),colorInput.color)
                self.connect(colorInput, SIGNAL('colorChanged(QColor)'),
                             self.on_color_changed)
                self.connect(valueInput, SIGNAL('valueChanged(int)'),
                             self.on_value_changed)
        
        self.mainLayout.addWidget(self.bar)
        
        self.setWindowTitle("Fraction Slider")
        self.resize(QSize(150,200))
        
    def on_color_changed(self, color):
        senderName = unicode(self.sender().objectName())
        splitted = senderName.split("_")
        bar = int(splitted[1])
        idx = int(splitted[2])
        self.bar.setColor(bar,idx,color)
    
    def on_value_changed(self, val):
        senderName = unicode(self.sender().objectName())
        splitted = senderName.split("_")
        bar = int(splitted[1])
        idx = int(splitted[2])
        self.bar.setValue(bar,idx,val)

class RulerTest(QDialog):
    def __init__(self, parent=None):
        super(RulerTest, self).__init__(parent)
        self.setupUi()
        
    def setupUi(self):
        self.mainLayout = QGridLayout(self)
        self.ruler = Ruler(100,parent=self)
        self.mainLayout.addWidget(self.ruler)
        self.resize(QSize(150,200))
        

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    
    form = StatsTest()
    #form = RulerTest()

    
    form.show()
    app.exec_()