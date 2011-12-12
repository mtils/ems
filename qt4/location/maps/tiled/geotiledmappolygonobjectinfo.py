'''
Created on 02.11.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSlot, QPointF, qAbs
from PyQt4.QtGui import QGraphicsPolygonItem, QPolygonF

from geotiledmapobjectinfo import GeoTiledMapObjectInfo #@UnresolvedImport

class GeoTiledMapPolygonObjectInfo(GeoTiledMapObjectInfo):
    def __init__(self, mapData, mapObject):
        self.polygon = mapObject
        
        GeoTiledMapObjectInfo.__init__(self, mapData, mapObject)
        
        self.polygon.pathChanged.connect(self.pathChanged)
        self.polygon.penChanged.connect(self.penChanged)
        self.polygon.brushChanged.connect(self.brushChanged)
        
        self.polygonItem = QGraphicsPolygonItem()
        self.graphicsItem = self.polygonItem
        
        self.penChanged(self.polygon.pen())
        self.brushChanged(self.polygon.brush())
        self.pathChanged(self.polygon.path())
    
    def pathChanged(self, path):
        self._genPoly()
        self.updateItem()
    
    def penChanged(self, pen):
        self.polygonItem.setPen(self.polygon.pen())
        self.updateItem()
    
    def brushChanged(self, brush):
        self.polygonItem.setBrush(self.polygon.brush())
        self.updateItem()
    
    def _genPoly(self):
        path = self.polygon.path()
        poly = QPolygonF()
        if len(path) > 0:
            origin = path[0]
            ox = origin.longitude() * 3600.0
            oy = origin.latitude() * 3600.0
            
            oldx = ox
            oldy = oy
            
            
            poly << QPointF(0,0)
            for pt in path:
                x = pt.longitude() * 3600.0
                y = pt.latitude() * 3600.0
    
                if (qAbs(x - oldx) > 180.0 * 3600.0):
                    if x > oldx:
                        x -= 360.0 * 3600.0
                    elif x < oldx:
                        x += 360.0 * 3600.0
                 
    
                poly << QPointF(x - ox, y - oy)
    
                oldx = x;
                oldy = y;
        self.polygonItem.setPolygon(poly)
        