'''
Created on 02.11.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSlot, qAbs
from PyQt4.QtGui import QGraphicsPathItem, QPen, QPainterPath

from geotiledmapobjectinfo import GeoTiledMapObjectInfo #@UnresolvedImport

class GeoTiledMapPolyLineObjectInfo(GeoTiledMapObjectInfo):
    def __init__(self, mapData, mapObject):
        self.polyLine = mapObject
        self.pathItem = QGraphicsPathItem()
        #self.graphicsItem = self.pathItem
        
        self.polyLine.pathChanged.connect(self.pathChanged)
        self.polyLine.penChanged.connect(self.penChanged)
        
        
        self._mapData = mapData
        GeoTiledMapObjectInfo.__init__(self, mapData, mapObject)
        
        self.graphicsItem = self.pathItem
        self.penChanged(self.polyLine.pen())
        self.pathChanged(self.polyLine.path())
    
    @pyqtSlot(list)
    def pathChanged(self, path):
        self._genPath()
        self.updateItem()
    
    @pyqtSlot(QPen)
    def penChanged(self, pen):
        self.pathItem.setPen(self.polyLine.pen())
        self.updateItem()
    
    def _genPath(self):
        path = self.polyLine.path()
        p = QPainterPath()
        if len(path) > 0:
            origin = path[0]
            
            ox = origin.longitude() * 3600.0
            oy = origin.latitude() * 3600.0
            
            oldx = ox
            oldy = oy
            
            p.moveTo(0, 0)
            for pt in path:
                x = pt.longitude() * 3600.0
                y = pt.latitude() * 3600.0
                if qAbs(x - oldx) > 180.0 *3600.0:
                    if x > oldx:
                        x -= 360.0 * 3600.0
                    elif x < oldx:
                        x += 360.0 * 3600.0
                
                p.lineTo(x - ox, y -oy)
                oldx = x
                oldy = y
        
        self.pathItem.setPath(p)
    
    