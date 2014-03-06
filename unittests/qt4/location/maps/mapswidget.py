'''
Created on 29.10.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSignal, QPropertyAnimation, Qt, QPointF,\
    QAbstractAnimation, QRectF, QTimer, SLOT, pyqtSlot, QParallelAnimationGroup,\
    QSizeF, pyqtProperty, QObject, QString
from PyQt4.QtGui import QGraphicsRectItem, QGraphicsSimpleTextItem, QPen,\
    QBrush, QColor, QFont, QGraphicsView, QWidget, QGraphicsScene

from ems.qt4.location.maps.graphicsgeomap import GraphicsGeoMap #@UnresolvedImport
from ems.qt4.location.maps.geomappingmanager import GeoMappingManager #@UnresolvedImport
from ems.qt4.location.maps.geomapobject import GeoMapObject #@UnresolvedImport
from ems.qt4.location.geocoordinate import GeoCoordinate #@UnresolvedImport
from marker import Marker #@UnresolvedImport
from ems.qt4.location.maps.geomaprouteobject import GeoMapRouteObject

class GeoMap(GraphicsGeoMap):
#    centerLatitude = 0.0
#    centerLongitude = 0.0
    
    clicked = pyqtSignal(Marker)
    panned = pyqtSignal()
    
    def __init__(self, manager, mapsWidget):
        self.mapsWidget = mapsWidget
        #super(GeoMap, self).__init__(manager, mapsWidget)
        GraphicsGeoMap.__init__(self, manager)
        self.panActive = False
        self._markerPressed = False
        self.pressed = None
        self._clickedWithoutMove = False
        self._animTest = 8.5658544302
    
    
    def getCenterLatitude(self):
        return self.center().latitude()
    
    
    def setCenterLatitude(self, latitude):
        #print "lat:{0}".format(latitude)
        center = self.center() 
        center.setLatitude(latitude)
        self.setCenter(center)
    
    centerLatitude = pyqtProperty(float, getCenterLatitude, setCenterLatitude)
    
    
    def getCenterLongitude(self):
        #return self._animTest
        return self.center().longitude()
    
    def setCenterLongitude(self, longitude):
        #print "lon: {0}".format(longitude)
        #self._animTest = longitude
        #return
#        center = GeoCoordinate(self.center())
        center = self.center()
        center.setLongitude(longitude)
        self.setCenter(center)
    
    centerLongitude = pyqtProperty(float, getCenterLongitude, setCenterLongitude)
    
    def mousePressEvent(self, event):
        self.panActive = True
        self._markerPressed = False
        self._clickedWithoutMove = True
        objects = self.mapObjectsAtScreenPosition(event.pos())
        #print self.screenPositionToCoordinate(QPointF(event.pos())), event.pos()
        if len(objects) > 0:
            if isinstance(objects[0], Marker):
                self.pressed = objects[0]
                self._markerPressed = True
                self.panActive = False
            elif isinstance(objects[0], GeoMapRouteObject):
                pass
            
        self.setFocus()
        event.accept()
        
    
    def mouseReleaseEvent(self, event):
        self.panActive = False
        
        if self._markerPressed:
            objects = self.mapObjectsAtScreenPosition(event.pos())
            if self.pressed in objects:
                self.clicked.emit(self.pressed)
        
            self._markerPressed = False
        elif self._clickedWithoutMove:
            #print "screenPos: {0}".format(event.pos())
            coord = self.screenPositionToCoordinate(QPointF(event.pos()))
            coordStr = str(coord)
            #print "Coordinate: {0}".format(coordStr)
            #print "Back to ScreenPos: {0}".format(self.coordinateToScreenPosition(coord))
            #print coordStr
            self.mapsWidget.statusBarItem.showText(coordStr)
            
        
        self.setFocus()
        event.accept()
    
    def mouseMoveEvent(self, event):
        self._clickedWithoutMove = False
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
            self.anim = QPropertyAnimation(self, 'centerLongitude') 
            self.anim.setEndValue(center.longitude())
            self.anim.setDuration(200)
            self.anim.start(QAbstractAnimation.DeleteWhenStopped)
        
        elif eventKey in (Qt.Key_6, Qt.Key_Right):
            center = self.screenPositionToCoordinate(QPointF(width/2.0 + width/5.0,
                                                             height/2.0))
            self.anim = QPropertyAnimation(self, 'centerLongitude')
            self.anim.setEndValue(center.longitude())
            self.anim.setDuration(200)
            self.anim.start(QAbstractAnimation.DeleteWhenStopped)
            
    
        elif eventKey in (Qt.Key_2, Qt.Key_Up):
            center = self.screenPositionToCoordinate(QPointF(width/2.0,
                                                             height/2.0 - height/5.0))
            self.anim = QPropertyAnimation(self, 'centerLatitude') 
            self.anim.setEndValue(center.latitude())
            self.anim.setDuration(200)
            self.anim.start(QAbstractAnimation.DeleteWhenStopped)
            
        
        elif eventKey in (Qt.Key_8, Qt.Key_Down):
            center = self.screenPositionToCoordinate(QPointF(width/2.0,
                                                             height/2.0 + height/5.0))
            self.anim = QPropertyAnimation(self, 'centerLatitude') 
            self.anim.setEndValue(center.latitude())
            self.anim.setDuration(200)
            self.anim.start(QAbstractAnimation.DeleteWhenStopped)
            
            
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
        
        x = float(x)
        y = float(y)
        w = float(w)
        h = float(h)
        
        f = QFont()
        #f.setFamily("Monospace")
        f.setFixedPitch(True)
        f.setPixelSize(w+0.2)
        self.plusText.setFont(f)
        self.minusText.setFont(f)
        
        plusBound = self.plusText.boundingRect()
        plusCenter = QPointF(x+w/2.0, y+h/4.0)
        plusDelta = plusCenter - plusBound.center()
        self.plusText.setPos(plusDelta)
        #print "plus:", plusDelta
        
        minusBound = self.minusText.boundingRect()
        minusCenter = QPointF(x+w/2.0, y+(2.0*h/4.0))
        minusDelta = minusCenter - minusBound.center()
        self.minusText.setPos(minusDelta)
        #print "minus:",minusDelta
        
    
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
                      self.rect().width(), self.rect().height()/2).contains(point)
    
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
    
class StatusBarNotifier(QObject):
    def __init__(self, statusBarItem):
        QObject.__init__(self, None)
        self._offset = 0
        self.item = statusBarItem
        
    def getOffset(self):
        return self._offset
    
    def setOffset(self, offset):
        self._offset = offset
        self.item.setOffset(self._offset)
    
    offset = pyqtProperty(int, getOffset, setOffset)
    
    @pyqtSlot()
    def hide(self):
        self.item.hide()
    
    
class StatusBarItem(QGraphicsRectItem):
    def __init__(self, parent=None):
        
        QGraphicsRectItem.__init__(self, parent)
        
        self._offsetNotifier = StatusBarNotifier(self)
        self._offset = 0
        
        self.setPen(QPen(QBrush(),0))
        self.setBrush(QBrush(QColor(0,0,0,120)))
        
        self.textItem = QGraphicsSimpleTextItem(self)
        self.textItem.setBrush(QBrush(Qt.white))
        
        #self.setText("Hallo")
    
    def setText(self, text):
        text = QString.fromUtf8(text)
        self.textItem.setText(text)
        rect = self.textItem.boundingRect()
        delta = self.rect().center() - rect.center()
        self.textItem.setPos(delta.x(), delta.y())
    
    def getOffset(self):
        return self._offset
    
    def setRect(self, x, y, w, h):
        QGraphicsRectItem.setRect(self, x, y + self._offset, w, h)
        self.setText(self.textItem.text())
    
    def setOffset(self, offset):
        self.setY(self.y() - self._offset + offset)
        self._offset = offset
    
    offset = pyqtProperty(int, getOffset, setOffset)
    
    def showText(self, text, timeout=3000):
        self.setText(text)
        self.show()
        QTimer.singleShot(timeout, self._offsetNotifier, SLOT('hide()'))
    
    @pyqtSlot()
    def show(self):
        self.anim = QPropertyAnimation(self._offsetNotifier, "offset")
        #anim.setPropertyName("offset")
        
        self.anim.setStartValue(0)
        self.anim.setEndValue(-1 * self.rect().height())
        self.anim.setDuration(500)
        self.anim.start(QAbstractAnimation.DeleteWhenStopped)
    
    @pyqtSlot()
    def hide(self):
        self.anim = QPropertyAnimation(self._offsetNotifier, "offset")
        self.anim.setStartValue(self._offsetNotifier._offset)
        self.anim.setEndValue(0)
        self.anim.setDuration(500)
        self.anim.start(QAbstractAnimation.DeleteWhenStopped)
    
    
class FixedGraphicsView(QGraphicsView):
    def scrollContentsBy(self, dx, dy):
        pass

class MapsWidget(QWidget):
    
    markerClicked = pyqtSignal(Marker)
    
    mapPanned = pyqtSignal()
    
    def __init__(self, initCoordinate=None, parent=None):
        QWidget.__init__(self, parent)
        self._map = None
        self.view = None
        #self.markerManager = None
        self.statusBarItem = None
        self.zoomButtonItem = None
        self._markerManager = None
        if initCoordinate is None:
            initCoordinate = GeoCoordinate(48.525759, 8.5659)
        self._initCoordinate = initCoordinate
    
    def initialize(self, manager):
        self._map = GeoMap(manager, self)
        if self._markerManager:
            self._markerManager.setMap(map)
        
        self._map.clicked.connect(self.markerClicked)
        self._map.panned.connect(self.mapPanned)
        
        sc = QGraphicsScene()
        sc.addItem(self._map)
        
        
        self._map.setPos(0.0,0.0)
        self._map.resize(QSizeF(self.size()))
        self.view = FixedGraphicsView(self)
        self.view.setVisible(True)
        self.view.setInteractive(True)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setScene(sc)
#        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        self.statusBarItem = StatusBarItem()
        sc.addItem(self.statusBarItem)
        
        self.zoomButtonItem = ZoomButtonItem(self._map)
        #sc.addItem(self.zoomButtonItem)
        
        
        self.view.resize(self.size())
        self.view.centerOn(self._map)
        self.resizeEvent(None)
        self._map.centerChanged.connect(self.onCenterChanged)
        #self.map.setCenter(GeoCoordinate(-27.5796, 153.1))
        #self.map.setCenter(GeoCoordinate(48.31321, 8.33554))
        self._map.setCenter(self._initCoordinate)
        #48.525759,8.5659
        #self.map.setCenter(GeoCoordinate(21.1813, -86.8455))
        self._map.setZoomLevel(15.0)
        #self.statusBarItem.setText("Hallo was geht")
    
    def resizeEvent(self, event):
        if self.view and self._map:
            self.view.resize(self.size())
            self._map.resize(self.width()-2, self.height()-2)
            self.view.centerOn(self._map)
            self.statusBarItem.setRect(0, self.height()-2, self.width()-2, 20.0)
            self.zoomButtonItem.setRect((self.width()-2.0)-(self.width()-2.0)/10.0,
                                        (self.height()-2.0)/2.0 - (self.height()-2.0)/6.0,
                                        (self.width()-2.0)/10.0,
                                        (self.height()-2.0/3.0))
    
    def onCenterChanged(self, coord):
        #print coord
        pass
        
    def animatedPanTo(self, center):
        if not self._map:
            return
        self.latAnim = QPropertyAnimation(self._map, "centerLatitude")
        self.latAnim.setEndValue(center.latitude())
        self.latAnim.setDuration(200)
        
        self.lonAnim = QPropertyAnimation(self._map, "centerLongitude")
        self.lonAnim.setEndValue(center.longitude())
        self.lonAnim.setDuration(200)
        
        self.group = QParallelAnimationGroup()
        self.group.addAnimation(self.latAnim)
        self.group.addAnimation(self.lonAnim)
        self.group.start(QAbstractAnimation.DeleteWhenStopped)
    
    def showEvent(self, even):
        self.resizeEvent(None)
    
    def setMyLocation(self, location, center=True):
        if self._markerManager:
            self._markerManager.setMyLocation(location)
        if self._map and center:
            self._map.setCenter(location)
    
    def map_(self):
        return self._map
    
    def statusBar(self):
        return self.statusBarItem
    
    def markerManager(self):
        return self._markerManager
    
    def setMarkerManager(self, markerManager):
        self._markerManager = markerManager
        if self._map:
            self._markerManager.setMap(self._map)
    
    
        
        