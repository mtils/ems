'''
Created on 31.10.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSlot, QPoint
from PyQt4.QtGui import QGraphicsItem

from geotiledmapobjectinfo import GeoTiledMapObjectInfo #@UnresolvedImport

class GeoTiledMapCustomObjectInfo(GeoTiledMapObjectInfo):
    
    custom = None
    '@type custom: GeoMapCustomObject'
    
    def __init__(self, mapData, mapObject):
        '''
        @param mapData: The mapData
        @type mapData: GeoTiledMapData
        @param mapObject: The mapObject
        @type mapObject: GeoMapObject
        '''
        GeoTiledMapObjectInfo.__init__(self, mapData, mapObject)
        self.custom = mapObject
        
        self.custom.triggerUpdate.connect(self.updateTriggered)
        self.custom.graphicsItemChanged.connect(self.graphicsItemChanged)
        self.custom.offsetChanged.connect(self.offsetChanged)
        
        self.graphicsItem = None
        
        self.graphicsItemChanged(self.custom.graphicsItem())
        self.offsetChanged(self.custom.offset())
    
    @pyqtSlot()
    def updateTriggered(self):
        self.updateItem()
    
    @pyqtSlot(QGraphicsItem)
    def graphicsItemChanged(self, item):
        self.graphicsItem = self.custom.graphicsItem()
        self.updateItem()
    
    @pyqtSlot(QPoint)
    def offsetChanged(self, offset):
        self.graphicsItem.setPos(self.custom.offset())
        self.updateItem()