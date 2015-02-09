'''
Created on 18.05.2011

@author: michi
'''

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from ems.math import ceilInt #@UnresolvedImport

class RulerPainter(object):
    
    scaleSide = 1
    nonScaleSide = 2
    
    def __init__(self, maxValue=100, subDivisionCount=10, font=None,
                 autoCeilMaxValue=True):
        self._subDivisions = []
        self._orientation = Qt.Horizontal
        self.textOrientation = self.nonScaleSide
        self.subDivisionCount = subDivisionCount
        self.autoCeilMaxValue = autoCeilMaxValue
        #self.textOrientation = self.scaleSide
        #self.scaleOrientation = Qt.LeftToRight
        self.scaleOrientation = Qt.RightToLeft
        self.maxValue = maxValue
        self.divisionWidth = 10.0
        self.textLineMargin = 2.0
        if font is None:
            font = self.getDefaultFont()
        self.setFont(font)
            
    def getDefaultFont(self):
#        font = QFont("Monospace")
#        font.setStyleHint(font.TypeWriter)
        font = QApplication.font()
        font.setPointSize(QApplication.font().pointSize()-2)
        return font
#        self.font().setPointSize(self.font().pointSize())
    def getFont(self):
        return self._font
    
    def setFont(self, font):
        self._font = font
        self._recalculateFontMetrics()
        
    
    def _recalculateFontMetrics(self):
        font = QFont(self._font)
        font.setPointSize(font.pointSize())
        fm = QFontMetricsF(font)
        self.fontHeight = fm.height()
        self.fontHeightH = self.fontHeight/2 
        self.maxFontWidth = fm.width(str(self._maxValue))
        
    def minimumSizeHint(self):
        font = QFont(self._font)
        font.setPointSize(font.pointSize())
        fm = QFontMetricsF(font)
        strMaxValue = str(self._maxValue)
        minWidth = fm.width(strMaxValue)+self.divisionWidth+self.textLineMargin
        minHeight = (len(self._subDivisions)+1) * fm.height()
        return QSize(minWidth,minHeight)
    
    def getRulerHeight(self, widgetHeight):
        return widgetHeight-self.fontHeight
    
    def getPositions(self, clipRect, leftOffset=0.0):
        positions = {'line':None,'text':None}
        
        if self.textOrientation == self.scaleSide:
            if self.scaleOrientation == Qt.LeftToRight:#1
                textLeftPos = self.divisionWidth + self.textLineMargin + leftOffset
                lineLeftPos = leftOffset
            else:#2
                textLeftPos = leftOffset
                lineLeftPos = self.divisionWidth + self.textLineMargin + leftOffset
                
        else:
            if self.scaleOrientation == Qt.LeftToRight:#3
                textLeftPos = leftOffset
                lineLeftPos = self.maxFontWidth + self.textLineMargin + leftOffset
            else:#4
                textLeftPos = self.divisionWidth + self.textLineMargin + leftOffset
                lineLeftPos = leftOffset
            
        lineRightPos = lineLeftPos + self.divisionWidth
        
        if self.scaleOrientation == Qt.LeftToRight:
            positions['line'] = QLineF(lineLeftPos, self.fontHeightH,
                                       lineLeftPos,
                                       self.getRulerHeight(clipRect.height())) 
        else:
            positions['line'] = QLineF(lineRightPos, self.fontHeightH,
                                       lineRightPos,
                                       self.getRulerHeight(clipRect.height()))
        positions['text'] = QPointF(textLeftPos,0.0)
        positions['lineLeftPos'] = lineLeftPos
        positions['lineRightPos'] = lineLeftPos + self.divisionWidth
        return positions
        
    def paintEvent(self, painter, clipRect, event=None, leftOffset=0.0):
        
        
        positions = self.getPositions(clipRect, leftOffset)
        
        textLeftPos = positions['text'].x()
        lineLeftPos = positions['lineLeftPos']
        
        lineRightPos = positions['lineRightPos']
        
        rulerHeight = positions['line'].y2()
        
        singlePoint = rulerHeight/len(self._subDivisions)
        
        startY = rulerHeight
        
        #print positions['line']
        
        drawMiniDivisions = False
        miniDivisionsRightPos = 0.0
        if singlePoint > 18.0:
            drawMiniDivisions = True
            if self.scaleOrientation == Qt.LeftToRight:
                miniDivisionsLeftPos = lineLeftPos
                miniDivisionsRightPos = lineRightPos - (self.divisionWidth/2)
            else:
                miniDivisionsLeftPos = lineLeftPos + (self.divisionWidth/2)
                miniDivisionsRightPos = lineRightPos
        
        #ruler line
        painter.drawLine(positions['line'])
        
        
        #painter.drawLine(QLineF(0.0, startY-1.0,self.divisionWidth,startY-1.0))
        if self.textOrientation == self.scaleSide:
            if self.scaleOrientation == Qt.LeftToRight:
                align = Qt.AlignLeft
            else:
                align = Qt.AlignRight
        else:
            if self.scaleOrientation == Qt.LeftToRight:
                align = Qt.AlignRight
            else:
                align = Qt.AlignLeft
            
        for division in self._subDivisions:
            painter.drawLine(QLineF(lineLeftPos, startY,lineRightPos,startY))
            
            fontRect = QRectF(textLeftPos, startY-self.fontHeightH,
                             self.maxFontWidth, self.fontHeight)
            
            painter.drawText(fontRect, align, str(division))
            #painter.fillRect(fontRect,Qt.SolidPattern)
            
            if drawMiniDivisions:
                startYDiv = startY-(singlePoint/2)
                painter.drawLine(QLineF(miniDivisionsLeftPos, startYDiv,
                                        miniDivisionsRightPos, startYDiv))
            
            startY -= singlePoint
            
        painter.drawLine(QLineF(lineLeftPos, self.fontHeightH,lineRightPos,
                                self.fontHeightH))
        
        fontRect = QRectF(textLeftPos, 0.0, self.maxFontWidth, self.fontHeight)
        
        
        painter.drawText(fontRect, align, str(self._maxValue))
        #RulerMixin.paint(self, painter, event, 20.0, 20.0)
        #painter.fillRect(fontRect,Qt.SolidPattern)
    
    def getMaxValue(self):
        return self._maxValue
    
    def ceilMaxValue(self, value):
        strVal = str(value)
        zeros = len(strVal)-1
        if (value % (10**zeros)) == 0:
            return value
            
        else:
            return ceilInt(value,zeros)
        
    
    def setMaxValue(self, value):
        if self.autoCeilMaxValue:
            value = self.ceilMaxValue(value)
        self._maxValue = value
        singleVal = int(self._maxValue/self.subDivisionCount)
        self._subDivisions = []
        for val in range(0,self._maxValue,singleVal):
            self._subDivisions.append(val)
    
    maxValue = property(getMaxValue,setMaxValue)

class TiledBarPainter(object):
    WSTRING = '999'
    def __init__(self, maxValue = 100, font=None):
        self._maxValue = maxValue
        self.barMargin = 0.0
        self._values = []
    
    def minimumSizeHint(self, font):
        font.setPointSize(font.pointSize() - 1)
        fm = QFontMetricsF(font)
        return QSize(fm.width(TiledBarPainter.WSTRING),100)
        
    def paintEvent(self, painter, clipRect, event=None, leftOffset=0.0):
        
        rectBorder = 0
        rectBorderD = rectBorder+rectBorder
        barMarginD = self.barMargin+self.barMargin
        pixelVal = (clipRect.height()-(barMarginD))/self._maxValue
        barWidth = clipRect.width()-(barMarginD)-rectBorderD
        
        startY = (clipRect.height()+clipRect.y()) - self.barMargin
        currentY = startY
        
        #print painter.pen().setWidth(3)
        x = self.barMargin + rectBorder + clipRect.x()
        
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
    
    def setValue(self, index, val):
        self._values[index]['val'] = val
    
    def setColor(self, index, col):
        self._values[index]['col'] = col
    
    def getMaxValue(self):
        return self._maxValue
    
    def setMaxValue(self, value):
        self._maxValue = value
    
    maxValue = property(getMaxValue,setMaxValue)

