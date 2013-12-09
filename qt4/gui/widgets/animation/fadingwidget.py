'''
Created on 28.08.2012

@author: michi
'''
from PyQt4.QtCore import Qt, QTimeLine, QEasingCurve, QRect
from PyQt4.QtGui import QWidget, QPixmap, QPainter

class FadingWidget(QWidget):
    
    UP = 0
    DOWN = 1
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        if parent:
            self.startBrush = parent.palette().window()
        else:
            self.startBrush = Qt.black
        
        self.animationDirection = self.DOWN
        self.startBrush = Qt.black
        
#        self.timeLine = QTimeLine(333, self)
        self.timeLine = QTimeLine(666, self)
        self.timeLine.setUpdateInterval(20)
        self.timeLine.setEasingCurve(QEasingCurve.OutQuad)
#        self.timeLine = QTimeLine(1500, self)
        self.timeLine.setFrameRange(1000, 0)
        self.timeLine.frameChanged.connect(self.update)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.resize(parent.size())
        self.widgetPixmap = QPixmap.grabWidget(parent)
    
    def start(self):
        self.timeLine.start()
        self.show()
    
    def _doUpAnimation(self, painter, frame, event):
        myWidth = self.rect().width()
        myHeight = self.rect().height()
        
        targetRect = QRect(self.rect())
        targetRect.setHeight(int(myHeight*frame / 1000.0))
        lowerRect = QRect(0,targetRect.height()+1,
                          myWidth, myHeight-targetRect.height())
#        print self.widgetPixmap.rect()
        #sourceRect = self.widgetPixmap.rect().intersected(rect)
        sourceRect = QRect(0,lowerRect.height(),
                           myWidth, myHeight-lowerRect.height())
        #sourceRect = targetRect.intersected(self.widgetPixmap.rect())
        
        painter.setOpacity(frame / 1000.0)
        painter.fillRect(lowerRect, self.startBrush)
        painter.setOpacity(1.0)
        painter.drawPixmap(targetRect, self.widgetPixmap, sourceRect)
    
    def _doDownAnimation(self, painter, frame, event):
        myWidth = self.rect().width()
        myHeight = self.rect().height()
        
        targetRect = QRect(self.rect())
        frameFactor = frame / 1000.0
        targetRect.setHeight(int(myHeight*frameFactor))
        
        upperRect = QRect(0, 0, myWidth, myHeight-targetRect.height())
        targetRect.moveTopLeft(upperRect.bottomLeft())
#        print self.widgetPixmap.rect()
        #sourceRect = self.widgetPixmap.rect().intersected(rect)
        sourceRect = QRect(0,0,
                           myWidth, myHeight-upperRect.height())
        #sourceRect = targetRect.intersected(self.widgetPixmap.rect())
        
        painter.setOpacity(frame / 1000.0)
        painter.fillRect(upperRect, self.startBrush)
        painter.setOpacity(1.0)
        painter.drawPixmap(targetRect, self.widgetPixmap, sourceRect)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        frame = self.timeLine.currentFrame()
        
        #painter.setOpacity(frame / 1000.0)
        if self.animationDirection == self.UP:
            self._doUpAnimation(painter, frame, event)
        
        elif self.animationDirection == self.DOWN:
            self._doDownAnimation(painter, frame, event)
        
        
        if frame <= 0:
            self.close()