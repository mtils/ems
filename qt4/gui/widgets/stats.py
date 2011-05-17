'''
Created on 17.05.2011

@author: michi
'''
from __future__ import division
import platform
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class TiledBar(QWidget):
    WSTRING = '999'
    def __init__(self, parent=None):
        self._maxValue = 100
        self._orientation = Qt.Horizontal
        self.barMargin = 0
        self._values = []
        super(TiledBar, self).__init__(parent)
    
    def minimumSizeHint(self):
        font = QFont(self.font())
        font.setPointSize(font.pointSize() - 1)
        fm = QFontMetricsF(font)
        return QSize(fm.width(TiledBar.WSTRING),100)
    
    def sizeHint(self):
        return self.minimumSizeHint()
        
    def paintEvent(self, event=None):
        painter = QPainter(self)
        painter.setPen(self.palette().color(QPalette.Mid))
        painter.setBrush(self.palette().brush(QPalette.AlternateBase))
        painter.drawRect(self.rect())
        
        rectBorder = 0
        rectBorderD = rectBorder+rectBorder
        barMarginD = self.barMargin+self.barMargin
        pixelVal = (self.height()-(barMarginD))/self._maxValue
        barWidth = self.width()-(barMarginD)-rectBorderD
        
        startY = self.height() - self.barMargin
        currentY = startY
        
        #print painter.pen().setWidth(3)
        x = self.barMargin + rectBorder
        for value in self._values:
            if value <= 0:
                continue
            segLineColor = value['col'].dark()
            painter.setPen(segLineColor)
            painter.setBrush(value['col'])
            
            rectHeight = value['val']*pixelVal
            
            rect = QRectF(x,currentY-rectHeight,
                             barWidth,
                             (rectHeight)-rectBorderD)
            painter.fillRect(rect,painter.brush())
            currentY -= rectHeight
            
        
    def addValue(self, val, col):
        self._values.append({'val':val,'col':col})
        self.update()
    
    def setValue(self, index, val):
        self._values[index]['val'] = val
        self.update()
    
    def setColor(self, index, col):
        self._values[index]['col'] = col
        self.update()
    
    def getMaxValue(self):
        return self._maxValue
    
    @pyqtSlot(int)
    def setMaxValue(self, value):
        self._maxValue = value
        self.update()
    
    maxValue = property(getMaxValue,setMaxValue)