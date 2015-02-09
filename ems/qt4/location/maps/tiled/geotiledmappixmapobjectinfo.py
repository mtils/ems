'''
Created on 02.11.2011

@author: michi
'''
from PyQt4.QtCore import QPointF
from PyQt4.QtGui import QGraphicsPixmapItem

from geotiledmapobjectinfo import GeoTiledMapObjectInfo #@UnresolvedImport

class GeoTiledMapPixmapObjectInfo(GeoTiledMapObjectInfo):
    def __init__(self, mapData, mapObject):
        GeoTiledMapObjectInfo.__init__(self, mapData, mapObject)
        self.pixmap = mapObject
        
        self.pixmap.pixmapChanged.connect(self.pixmapChanged)
        self.pixmap.offsetChanged.connect(self.offsetChanged)
        
        self.pixmapItem = QGraphicsPixmapItem()
        self.graphicsItem = self.pixmapItem
        
        self.originChanged(self.pixmap.origin())
        self.pixmapChanged(self.pixmap.pixmap())
        self.offsetChanged(self.pixmap.offset())
        
        
        
    
    def pixmapChanged(self, pixmap):
        #print "pixmap Changed to {0} empty:{1}".format(pixmap, pixmap.isNull())
        self.pixmapItem.setPixmap(self.pixmap.pixmap())
        #self.pixmapItem.setPixmap(pixmap)
        self.pixmapItem.setScale(1.0)
        self.updateItem()
    
    def offsetChanged(self, offset):
        self.pixmapItem.setOffset(QPointF(self.pixmap.offset()))
        self.updateItem()
    
    
    
    
        
