'''
Created on 02.11.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QGraphicsPathItem

from geotiledmapobjectinfo import GeoTiledMapObjectInfo #@UnresolvedImport
from ems.qt4.location.maps.geomapgroupobject import GeoMapGroupObject
from ems.qt4.location.maps.geomapobject import GeoMapObject

class GeoTiledMapGroupObjectInfo(GeoTiledMapObjectInfo):
    def __init__(self, mapData, mapObject):
        GeoTiledMapObjectInfo.__init__(self, mapData, mapObject)
        self.group = mapObject
        #self.group.addChildObject(mapObject)
        #self._mapData = mapData
        
        self.group.childAdded.connect(self.childAdded)
        self.group.childUpdated.connect(self.childUpdated)
        self.group.childRemoved.connect(self.childRemoved)
        
        self.pathItem = QGraphicsPathItem()
        self.graphicsItem = self.pathItem
        
        self.pathItem.setPos(0.0, 0.0)
        
        objects = self.group.childs
        for obj in objects:
            info = obj.info()
            if info:
                info.graphicsItem.setParentItem(self.graphicsItem)
        
        self.updateItem()
    
    @pyqtSlot(GeoMapObject)
    def childAdded(self, childObject):
        if not childObject:
            return
        info = childObject.info()
        
        if info and info.graphicsItem:
            #the child's z value will get updated in QGeoTiledMapGroupObjectInfo::childUpdated
            #we do this in order to keep the same order of operations that we had previously
            try:
                childObject.zValueChanged.disconnect(info.zValueChanged)
            except TypeError:
                pass
            info.graphicsItem.setParentItem(self.graphicsItem)
            self._mapData.update(self._mapObject)
    
    @pyqtSlot(GeoMapObject)
    def childUpdated(self, childObject):
        if not childObject:
            return
        info = childObject.info()
        
        if info and info.graphicsItem:
            self._mapData.update(self._mapObject)
            info.zValueChanged(childObject.zValue())
    
    @pyqtSlot(GeoMapObject)
    def childRemoved(self, childObject):
        try:
            if childObject and self._mapData._oe:
                self._mapData._oe.removeObject(childObject)
                self.updateItem()
        except AttributeError:
            pass
    
    