'''
Created on 17.05.2011

@author: michi
'''
from __future__ import division
import platform
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ems.qt4.gui.painterpilots.stats import RulerPainter, TiledBarPainter  #@UnresolvedImport

class TiledBar(QWidget):
    WSTRING = '999'
    def __init__(self, maxValue=100, parent=None):
        self._maxValue = maxValue
        self.painter = TiledBarPainter(self._maxValue)
        self.barMargin = 0
        super(TiledBar, self).__init__(parent)
    
    def minimumSizeHint(self):
        return self.painter.minimumSizeHint(self.font())
    
    def sizeHint(self):
        return self.minimumSizeHint()
        
    def paintEvent(self, event=None):
        painter = QPainter(self)
        self.painter.paintEvent(painter, self.rect(), event,0.0)
        
    def addValue(self, val, col):
        self.painter.addValue(val,col)
        self.update()
    
    def setValue(self, index, val):
        self.painter.setValue(index, val)
        self.update()
    
    def setColor(self, index, col):
        self.painter.setColor(index, col)
        self.update()
    
    def getMaxValue(self):
        return self._maxValue
    
    @pyqtSlot(int)
    def setMaxValue(self, value):
        self.painter.setMaxValue(value)
        self.update()
    
    maxValue = property(getMaxValue,setMaxValue)


class Ruler(QWidget):
    def __init__(self, maxValue=100, parent=None):
        super(Ruler, self).__init__(parent)
        self.ruler = RulerPainter(maxValue)
        
        self.setFont(self.ruler.getFont())
        
    def minimumSizeHint(self):
        return self.ruler.minimumSizeHint()
    
    def sizeHint(self):
        return self.minimumSizeHint()
    
    def paintEvent(self, event=None):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        self.ruler.paintEvent(painter, self.rect(), event, 0.0)
    
    def getMaxValue(self):
        return self._maxValue
    
    def setMaxValue(self, value):
        self.ruler.setMaxValue(value)
        self.update()
    
    maxValue = property(getMaxValue,setMaxValue)

class TiledBarRulered(QWidget):
    def __init__(self, maxValue=100, parent=None):
        super(TiledBarRulered, self).__init__(parent)
        self.ruler = RulerPainter(maxValue)
        self.ruler.scaleOrientation = Qt.LeftToRight
        self.setFont(self.ruler.getFont())
        self.bar = TiledBarPainter(maxValue)
    
    def minimumSizeHint(self):
        rulerSize = self.ruler.minimumSizeHint()
        barSize = self.bar.minimumSizeHint(self.font())
        return self.ruler.minimumSizeHint()
    
    def sizeHint(self):
        return self.minimumSizeHint()
    
    def getMaxValue(self):
        return self.ruler.getMaxValue()
    
    @pyqtSlot(int)
    def setMaxValue(self, value):
        self.ruler.setMaxValue(value)
        self.bar.setMaxValue(value)
        self.update()
    
    def paintEvent(self, event=None):
        painter = QPainter(self)
        #height = self.ruler.getRulerHeight(self.height())
        positions = self.ruler.getPositions(self.rect())
        #print height
        barRect = QRectF(positions['line'].x1(),positions['line'].y1(),
                         self.width(),
                         positions['line'].y2()-positions['line'].y1())
        #painter.fillRect(barRect, Qt.white)
        #print barRect
        
        
        self.bar.paintEvent(painter, barRect, event,0.0)
        painter.setBrush(self.palette().foreground())
        painter.setPen(self.palette().color(QPalette.Foreground))
        self.ruler.paintEvent(painter, self.rect(), event,0.0)
        
    def addValue(self, val, col):
        self.bar.addValue(val,col)
        self.update()
    
    def setValue(self, index, val):
        self.bar.setValue(index, val)
        self.update()
    
    def setColor(self, index, col):
        self.bar.setColor(index, col)
        self.update()
    
    maxValue = property(getMaxValue,setMaxValue)
    
    def getSubDivisionCount(self):
        return self.ruler.subDivisionCount
    
    def setSubDivisionCount(self, count):
        self.ruler.subDivisionCount = count
        
    subDivisionCount = property(getSubDivisionCount,setSubDivisionCount)
    
        
