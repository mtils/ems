'''
Created on 29.10.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSignal, QPropertyAnimation, Qt, QPointF,\
    QAbstractAnimation, QRectF, QTimer, SLOT, pyqtSlot, QParallelAnimationGroup
from PyQt4.QtGui import QGraphicsRectItem, QGraphicsSimpleTextItem, QPen,\
    QBrush, QColor, QFont, QGraphicsView, QWidget, QGraphicsScene

from lib.ems.qt4.location.maps.graphicsgeomap import GraphicsGeoMap
from lib.ems.qt4.location.maps.geomappingmanager import GeoMappingManager
from lib.ems.qt4.location.maps.geomapobject import GeoMapObject
from lib.ems.qt4.location.geocoordinate import GeoCoordinate
from marker import Marker #@UnresolvedImport

class GeoMap(GraphicsGeoMap):
    centerLatitude = 0.0
    centerLongitude = 0.0
    
    clicked = pyqtSignal(Marker)
    panned = pyqtSignal()
    
    def __init__(self, manager, mapsWidget):
        self.mapsWidget = mapsWidget
        super(GeoMap, self).__init__(manager, mapsWidget)
        self.panActive = False
        self._markerPressed = False
        self.pressed = None
    
    def centerLatitude(self):
        return self.center().latitude()
    
    def centerLongitude(self):
        return self.center().longitude()
    
    def setCenterLatitude(self, latitude):
        self.center().setLatitude(latitude)
        self.setCenter(self.center())
    
    def setCenterLongitude(self, longitude):
        self.center().setLongitude(longitude)
        self.setCenter(self.center())
    
    def mousePressEvent(self, event):
        self.panActive = True
        self._markerPressed = False
        objects = self.mapObjectsAtScreenPosition(event.pos())
        if len(objects) > 0:
            self.pressed = objects[0]
            self._markerPressed = True
        self.setFocus()
        event.accept()
    
    def mouseReleaseEvent(self, event):
        self.panActive = False
        if self._markerPressed:
            objects = self.mapObjectsAtScreenPosition(event.pos())
            if self.pressed in objects:
                self.clicked.emit(self.pressed)
        
            self._markerPressed = False
        self.setFocus()
        event.accept()
    
    def mouseMoveEvent(self, event):
        if self.panActive:
            delta = event.lastPos() - event.pos()
            self.pan(delta.x(), delta.y())
            self.panned.emit()
        self.setFocus()
        event.accept()
    
    def wheelEvent(self, event):
        panX = event.pos().x() - self.size().width()/2.0
        panY = event.pos().y() - self.size().height()/2.0
        self.pan(panX, panY)
        
        if event.delta() > 0: #zoom in
            if self.zoomLevel() < self.maximumZoomLevel():
                self.setZoomLevel(self.zoomLevel() + 1)
            
        else:
            if self.zoomLevel() > self.minimumZoomLevel():
                self.setZoomLevel(self.zoomLevel() - 1)
        
        self.pan(-panX, -panY)
        self.setFocus()
        event.accept()
    
    def keyPressEvent(self, event):
        
        width = self.size().width()
        height = self.size().height()
         
        eventKey = event.key()
        
        if eventKey in (Qt.Key_4, Qt.Key_Left):
            center = self.screenPositionToCoordinate(QPointF(width/2.0 - width/5.0,
                                                             height/2.0))
            anim = QPropertyAnimation(self, 'centerLongitude') 
            anim.setEndValue(center.longitude())
            anim.setDuration(200)
            anim.start(QAbstractAnimation.DeleteWhenStopped)
        
        elif eventKey in (Qt.Key_6, Qt.Key_Right):
            center = self.screenPositionToCoordinate(QPointF(width/2.0 + width/5.0,
                                                             height/2.0))
            anim = QPropertyAnimation(self, 'centerLongitude') 
            anim.setEndValue(center.longitude())
            anim.setDuration(200)
            anim.start(QAbstractAnimation.DeleteWhenStopped)
    
        elif eventKey in (Qt.Key_2, Qt.Key_Up):
            center = self.screenPositionToCoordinate(QPointF(width/2.0,
                                                             height/2.0 - height/5.0))
            anim = QPropertyAnimation(self, 'centerLatitude') 
            anim.setEndValue(center.latitude())
            anim.setDuration(200)
            anim.start(QAbstractAnimation.DeleteWhenStopped)
        
        elif eventKey in (Qt.Key_8, Qt.Key_Down):
            center = self.screenPositionToCoordinate(QPointF(width/2.0,
                                                             height/2.0 + height/5.0))
            anim = QPropertyAnimation(self, 'centerLatitude') 
            anim.setEndValue(center.latitude())
            anim.setDuration(200)
            anim.start(QAbstractAnimation.DeleteWhenStopped)
            
        elif eventKey == Qt.Key_1:
            if self.zoomLevel() > self.minimumZoomLevel():
                self.setZoomLevel(self.zoomLevel() - 1)
        
        elif eventKey == Qt.Key_3:
            if self.zoomLevel() < self.maximumZoomLevel():
                self.setZoomLevel(self.zoomLevel() + 1)
        
        self.setFocus()
        event.accept()

class ZoomButtonItem(QGraphicsRectItem):
    
    def __init__(self, geoMap):
        QGraphicsRectItem.__init__(self, geoMap)
        self.map = geoMap
        
        self.pressedOverBottomHalf = False
        self.pressedOverTopHalf = False
        
        self.setPen(QPen(QBrush(), 0))
        self.setBrush(QBrush(QColor(0,0,0,150)))
        
        self.plusText = QGraphicsSimpleTextItem(self)
        self.plusText.setText("+")
        self.plusText.setBrush(QBrush(Qt.white))
        
        self.minusText = QGraphicsSimpleTextItem(self)
        self.minusText.setText('-')
        self.minusText.setBrush(QBrush(Qt.white))
    
    def setRect(self, x, y, w, h):
        QGraphicsRectItem.setRect(self, x, y, w, h)
        
        f = QFont()
        f.setFixedPitch(True)
        f.setPixelSize(h/5.0)
        self.plusText.setFont(f)
        self.minusText.setFont(f)
        
        plusBound = self.plusText.boundingRect()
        plusCenter = QPointF(x+w/2.0, y+h/4.0)
        plusDelta = plusCenter - plusBound.center()
        self.plusText.setPos(plusDelta)
        
        minusBound = self.minusText.boundingRect()
        minusCenter = QPointF(x+w/2.0, y+3.0*h/4.0)
        minusDelta = minusCenter - minusBound.center()
        self.minusText.setPos(minusDelta)
        
    
    def mousePressEvent(self, event):
        pos = event.pos()
        if not self.pressedOverTopHalf and not self.pressedOverBottomHalf:
            if self.isTopHalf(pos):
                self.pressedOverTopHalf = True
            elif self.isBottomHalf(pos):
                self.pressedOverBottomHalf = True
        
        self.map.setFocus()
        event.accept()
    
    def isTopHalf(self, point):
        return QRectF(self.rect().x(), self.rect().y(),
                      self.width(), self.rect().height()/2).contains(point)
    
    def isBottomHalf(self, point):
        return QRectF(self.rect().x(), self.rect().y() + self.rect().height()/2.0,
                      self.rect().width(), self.rect().height()/2.0).contains(point)
    
    def mouseReleaseEvent(self, event):
        pos = event.pos()
        if self.isTopHalf(pos) and self.pressedOverTopHalf:
            self.map.setZoomLevel(self.map.zoomLevel() + 1.0)
        elif self.isBottomHalf(pos) and self.pressedOverBottomHalf:
            self.map.setZoomLevel(self.map.zoomLevel() - 1.0)
        
        self.pressedOverBottomHalf = False
        self.pressedOverTopHalf = False
        self.map.setFocus()
        event.accept()
    
    def mouseMoveEvent(self, event):
        event.accept()
    

class StatusBarItem(QGraphicsRectItem):
    def __init__(self, parent=None):
        QGraphicsRectItem.__init__(self, parent)
        self._offset = 0
        
        self.setPen(QPen(QBrush(),0))
        self.setBrush(QBrush(QColor(0,0,0,120)))
        
        self.textItem = QGraphicsSimpleTextItem(self)
        self.textItem.setBrush(QBrush(Qt.white))
        
        self.setText("")
    
    def setText(self, text):
        self.textItem.setText(text)
        rect = self.textItem.boundingRect()
        delta = self.rect().center() - rect.center()
        self.textItem.setPos(delta.x(), delta.y())
    
    def offset(self):
        return self._offset
    
    def setRect(self, x, y, w, h):
        QGraphicsRectItem.setRect(self, x, y + self._offset, w, h)
        self.setText(self.textItem.text())
    
    def setOffset(self, offset):
        self.setY(self.y() - self._offset + offset)
        self._offset = offset
    
    def showText(self, text, timeout):
        self.setText(text)
        self.show()
        QTimer.singleShot(timeout, self, SLOT('hide()'))
    
    @pyqtSlot()
    def show(self):
        anim = QPropertyAnimation(self, "offset")
        anim.setStartValue(0)
        anim.setEndValue(-1 * self.rect().height())
        anim.setDuration(500)
        anim.start(QAbstractAnimation.DeleteWhenStopped)
    
    @pyqtSlot()
    def hide(self):
        anim = QPropertyAnimation(self, "offset")
        anim.setStartValue(self._offset)
        anim.setEndValue(0)
        anim.setDuration(500)
        anim.start(QAbstractAnimation.DeleteWhenStopped)
    
    
class FixedGraphicsView(QGraphicsView):
    def scrollContentsBy(self, dx, dy):
        pass

class MapsWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.map = None
        self.view = None
        self.markerManager = None
        self.statusBarItem = None
        self.zoomButtonItem = None
    
    def initialize(self, manager):
        self.map = GeoMap(manager, self)
        if self.markerManager:
            self.markerManager.setMap(map)
        
        self.map.clicked.connect(self.markerClicked)
        self.map.panned.connect(self.mapPanned)
        
        sc = QGraphicsScene()
        sc.addItem(self.map)
        
        self.map.setPos(0.0,0.0)
        self.map.resize(self.size())
        self.view = FixedGraphicsView(self)
        self.view.setVisible(True)
        self.view.setInteractive(True)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setScene(sc)
        
        self.statusBarItem = StatusBarItem()
        sc.addItem(self.statusBarItem)
        
        self.view.resize(self.size())
        self.view.centerOn(self.map)
        self.resizeEvent(None)
        self.map.setCenter(GeoCoordinate(-27.5796, 153.1))
        self.map.setZoomLevel(15)
    
    def resizeEvent(self, event):
        if self.view and self.map:
            self.view.resize(self.size())
            self.map.resize(self.width()-2, self.height()-2)
            self.view.centerOn(self.map)
            self.statusBarItem.setRect(0, self.height()-2, self.width()-2, 20)
            self.zoomButtonItem.setRect((self.width()-2)-(self.width()-2)/10.0,
                                        (self.height()-2)/2.0 - (self.height()-2)/6.0,
                                        (self.width()-2)/10.0,
                                        (self.height()-2/3.0))
        
    def animatedPanTo(self, center):
        if not self.map:
            return
        latAnim = QPropertyAnimation(self.map, "centerLatitude")
        latAnim.setEndValue(center.latitude())
        latAnim.setDuration(200)
        
        lonAnim = QPropertyAnimation(self.map, "centerLongitude")
        lonAnim.setEndValue(center.longitude())
        lonAnim.setDuration(200)
        
        group = QParallelAnimationGroup()
        group.addAnimation(latAnim)
        group.addAnimation(lonAnim)
        group.start(QAbstractAnimation.DeleteWhenStopped)
    
    def showEvent(self, even):
        self.resizeEvent(None)
    
    
        
        