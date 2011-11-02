'''
Created on 31.10.2011

@author: michi
'''
import math

from PyQt4.QtCore import qRound, QPointF, QPoint, qAbs, QRectF, Qt
from PyQt4.QtGui import QPixmap, QPainter 

from lib.ems.qt4.location.maps.geomapdata import GeoMapData
from lib.ems.qt4.location.geocoordinate import GeoCoordinate
from lib.ems.qt4.location.geoboundingbox import GeoBoundingBox
from lib.ems.qt4.location.maps.geomapobject import GeoMapObject
from geotiledmapgroupobjectinfo import GeoTiledMapGroupObjectInfo #@UnresolvedImport
from geotiledmaprectangleobjectinfo import GeoTiledMapRectangleObjectInfo #@UnresolvedImport
from geotiledmapcircleobjectinfo import GeoTiledMapCircleObjectInfo #@UnresolvedImport
from geotiledmappolylineobjectinfo import GeoTiledMapPolyLineObjectInfo #@UnresolvedImport
from geotiledmappolygonobjectinfo import GeoTiledMapPolygonObjectInfo #@UnresolvedImport
from geotiledmappixmapobjectinfo import GeoTiledMapPixmapObjectInfo #@UnresolvedImport
from geotiledmaptextobjectinfo import GeoTiledMapTextObjectInfo #@UnresolvedImport
from geotiledmaprouteobjectinfo import GeoTiledMapRouteObjectInfo #@UnresolvedImport
from geotiledmapcustomobjectinfo import GeoTiledMapCustomObjectInfo #@UnresolvedImport

def rmod(a, b):
    div = float(a) / float(b)
    return float(a) - div * float(b)

class GeoTileIterator(object):
    pass
    

class GeoTiledMapData(GeoMapData):
    '''
    \brief The QGeoTiledMapData class is a subclass of QGeoMapData provided
    to make working with tile based mapping services more convenient.

    \inmodule QtLocation

    \ingroup maps-impl-tiled

    \since 1.2

    This class assumes that at a zoom level of z the world is represented as a
    2^z by 2^z grid of tiles, and that the Mercator projection is used to map
    back and forth between coordinate and positions on the map.

    Different projections can be provided by reimplementing
    coordinateToWorldReferencePosition() and worldReferencePositionToCoordinate().

    Many of the internal calculations deal with positions as though they are
    pixel positions on the map at the maximum zoom level.  Several functions are
    provided which expose information about the map and the viewport onto the
    map in these terms for use with custom QGeoMapObjectInfo subclasses.

    These functions include worldReferenceViewportCenter(), worldReferenceSize() and
    worldReferenceViewportRect().

    NOTE: QGeoTiledMapData blocks property change signals from QGeoMapData by calling
    QGeoMapData::setBlockPropertyChangeSignals() with true. Changing this in
    QGeoTiledMapData subclasses will cause the signals being emitted at wrong time.
    '''
    def __init__(self, engine):
        '''
        Constructs a new tiled map data object, which makes use of the functionality provided by \a engine.
        
        @param engine: The MappingManagerEngine
        @type engine: GeoMappingManagerEngine
        '''
        self.tileEngine = engine
        
        self.setBlockPropertyChangeSignals(True)
        self.setZoomLevel(8.0)
        self._worldReferenceSize = (1 << qRound(self.tileEngine.maximumZoomLevel())) * self.tileEngine.tileSize()
        self._worldReferenceViewportCenter = None
        self.cache = {}
        self.zoomCache = {}
        self._zoomFactor = 0
        #self._tileSize = 0
    
    def coordinateToScreenPosition(self, coordOrLat, lon=0.0):
        if isinstance(coordOrLat, GeoCoordinate):
            lon = coordOrLat.longitude()
            lat = coordOrLat.latitude()
        else:
            lat = coordOrLat
            
        offset = self.windowOffset()
        
        pos = self._coordinateToWorldReferencePosition(lon, lat)
        
        x = pos.x() - self.worldReferenceViewportRect.left()
        
        y = pos.y() - self.worldReferenceViewportRect.top()
        
        posF = QPointF(offset.x() + int(x) / self._zoomFactor, offset.y() + int(y) / self._zoomFactor)
        
        return posF
    
    def screenPositionToCoordinate(self, screenPosition):
        worldRef = self._screenPositionToWorldReferencePosition(screenPosition)
        
        if worldRef.isNull():
            return GeoCoordinate()
        
        insph = self._worldReferencePositionToCoordinate(worldRef)
        
        return insph
    
    def _screenPositionToWorldReferencePosition(self, screenPosition):
        offset = self.windowOffset()
        
        pos = QPointF(screenPosition.x() - offset.x(),
                      screenPosition.y() - offset.y())
        
        worldX = int(self.worldReferenceViewportRect.left() + pos.x() * self._zoomFactor + 0.5) % self._worldReferenceSize.width()
        worldY = int(self.worldReferenceViewportRect.top() + pos.y() * self._zoomFactor + 0.5) % self._worldReferenceSize.height()
        
        return QPointF(worldX, worldY)
    
    def _coordinateToWorldReferencePosition(self, lngOrCoord, lat):
        '''
        Converts the coordinate \a coordinate to a pixel position on the entire
        map at the maximum zoom level.
    
        The default implementation is based on the Mercator projection.
        
        @param lngOrCoord: GeoCoordinate or lat
        @type lngOrCoord: GeoCoordinate|float
        @param lat: Latitude
        @type lat: float
        '''
        if isinstance(lngOrCoord, GeoCoordinate):
            lng = lngOrCoord.longitude()
            lat = lngOrCoord.latitude()
        else:
            lng = lngOrCoord
            
        lng = lng / 360.0 + 0.5
        
        lat = 0.5 - (math.log(math.tan((math.pi / 4.0) + (math.pi / 2.0) * lat / 180.0)) / math.pi) / 2.0
        lat = max(0.0, lat)
        lat = min(1.0, lat)
        
        x = lng * self._worldReferenceSize.width()
        y = lng * self._worldReferenceSize.height()
        
        if x > 0:
            x += 0.5
        else:
            x -= 0.5
        
        if y > 0:
            y += 0.5
        else:
            y -= 0.5
        r = QPoint(int(x), int(y))
        return r
    
    def _worldReferencePositionToCoordinate(self, pixel):
        '''
        Converts the pixel position \a pixel on the map to a coordinate.

        The pixel position is relative the entire map at the maximum zoom level.
    
        The default implementation is based on the Mercator projection.
        
        
        @param pixel: The pixel on screen
        @type pixel: QPoint
        '''
        fx = pixel.x() / self._worldReferenceSize.width()
        fy = pixel.y() / self._worldReferenceSize.height()
        
        if fy < 0.0:
            fy = 0.0
        elif fy > 1.0:
            fy = 1.0
        
        if fy == 0.0:
            lat = 90.0
        elif fy == 1.0:
            lat = -90.0
        else:
            lat = (180.0 / math.pi) * (2.0 * math.atan(math.exp(math.pi * (1.0 - 2.0 * fy))) - (math.pi / 2.0))
        
        if fx >= 0:
            lng = rmod(fx, 1.0)
        else:
            lng = rmod(1.0 - rmod(-1.0 * fx, 1.0), 1.0)
        
    
        lng = lng * 360.0 - 180.0
        
        return GeoCoordinate(lat, lng, 0.0)
    
    def setCenter(self, center):
        changed = (self._center != center)
        if not changed:
            return
        self._worldReferenceViewportCenter = self._coordinateToWorldReferencePosition(center)
        self._updateScreenRect()
        self.updateMapDisplay.emit()
        self.centerChanged.emit(center)
        
        self._updateMapImage()
        GeoMapData.setCenter(self, center)
        self._oe.invalidatePixelsForViewport()
        self._oe.trimPixelTransforms()
    
    def setMapType(self, mapType):
        if mapType == self._mapType:
            return
        GeoMapData.setMapType(self, mapType)
        self._clearRequests()
        self.cache.clear()
        self.zoomCache.clear()
        self.updateMapDisplay.emit()
        self.mapTypeChanged.emit(self._mapType)
        self._updateMapImage()
    
    def setConnectivityMode(self, mode):
        if mode == self._connectivityMode:
            return
        GeoMapData.setConnectivityMode(self, mode)
        self.connectivityModeChanged.emit(mode)
    
    def center(self):
        return self._worldReferencePositionToCoordinate(self._worldReferenceViewportCenter)
    
    def setZoomLevel(self, zoomLevelF):
        oldImage = QPixmap(self.windowSize().toSize())
        if not oldImage.isNull():
            painter1 = QPainter(oldImage)
            self.paintMap(painter1, 0)
            painter1.end()
        
        oldZoomLevel = self._zoomLevel
        zoomLevel = qRound(zoomLevelF)
        
        GeoMapData.setZoomLevel(self, zoomLevel)
        
        self._oe.invalidateZoomDependents()
        self._oe.invalidatePixelsForViewport()
        self._oe.trimPixelTransforms()
        
        zoomLevel = GeoMapData.zoomLevel(self)
        
        zoomDiff = qRound(zoomLevel - oldZoomLevel)
        
        if zoomDiff == 0:
            return
        
        self._zoomFactor = 1 << qRound(self._engine.maximumZoomLevel() - self._zoomLevel)
        tileSize = self.tileEngine.tileSize()
        
        self._updateScreenRect()
        
        if oldImage.isNull():
            self._updateMapImage()
            self.zoomLevelChanged.emit(self._zoomLevel)
            return
        
        #scale old image
        target = oldImage.rect()
        
        width = target.width() / (1 << qAbs(zoomDiff))
        height = target.height() / (1 << qAbs(zoomDiff))
        x = target.x() + ((target.width() - width) / 2.0)
        y = target.y() + ((target.height() - height) / 2.0)
        source = QRectF(x, y, width, height)
        
        newImage = QPixmap(oldImage.size())
        newImage.fill(Qt.lightGray)
        painter2 = QPainter(newImage)
        
        if zoomDiff < 0:
            painter2.drawPixmap(source, oldImage, target)
        else:
            painter2.drawPixmap(target, oldImage, source)
        
        painter2.end()
        
        self.zoomCache = {}
        
        it = GeoTileIterator(self)
        offset = self.windowOffset()
        
        while it.hasNext():
            req = it.next()
            tileRect = req.tileRect()
            
            if self.cache.has_key(req):
                continue
            
            if not self.intersectsScreen(tileRect):
                continue
            
            overlaps = self.intersectedScreen(tileRect)
            for i in range(len(overlaps)):
                s = overlaps[i].first
                t = overlaps[i].second
                
                source = QRectF(offset.x() + int(t.left()) / self._zoomFactor,
                                offset.y() + int(t.top()) / self._zoomFactor,
                                int(t.width()) / self._zoomFactor,
                                int(t.height()) / self._zoomFactor)
                
                tile = QPixmap(tileSize)
                tile.fill(Qt.lightGray)
                
                target = QRectF(int(s.left()) / self._zoomFactor,
                                int(s.top()) / self._zoomFactor,
                                int(s.width()) / self._zoomFactor,
                                int(s.height()) / self._zoomFactor)
                
                painter3 = QPainter(tile)
                painter3.drawPixmap(target, newImage, source)
                painter3.end()
                
                self.zoomCache[req] = tile
        
        self.updateMapDisplay.emit()
        
        self._clearRequests()
        self._updateMapImage()
        
        self.zoomLevelChanged.emit(self._zoomLevel)
    
    def setWindowSize(self, size):
        '''
        @param size: The new size
        @type size: QSize
        '''
        
        if self._windowSize == size:
            return
        
        GeoMapData.setWindowSize(self, size)
        
        self._oe.invalidatePixelsForViewport()
        self._oe.trimPixelTransforms()
    
        self._updateScreenRect();
    
        self.windowSizeChanged.emit(self._windowSize);
    
        self._updateMapImage();
    
    def pan(self, dx, dy):
        '''
        @param dx: x panning
        @type dx: int
        @param dy: y panning
        @type dy: int
        '''
        x = self._worldReferenceViewportCenter.x()
        y = self._worldReferenceViewportCenter.y()
        
        x = (x + dx * self._zoomFactor) % self._worldReferenceSize.width()
        if x < 0:
            x += self._worldReferenceSize.width()
        
        y = (y + dy * self._zoomFactor)
        height = int(self._worldReferenceViewportRect.height() / 2.0)
        if y < height:
            y = height
        if y > self._worldReferenceSize.height() - height:
            y = self._worldReferenceSize.height() - height
        
        self._worldReferenceViewportCenter.setX(x)
        self._worldReferenceViewportCenter.setY(y)
        
        centerCoord = self.center()
        
        GeoMapData.setCenter(self, centerCoord)
        self._oe.invalidatePixelsForViewport()
        self._oe.trimPixelTransforms()
    
        self._updateScreenRect();
    
        self.centerChanged.emit(centerCoord)
    
        self._updateMapImage();
    
    def viewport(self):
        if self._worldReferenceViewportRectRight.isValid():
            return GeoBoundingBox(self._worldReferencePositionToCoordinate(self._worldReferenceViewportRectLeft.topLeft()),
                                  self._worldReferencePositionToCoordinate(self._worldReferenceViewportRectRight.bottomRight()));
        else:
            return GeoBoundingBox(self._worldReferencePositionToCoordinate(self._worldReferenceViewportRect.topLeft()),
                                   self._worldReferencePositionToCoordinate(self._worldReferenceViewportRect.bottomRight()))
        
    def fitInViewport(self, bounds, preserveViewportCenter=False):
        if not preserveViewportCenter:
            self.setCenter(bounds.center())
        
        minZoomLevel = self._engine.minimumZoomLevel()
        maxZoomLevel = self._engine.maximumZoomLevel()
        
        zoomFactor = 1 << maxZoomLevel
        
        for i in range(minZoomLevel, (maxZoomLevel+1)):
            rect = self._screenRectForZoomFactor(zoomFactor)
            viewport = GeoBoundingBox(self._worldReferencePositionToCoordinate(rect.topLeft()),
                                      self._worldReferencePositionToCoordinate(rect.bottomRight()))
            
            if not viewport.contains(bounds):
                self.setZoomLevel(max(minZoomLevel, i -1))
                return
            
            zoomFactor /= 2
        
        self.setZoomLevel(maxZoomLevel)
    
    def paintMap(self, painter, option):
        '''
        @param painter: The painter
        @type painter: QPainter
        @param option: The StyleOption
        @type option: QStyleOptionGraphicsItem
        '''
        self._paintMap(painter, option)
            
    def paintObjects(self, painter, option):    
        '''
        @param painter: The painter
        @type painter: QPainter
        @param option: The StyleOption
        @type option: QStyleOptionGraphicsItem
        '''
        self._paintObjects(painter, option)
    
    def createMapObjectInfo(self, mapObject):
        '''
        @param obj: The MapObject
        @type obj: GeoMapObject
        '''
        type_ = mapObject.type_()
        if type_ == GeoMapObject.GroupType:
            return GeoTiledMapGroupObjectInfo(self, mapObject)
        elif type_ == GeoMapObject.RectangleType:
            return GeoTiledMapRectangleObjectInfo(self, mapObject)
        elif type_ == GeoMapObject.CircleType:
            return GeoTiledMapCircleObjectInfo(self, mapObject)
        elif type_ == GeoMapObject.PolylineType:
            return GeoTiledMapPolyLineObjectInfo(self, mapObject)
        elif type_ == GeoMapObject.PolygonType:
            return GeoTiledMapPolygonObjectInfo(self, mapObject)
        elif type_ == GeoMapObject.PixmapType:
            return GeoTiledMapPixmapObjectInfo(self, mapObject)
        elif type_ == GeoMapObject.TextType:
            return GeoTiledMapTextObjectInfo(self, mapObject)
        elif type_ == GeoMapObject.RouteType:
            return GeoTiledMapRouteObjectInfo(self, mapObject)
        elif type_ == GeoMapObject.CustomType:
            return GeoTiledMapCustomObjectInfo(self, mapObject)