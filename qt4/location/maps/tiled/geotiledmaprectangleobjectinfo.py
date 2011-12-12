'''
Created on 02.11.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSlot, QPointF
from PyQt4.QtGui import QGraphicsPolygonItem, QPen, QBrush, QPolygonF

from geotiledmapobjectinfo import GeoTiledMapObjectInfo #@UnresolvedImport
from ems.qt4.location.geocoordinate import GeoCoordinate

class GeoTiledMapRectangleObjectInfo(GeoTiledMapObjectInfo):
    
    def __init__(self, mapData, mapObject):
        GeoTiledMapObjectInfo.__init__(self, mapData, mapObject)
        self.rectangle = mapObject
        self.rectangle.topLeftChanged.connect(self.topLeftChanged)
        self.rectangle.bottomRightChanged.connect(self.bottomRightChanged)
        self.rectangle.penChanged.connect(self.penChanged)
        self.rectangle.brushChanged.connect(self.brushChanged)
        
        self.polygonItem = QGraphicsPolygonItem()
        self.graphicsItem = self.polygonItem
        
        self.topLeftChanged(self.rectangle.topLeft())
        self.bottomRightChanged(self.rectangle.bottomRight())
        self.penChanged(self.rectangle.pen())
        self.brushChanged(self.rectangle.brush())
    
    @pyqtSlot(GeoCoordinate)
    def topLeftChanged(self, topLeft):
        self._regenPolygon()
        self.updateItem()
    
    @pyqtSlot(GeoCoordinate)
    def bottomRightChanged(self, bottomRight):
        self._regenPolygon()
        self.updateItem()
    
    @pyqtSlot(QPen)
    def penChanged(self, pen):
        self.polygonItem.setPen(self.rectangle.pen())
        self.updateItem()
    
    @pyqtSlot(QBrush)
    def brushChanged(self, brush):
        self.polygonItem.setBrush(self.rectangle.brush())
        self.updateItem()
    
    def _regenPolygon(self):
        
        if not self.rectangle.bounds().isValid():
            return
        
        tl = self.rectangle.bounds().topLeft()
        if not tl.isValid():
            return
        
        br = self.rectangle.bounds().bottomRight()
        if not br.isValid():
            return
        
        left = tl.longitude() * 3600.0
        right = br.longitude() * 3600.0
        top = tl.latitude() * 3600.0
        bottom = br.latitude() * 3600.0
        
        if left > right:
            right += 360.0 * 3600.0
        
        poly = QPolygonF()
        
        poly << QPointF(left, top)
        poly << QPointF(right, top)
        poly << QPointF(right, bottom)
        poly << QPointF(left, bottom)
        
        self.polygonItem.setPolygon(poly)