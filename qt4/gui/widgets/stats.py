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
    def __init__(self, maxValue=100, subDivisionCount=10, parent=None):
        super(TiledBarRulered, self).__init__(parent)
        self.ruler = RulerPainter(maxValue,subDivisionCount)
        self.ruler.scaleOrientation = Qt.LeftToRight
        self.setFont(self.ruler.getFont())
        self.bar = TiledBarPainter(maxValue)
    
    def minimumSizeHint(self):
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
        painter.fillRect(self.rect(), Qt.white)
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
    
class MultiBarRulered(QWidget):
    def __init__(self, maxValue=100, subDivisionCount=10, parent=None):
        super(MultiBarRulered, self).__init__(parent)
        self.ruler = RulerPainter(maxValue,subDivisionCount)
        self.ruler.scaleOrientation = Qt.LeftToRight
        self.setFont(self.ruler.getFont())
        self.bar = TiledBarPainter(maxValue)
        self.bars = [TiledBarPainter(maxValue),
                     TiledBarPainter(maxValue),
                     TiledBarPainter(maxValue)]
    
    def minimumSizeHint(self):
#        rulerSize = self.ruler.minimumSizeHint()
#        barSize = self.bar.minimumSizeHint(self.font())
#        width = rulerSize.width() + (barSize.width())
        return QSize(220,140)
    
    def sizeHint(self):
        return self.minimumSizeHint()
    
    def getMaxValue(self):
        return self.ruler.getMaxValue()
    
    @pyqtSlot(int)
    def setMaxValue(self, value):
        self.ruler.setMaxValue(value)
        calcValue = self.ruler.getMaxValue()
        for bar in self.bars:
            bar.setMaxValue(calcValue)
        self.update()
    
    def paintEvent(self, event=None):
        painter = QPainter(self)
        #painter.fillRect(self.rect(), Qt.white)
        #height = self.ruler.getRulerHeight(self.height())
        positions = self.ruler.getPositions(self.rect())
        #print height
        barRect = QRectF(positions['line'].x1(),positions['line'].y1(),
                         self.width(),
                         positions['line'].y2()-positions['line'].y1())
            
        painter.drawLine(QLineF(positions['line'].x1(),
                                positions['line'].y2(),
                                self.width(),
                                positions['line'].y2()))

        oneValueWidth = float(self.width()-positions['line'].x1())/3
        oneValueWidthH = oneValueWidth/2.0
        
        #painter.fillRect(barRect, Qt.white)
        
        #print oneValueWidth
        middlePositions = []
        x = positions['line'].x1()
        textPositions = []
        barPositions = []
        
        for i in range(3):
            middlePositions.append(x+oneValueWidthH)
#            painter.drawLine(QLineF(x,
#                                positions['line'].y2()+10.0,
#                                x,
#                                positions['line'].y2()))
            textPositions.append(QRectF(x,positions['line'].y2()-5.0,
                                        oneValueWidth,
                                        22.0))
            barPositions.append(QRectF(x,
                                       barRect.y(),
                                       oneValueWidth,
                                       barRect.height()))
            
            x += oneValueWidth
        labels = ('Verlust','Erzeugung','Einsatz')
        i=0
        for rect in textPositions:
            #painter.fillRect(rect, Qt.red)
            painter.drawText(rect, Qt.AlignCenter,labels[i])
            i +=1
        
        
        #print barRect
        
        #self.bar.paintEvent(painter, barRect, event,0.0)
        for i in range(3):
            self.bars[i].paintEvent(painter, barPositions[i], event,0.0)
        
        
        painter.setBrush(self.palette().foreground())
        painter.setPen(self.palette().color(QPalette.Foreground))
        self.ruler.paintEvent(painter, self.rect(), event,0.0)
        
    def addValue(self, barIdx, val, col):
        self.bars[barIdx].addValue(val,col)
        self.update()
    
    def setValue(self, barIdx, index, val):
        self.bars[barIdx].setValue(index, val)
        self.update()
    
    def setColor(self, barIdx, index, col):
        self.bars[barIdx].setColor(index, col)
        self.update()
    
    maxValue = property(getMaxValue,setMaxValue)
    
    def getSubDivisionCount(self):
        return self.ruler.subDivisionCount
    
    def setSubDivisionCount(self, count):
        self.ruler.subDivisionCount = count
        
    subDivisionCount = property(getSubDivisionCount,setSubDivisionCount)
