'''
Created on 31.10.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QGraphicsEllipseItem, QPen, QBrush

from geotiledmapobjectinfo import GeoTiledMapObjectInfo ##@UnresolvedImport

class GeoTiledMapCircleObjectInfo(GeoTiledMapObjectInfo):
    circle = None
    '@type circle: GeoMapCircleObject'
    
    ellipseItem = None
    '@type circle: GeoMapEllipseObject'
    
    def __init__(self, mapData, mapObject):
        '''
        Constructor
        
        @param mapData: The mapData
        @type mapData: GeoTiledMapData
        @param mapObject: GeoMapObject
        @type mapObject: GeoMapObject
        '''
        self.circle = mapObject
        
        self.ellipseItem = QGraphicsEllipseItem()
        self.ellipseItem.setPos(0, 0)
        
        self.graphicsItem = self.ellipseItem
        
        GeoTiledMapObjectInfo.__init__(self, mapData, mapObject)
        self.circle.radiusChanged.connect(self.radiusChanged)
        self.circle.penChanged.connect(self.penChanged)
        self.circle.brushChanged.connect(self.brushChanged)
        
        
        
        self.graphicsItem = self.ellipseItem
        
        self.radiusChanged(self.circle.radius())
        self.brushChanged(self.circle.brush())
        self.penChanged(self.circle.pen())
    
    @pyqtSlot(int)
    def radiusChanged(self, radius):
        radius = self.circle.radius()
        self.ellipseItem.setRect(-1*radius, -1*radius, 2*radius, 2*radius)
        self.updateItem()
    
    @pyqtSlot(QPen)
    def penChanged(self, pen):
        '''
        @param pen: The pen
        @type pen: QPen
        '''
        self.ellipseItem.setPen(pen)
        self.updateItem()
    
    @pyqtSlot(QBrush)
    def brushChanged(self, brush):
        '''
        @param brush: The new brush
        @type brush: QBrush
        '''
        self.ellipseItem.setBrush(brush)
        self.updateItem()