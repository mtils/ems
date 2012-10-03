'''
Created on 29.10.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSignal, pyqtSlot, QPointF, QRectF 

from ems.qt4.location.maps.geomapobjectinfo import GeoMapObjectInfo
from ems.qt4.location.geocoordinate import GeoCoordinate #@UnresolvedImport
from ems.qt4.location.geoboundingbox import GeoBoundingBox #@UnresolvedImport

class GeoTiledMapObjectInfo(GeoMapObjectInfo):
    def __init__(self, mapData, mapObject):
        self.inited = False
        GeoMapObjectInfo.__init__(self, mapData, mapObject)
        
        
        self.updateAfterInit = False
        self.graphicsItem = None
        self.tiledMapData = mapData
        
    
    def init(self):
        if self.graphicsItem:
            self.graphicsItem.setZValue(self._mapObject.zValue())
            self.graphicsItem.setVisible(self._mapObject.isVisible())
        self.inited = True
        if self.updateAfterInit:
            self.tiledMapData._updateMapDisplay()
            self.updateAfterInit = False
        GeoMapObjectInfo.init(self)
    
    @pyqtSlot(int)
    def zValueChanged(self, zValue):
        if self.graphicsItem:
            self.graphicsItem.setZValue(zValue)
            self.updateItem()
            if self.tiledMapData and self.tiledMapData._oe:
                self.tiledMapData._oe.rebuildScenes()
    
    @pyqtSlot(bool)
    def visibleChanged(self, visible):
        if self.graphicsItem:
            self.graphicsItem.setVisible(visible)
            self.updateItem()
    
    @pyqtSlot(GeoCoordinate)
    def originChanged(self, origin):
        if self.graphicsItem:
            self.updateItem()
    
    @pyqtSlot(int)
    def unitsChanged(self, units):
        if self.graphicsItem:
            self.updateItem()
    
    @pyqtSlot(int)
    def transformTypeChanged(self, transformType):
        if self.graphicsItem:
            self.updateItem()
    
    def boundingBox(self):
        if not self.graphicsItem or not self.tiledMapData:
            return GeoBoundingBox()
        
        e = self.tiledMapData._oe
        
        obj = self._mapObject
        
        e.updateTransforms()
        
        if e.latLonExact.contains(obj):
            items = e.latLonExact.values(obj)
            for item in items:
                latLonBounds = item.boundingRect()
                topLeft = latLonBounds.bottomLeft()
                if topLeft.x() >= 180.0 * 3600.0:
                    topLeft.setX(topLeft.x() - 360.0 * 3600.0)
                if (topLeft.x() < -180.0 * 3600.0):
                    topLeft.setX(topLeft.x() + 360.0 * 3600.0)
                
                bottomRight = latLonBounds.topRight()
                if (bottomRight.x() >= 180.0 * 3600.0):
                    bottomRight.setX(bottomRight.x() - 360.0 * 3600.0)
                if (bottomRight.x() < -180.0 * 3600.0):
                    bottomRight.setX(bottomRight.x() + 360.0 * 3600.0)
                
                tlc = GeoCoordinate(topLeft.y() / 3600.0, topLeft.x() / 3600.0)
                brc = GeoCoordinate(bottomRight.y() / 3600.0, bottomRight.x() / 3600.0)
                
                return GeoBoundingBox(tlc, brc)
            return GeoBoundingBox()
        else:
            trans = e.latLonTrans.value(obj)
            bounds = self.graphicsItem.boundingRect()
            poly = bounds * trans
            
            latLonBounds = poly.boundingRect()
            topLeft = latLonBounds.bottomLeft()
            if (topLeft.x() >= 180.0 * 3600.0):
                topLeft.setX(topLeft.x() - 360.0 * 3600.0)
            if (topLeft.x() < -180.0 * 3600.0):
                topLeft.setX(topLeft.x() + 360.0 * 3600.0)
            
            bottomRight = latLonBounds.topRight()
            if (bottomRight.x() >= 180.0 * 3600.0):
                bottomRight.setX(bottomRight.x() - 360.0 * 3600.0)
            if (bottomRight.x() < -180.0 * 3600.0):
                bottomRight.setX(bottomRight.x() + 360.0 * 3600.0)
            
            tlc = GeoCoordinate(topLeft.y() / 3600.0, topLeft.x() / 3600.0)
            brc = GeoCoordinate(bottomRight.y() / 3600.0, bottomRight.x() / 3600.0)
            
            return GeoBoundingBox(tlc, brc)
    
    def contains(self, coordinate):
        if not self.graphicsItem or not self.tiledMapData:
            return False
        
        e = self.tiledMapData._oe
        
        e.updateTransforms()
        latLonPoint = QPointF(coordinate.longitude()*3600.0, coordinate.latitude()*3600.0)
        
        obj = self._mapObject
        
        if e.latLonExact.contains(obj):
            items = e.latLonExact.values(obj)
            for item in items:
                if item.contains(latLonPoint):
                    return True
        else:
            transList = e.latLonTrans.values(obj)
            for trans in transList:
                unused = False
                inv,ok = trans.inverted(unused)
                if not ok:
                    continue
                localPoint = latLonPoint * inv
                
                if self.graphicsItem.contains(localPoint):
                    return True
        return False
    
    def updateItem(self, target=None):
        if target is None:
            target = QRectF()
        if not self.inited:
            self.updateAfterInit = True
            return
        
        obj = self._mapObject
        if obj:
            self.tiledMapData.update(obj)
        if self.graphicsItem:
            self.tiledMapData.triggerUpdateMapDisplay(target)
                