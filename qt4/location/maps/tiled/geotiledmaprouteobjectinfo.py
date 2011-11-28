'''
Created on 02.11.2011

@author: michi
'''
from PyQt4.QtCore import qAbs
from PyQt4.QtGui import QGraphicsPathItem, QPainterPath

from geotiledmapobjectinfo import GeoTiledMapObjectInfo #@UnresolvedImport

class GeoTiledMapRouteObjectInfo(GeoTiledMapObjectInfo):
    def __init__(self, mapData, mapObject):
        GeoTiledMapObjectInfo.__init__(self, mapData, mapObject)
        self.route = mapObject
        
        self.route.routeChanged.connect(self.routeChanged)
        self.route.penChanged.connect(self.penChanged)
        self.route.detailLevelChanged.connect(self.detailLevelChanged)
        
        self.pathItem = QGraphicsPathItem()
        self.graphicsItem = self.pathItem
        
        self.routeChanged(self.route.route())
        self.penChanged(self.route.pen())
        self.routeChanged(self.route.route())
    
    def routeChanged(self, route):
        self._regenPath()
        self.updateItem()
    
    def penChanged(self, pen):
        self.pathItem.setPen(self.route.pen())
        self.updateItem()
    
    def detailLevelChanged(self, detailLevel):
        self.updateItem()
    
    def _regenPath(self):
        path = []
        
        segment = self.route.route().firstRouteSegment()
        while segment.isValid():
            #path.append(segment.path())
            for coord in segment.path():
                path.append(coord)
            segment = segment.nextRouteSegment()
        
        pth = QPainterPath()
        
        if len(path) > 0:
            oldx = 0.0
            oldy = 0.0
            firstIteration = True
            for coord in path:
                #print coord.latitude(), coord.longitude() 
                x = coord.longitude() * 3600.0
                y = coord.latitude() * 3600.0
                if firstIteration:
                    pth.moveTo(x, y)
                    firstIteration = False
                else:
                    if qAbs(x - oldx) > 180.0 * 3600.0:
                        if x > oldx:
                            x -= 360.0 * 3600.0
                        elif x < oldx:
                            x += 360.0 * 3600.0
                    
                    pth.lineTo(x, y)
                
                oldx = x
                oldy = y
                
        self.pathItem.setPath(pth)