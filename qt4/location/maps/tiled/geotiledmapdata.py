'''
Created on 31.10.2011

@author: michi
'''
import math

from PyQt4.QtCore import qRound, QPointF, QPoint, qAbs, QRectF, Qt, pyqtSlot,\
    QRect, QTimer, SLOT, QSize
from PyQt4.QtGui import QPixmap, QPainter, QImage, QPainterPath, \
    QStyleOptionGraphicsItem 

from ems.qt4.location.maps.geomapdata import GeoMapData
from ems.qt4.location.geocoordinate import GeoCoordinate
from ems.qt4.location.geoboundingbox import GeoBoundingBox
from ems.qt4.location.maps.geomapobject import GeoMapObject
from geotiledmapgroupobjectinfo import GeoTiledMapGroupObjectInfo #@UnresolvedImport
from geotiledmaprectangleobjectinfo import GeoTiledMapRectangleObjectInfo #@UnresolvedImport
from geotiledmapcircleobjectinfo import GeoTiledMapCircleObjectInfo #@UnresolvedImport
from geotiledmappolylineobjectinfo import GeoTiledMapPolyLineObjectInfo #@UnresolvedImport
from geotiledmappolygonobjectinfo import GeoTiledMapPolygonObjectInfo #@UnresolvedImport
from geotiledmappixmapobjectinfo import GeoTiledMapPixmapObjectInfo #@UnresolvedImport
from geotiledmaptextobjectinfo import GeoTiledMapTextObjectInfo #@UnresolvedImport
from geotiledmaprouteobjectinfo import GeoTiledMapRouteObjectInfo #@UnresolvedImport
from geotiledmapcustomobjectinfo import GeoTiledMapCustomObjectInfo #@UnresolvedImport
from geotiledmapreply import GeoTiledMapReply #@UnresolvedImport
from ems.qt4.location.maps.geomapobjectengine import GeoMapObjectEngine
from geotiledmaprequest import GeoTiledMapRequest #@UnresolvedImport

def rmod(a, b):
    div = float(a) / float(b)
    return float(a) - div * float(b)

class GeoTileIterator(object):
    def __init__(self, mapDataOrConMode, mapType=None, screenRect=None,
                  tileSize=None, zoomLevel=None):
        self._atEnd = False
        self._row = -1
        self._col = -1
        self._width = 0
        self._screenRect = QRect()
        self._tileSize = QSize()
        self._mapType = 0
        self._connectivityMode = 0
        self._zoomLevel = 0
        self._currTopLeft = QPoint(0,0)
        self._tileRect = QRect()
        
        if isinstance(mapDataOrConMode,GeoTiledMapData):
            self._screenRect = mapDataOrConMode.worldReferenceViewportRect()
            self._mapType = mapDataOrConMode.mapType()
            self._connectivityMode = mapDataOrConMode.connectivityMode()
            self._zoomLevel = mapDataOrConMode.zoomLevel()
            
            tiledEngine = mapDataOrConMode.tileEngine
            self._tileSize = tiledEngine.tileSize() * mapDataOrConMode.zoomFactor()
        else:
            self._screenRect = screenRect
            self._tileSize = tileSize
            self._mapType = mapType
            self._connectivityMode = mapDataOrConMode
            self._zoomLevel = zoomLevel
            
        self._tileRect = QRect(QPoint(0,0), self._tileSize)
            
        x = (self._screenRect.topLeft().x() / self._tileSize.width())
        y = (self._screenRect.topLeft().y() / self._tileSize.height())
        
        self._width = self._tileSize.width() * (1 << self._zoomLevel)
        
        self._currTopLeft.setX(x * self._tileSize.width())
        self._currTopLeft.setY(y * self._tileSize.height())
    
    def hasNext(self):
        return not self._atEnd
    
    def next_(self):
        numCols = 1 << self._zoomLevel
        col = int((self._currTopLeft.x() / self._tileSize.width()) % numCols)
        row = int((self._currTopLeft.y() / self._tileSize.height()) % numCols)
        self._tileRect.moveTopLeft(self._currTopLeft)
        
        if self._tileRect.left() >= self._width:
            self._tileRect.translate(-self._width, 0)
    
        #self._currTopLeft.rx() += self._tileSize.width()
        self._currTopLeft.setX(self._currTopLeft.x() + self._tileSize.width())
        
        if self._currTopLeft.x() > self._screenRect.right(): #next row
            x = (self._screenRect.topLeft().x() / self._tileSize.width())
            self._currTopLeft.setX(x * self._tileSize.width())
            #self._currTopLeft.ry() += self._tileSize.height()
            self._currTopLeft.setY(self._currTopLeft.y() + self._tileSize.height())
        
        return GeoTiledMapRequest(self._connectivityMode, self._mapType,
                                  self._zoomLevel, self._row, self._col,
                                  self._tileRect)
        

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
        
        self._worldReferenceViewportCenter = QRect()
        self._worldReferenceSize = (1 << qRound(self.tileEngine.maximumZoomLevel())) * self.tileEngine.tileSize()
        self._worldReferenceViewportRect = QRect()
        
        self._worldReferenceViewportRectLeft = QRect()
        self._worldReferenceViewportRectRight = QRect()
        
        self._requestRects = []
        self._replyRects = []
        
        self._requests = []
        self._replies = []
        
        self.cache = {}
        self.zoomCache = {}
        
        self._zoomFactor = 0
        self._oe = GeoMapObjectEngine(self, self)
        self.spherical = "+proj=latlon +ellps=sphere"
        self.wgs84 = "+proj=latlon +ellps=WGS84"
        #self._tileSize = 0
    
    def __del__(self):
        for reply in self._replies:
            reply.abort()
            reply.deleteLater()
        if self._oe:
            del self._oe
    
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
        else:
            return None
    @pyqtSlot()
    def _processRequests(self):
        for reply in self._replies:
            if not self.intersectsScreen(reply.request().tileRect()) \
                or (self.zoomLevel() != reply.request().zoomLevel()) \
                or (self.mapType() != reply.request().mapType()) \
                or (self.connectivityMode() != reply.request().connectivityMode()):
                self._replyRects.remove(reply.request().tileRect())
                del self.zoomCache[reply.request()]
        
        tiledEngine = self._engine
        
        for req in self._requests:
            self._requestRects.remove(req.tileRect())
            
            if (req.tileRect() in self._replyRects) or\
                not self._intersectsScreen(req.tileRect()):
                continue
            
            reply = tiledEngine.getTileImage(req)
            
            if not reply:
                continue
            
            if reply.error() != GeoTiledMapReply.NoError:
                self.tileError(reply.error(), reply.errorString())
                reply.deleteLater()
                del self.zoomCache[reply.request()]
                continue
            
            reply.finished.connect(self._tileFinished)
            reply.error.connect(self.tileError)
            
            self._replies.append(reply)
            self._replyRects.append(reply.request.tileRect())
            
            if reply.isFinished():
                self._replyFinished(reply)
    
    @pyqtSlot()
    def _tileFinished(self):
        reply = self.sender()
        
        if not reply:
            if len(self._requests) > 0:
                QTimer.singleShot(0, self, SLOT('_processRequests()'))
                return
        else:
            self._replyFinished(reply)
    
    @pyqtSlot(GeoTiledMapReply)
    def _replyFinished(self, reply):
        self._replyRects.remove(reply.request().tileRect())
        self._replies.remove(reply)
        del self.zoomCache[reply.request()]
        
        if reply.error() != GeoTiledMapReply.NoError:
            if len(self._requests) > 0:
                QTimer.singleShot(0, self, SLOT('_processRequests()'))
            reply.deleteLater()
            return
        
        if self.zoomLevel() != reply.request().zoomLevel()\
            or self.mapType() != reply.request().mapType()\
            or self.connectivityMode() != reply.request().connectivityMode():
            if len(self._requests) > 0:
                QTimer.singleShot(0, self, SLOT("_processRequests()"))
            reply.deleteLater()
            return
        
        tile = QImage()
        
        if not tile.loadFromData(reply.mapImageData(), reply.mapImageFormat().toAscii()):
            del tile
            if len(self._requests) > 0:
                QTimer.singleShot(0, self, SLOT('_processRequests()'))
            reply.deleteLater()
            return
        
        if tile.isNull() or tile.size().isEmpty():
            del tile
            if len(self._requests) > 0:
                QTimer.singleShot(0, self, SLOT("_processRequests()"))
            reply.deleteLater()
            return
        
        self.cache[reply.request()] = tile
        
        self._cleanupCaches()
        
        tileRect = reply.request.tileRect()
        offset = self.windowOffset()
        
        overlaps = self.intersectedScreen(tileRect)
        
        for overlap in overlaps:
            t = overlap.second
            target = QRectF(offset.x() + int(t.left()) / self._zoomFactor,
                            offset.y() + int(t.top()) / self._zoomFactor,
                            int(t.width()) / self._zoomFactor,
                            int(t.height()) / self._zoomFactor);
            self.updateMapDisplay.emit(target)
        
        if len(self._requests) > 0:
            QTimer.singleShot(0, self, SLOT("_processRequests()"))
        
        reply.deleteLater()
    
    def tileError(self, error, errorString):
        pass
    
    def mapObjectsAtScreenPosition(self, screenPosition):
        if screenPosition.isNull():
            return []
        
        results = []
        considered = []
        
        self._oe.updateTransforms()
        
        pixelItems = self._oe.pixelScene.items(QRectF(screenPosition - QPointF(1,1),
                                                      screenPosition + QPointF(1,1)),
                                               Qt.IntersectsItemShape,
                                               Qt.AscendingOrder)
        
        for item in pixelItems:
            obj = self._oe.pixelItems.value(item)
            
            if obj.isVisible() and (obj not in considered):
                contains = False
            
            if self._oe.pixelExact.has_key(obj):
                for item in self._oe.pixelExact[obj]:
                    if item.shape().contains(screenPosition):
                        contains = True
                        break
            else:
                item = self._oe.graphicsItemFromMapObject(obj)
                
                if item:
                    trans = self._oe.pixelTrans[obj]
                    
                    for t in trans:
                        unused = False 
                        inv, ok = t.inverted(unused)
                        if ok:
                            testPt = screenPosition * inv
                            
                            #we have to special case text objects here
                            #in order to maintain their old (1.1) behaviour
                            
                            if obj.type_() == GeoMapObject.TextType:
                                if item.boundingRect().contains(testPt):
                                    contains = True
                                    break
                                else:
                                    if item.shape().contains(testPt):
                                        contains = True;
            if contains:
                results.append(obj)
            
            considered.append(obj)
        return results
    
    def mapObjectsInScreenRect(self, screenRect):
        results = []
        considered = []
        
        self._oe.updateTransforms()
        
        pixelItems = self._oe.pixelScene.items(screenRect,
                                               Qt.IntersectsItemShape,
                                               Qt.AscendingOrder)
        
        for item in pixelItems:
            obj = self._oe.pixelItems[item]
            
            if obj.isVisible() and (obj not in considered):
                contains = False
                
                if self._oe.pixelExact.has_key(obj):
                    for childItem in self._oe.pixelExact[obj]:
                        if childItem.shape().intersects(screenRect):
                            contains = True
                
                else:
                    gItem = self._oe.graphicsItemFromMapObject(obj) #QGraphicsItem
                    
                    if gItem:
                        trans = self._oe.pixelTrans[obj]
                        for t in trans:
                            unused = False
                            inv, ok = t.inverted(unused)
                            if ok:
                                testPoly = screenRect * inv
                                
                                testPath = QPainterPath()
                                testPath.moveTo(testPoly[0])
                                testPath.moveTo(testPoly[1])
                                testPath.moveTo(testPoly[2])
                                testPath.moveTo(testPoly[3])
                                testPath.closeSubpath()
                                
                                if item.shape().intersects(testPath):
                                    contains = True
                if contains:
                    results.append(obj)
                
                considered.append(obj)
                
    def worldReferenceViewportCenter(self):
        '''
        Returns the center of the viewport, in pixels on the entire
        map as a pixmap at the maximum zoom level.
        
        @rtype: QPoint
        '''
        return self._worldReferenceViewportCenter
    
    def worldReferenceSize(self):
        '''
        Returns the size, in pixels, of the entire map as a pixmap at the maximum
        zoom level.
        
        @rtype: QSize
        '''
        return self._worldReferenceSize
    
    def worldReferenceViewportRect(self):
        '''
        Returns the visible screen rectangle, in pixels on the entire map
        as a pixmap at the maximum zoom level.
        
        @rtype: QRect
        '''
        return self._worldReferenceViewportRect
    
    def zoomFactor(self):
        '''
        Returns the ratio between a single pixel on the screen and a pixel on
        the entire map as a pixmap at the maximum zoom level.
        
        @rtype: int
        '''
        return self._zoomFactor
    
    def triggerUpdateMapDisplay(self, target=QRectF()):
        '''
        Forces the map display to update in the region specified by \a target.

        If \a target is empty the entire map display will be updated.
        
        @param target: The target to be updated
        @type target: QRectF
        '''
        self.updateMapDisplay.emit(target)
    
    def windowOffset(self):
        offsetX = ((self._windowSize.width() * self._zoomFactor) - self._worldReferenceViewportRect.width()) / 2.0
        if offsetX < 0.0:
            offsetX = 0.0
        offsetX /= self._zoomFactor
        
        offsetY = ((self._windowSize.height() * self._zoomFactor) - self._worldReferenceViewportRect.height()) / 2.0
        if offsetY < 0.0:
            offsetY = 0.0
        offsetY /= self._zoomFactor;
    
        return QPointF(offsetX, offsetY)
    
    def _updateMapImage(self):
        if self._zoomLevel == -1.0 or not self._windowSize.isValid():
            return
        wasEmpty = (len(self._requests) == 0)
        it = GeoTileIterator(self)
        
        while it.hasNext():
            req = it.next()
            tileRect = req.tileRect()
            if not self.cache.has_key(req):
                if not (tileRect in self._requestRects) and not (tileRect in self._replyRects):
                    self._requests.append(req)
                    self._requestRects.append(tileRect)
        
        if wasEmpty and len(self._requests) > 0:
            QTimer.singleShot(0, self, SLOT("_processRequests()"))
    
    def _clearRequests(self):
        self._requests = []
        self._requestRects = []
    
    def paintMap(self, painter, option):
        '''
        @param painter: The painter
        @type painter: QPainter
        @param option: The StyleOption
        @type option: QStyleOptionGraphicsItem
        '''
        offset = self.windowOffset()
        
        it = GeoTileIterator(self)
        
        while it.hasNext():
            req = it.next()
            tileRect = req.tileRect()
            
            overlaps = self.intersectedScreen(tileRect)
            for overlap in overlaps:
                s = overlap.first
                t = overlap.second
                
                source = QRectF(int(s.left()) / self._zoomFactor,
                                int(s.top()) / self._zoomFactor,
                                int(s.width()) / self._zoomFactor,
                                int(s.height()) / self._zoomFactor)
                
                target = QRectF(offset.x() + int(t.left()) / self._zoomFactor,
                                offset.y() + int(t.top()) / self._zoomFactor,
                                int(t.width()) / self._zoomFactor,
                                int(t.height()) / self._zoomFactor)
                
                if self.cache.has_key(req):
                    painter.drawImage(target, self.cache[req], source)
                else:
                    if self.zoomCache.has_key(req):
                        painter.drawPixmap(target, self.zoomCache[req], source)
                    else:
                        painter.fillRect(target, Qt.lightGray)
    
    def paintObjects(self, painter, option):
        '''
        @param painter: The painter
        @type painter: QPainter
        @param option: The StyleOption
        @type option: QStyleOptionGraphicsItem
        '''
        painter.save()
        painter.setRenderingHint(QPainter.Antialiasing)
        
        if option:
            target = option.rect
        else:
            target = QRectF(QPointF(0,0), self._windowSize)
        
        offset = self.windowOffset()
        
        target.adjust(offset.x(), offset.y(), -1.0 * offset.x(), -1.0 * offset.y())
        
        painter.setClipRect(target)
        
        self._oe.updateTransforms()
        
        items = self._oe.pixelScene.items(target,
                                          Qt.IntersectsItemShape,
                                          Qt.AscendingOrder)
        
        objsDone = []
        
        baseTrans = painter.transform()
        
        style = QStyleOptionGraphicsItem()
        
        for item in items:
            obj = self._oe.pixelItems[item]
            
            if obj.isVisible() and not (obj in objsDone):
                if self._oe.pixelExact.has_key(obj):
                    for it in self._oe.pixelExact[obj]:
                        painter.setTransform(baseTrans)
                        
                        it.paint(painter, style)
                else:
                    gItem = self._oe.graphicsItemFromMapObject(obj)
                    for trans in self._oe.pixelTrans[obj]:
                        painter.setTransform(trans * baseTrans)
                        item.paint(painter, style)
                        for child in gItem.children():
                            painter.setTransform(child.transform() * trans * baseTrans)
                            painter.translate(child.pos())
                            child.paint(painter, style)
            
            objsDone.append(obj)
        painter.restore()
        del style
    
    def _cleanupCaches(self):
        boundaryTiles = 3
        
        tiledEngine = self._engine
        
        tileSize = tiledEngine.tileSize()
        
        cacheRect1 = QRectF()
        cacheRect2 = QRectF()
        
        cacheRect1 = self._worldReferenceViewportRect.adjusted(-boundaryTiles * tileSize.width(),
                                                               -boundaryTiles * tileSize.height(),
                                                               boundaryTiles * tileSize.width(),
                                                               boundaryTiles * tileSize.height())
        
        if cacheRect1.width() > self._worldReferenceSize.width():
            cacheRect1.setX(0)
            cacheRect1.setWidth(self._worldReferenceSize.width())
        else:
            if cacheRect1.x() + cacheRect1.width() > self._worldReferenceSize.width():
                oldWidth = cacheRect1.width()
                cacheRect1.setWidth(self._worldReferenceSize.width() - cacheRect1.x())
                cacheRect2 = QRectF(0,
                                    cacheRect1.y(),
                                    oldWidth - cacheRect1.width(),
                                    cacheRect1.height())
        
        keys = self.cache.keys()
        for key in keys:
            tileRect = keys[key].tileRect()
            if not cacheRect1.intersects(tileRect):
                if cacheRect2.isNull() or not cacheRect2.intersects(tileRect):
                    del self.cache[key]
    
    def screenRectForZoomFactor(self, factor):
        viewportWidth = self._windowSize.width()
        viewportHeight = self._windowSize.height()
        
        width = int(viewportWidth * factor)
        height = int(viewportHeight * factor)
        
        if width > self._worldReferenceSize.width():
            width = self._worldReferenceSize.width()
        
        if height > self._worldReferenceSize.height():
            height = self._worldReferenceSize.height()
        
        x = (self._worldReferenceViewportCenter.x() - (width / 2)) % self._worldReferenceSize.width()
        if x < 0:
            x += self._worldReferenceSize.width()
        
        y = self._worldReferenceViewportCenter.y() - (height / 2)
        
        if y < 0:
            y = 0
        
        if (y + height) >= self._worldReferenceSize.height():
            y = self._worldReferenceSize.height() - height
        
        return QRectF(x, y, width, height)
    
    def _updateScreenRect(self):
        worldReferenceViewportRect = self.screenRectForZoomFactor(self._zoomFactor)
        
        x = worldReferenceViewportRect.x()
        y = worldReferenceViewportRect.y()
        width = worldReferenceViewportRect.width()
        height = worldReferenceViewportRect.height()
        
        if x + width < self._worldReferenceSize.width():
            self._worldReferenceViewportRectLeft = worldReferenceViewportRect
            self._worldReferenceViewportRectRight = QRect()
        else:
            widthLeft = self._worldReferenceSize.width() - x
            widthRight = width - widthLeft
            self._worldReferenceViewportRectLeft = QRect(x, y, widthLeft, height)
            self._worldReferenceViewportRectRight = QRect(0, y, widthRight, height)
    
    def containedInScreen(self, point):
        return (self._worldReferenceViewportRectLeft.contains(point)
                or (self._worldReferenceViewportRectRight.isValid()
                    and self._worldReferenceViewportRectRight.contains(point)))
    
    def intersectsScreen(self, rect):
        return (self._worldReferenceViewportRectLeft.intersects(rect)
                or (self._worldReferenceViewportRectRight.isValid()
                    and self._worldReferenceViewportRectRight.intersects(rect)))
    
    def intersectedScreen(self, rect, translateToScreen=True):
        result = []
        rectL = rect.intersected(self._worldReferenceViewportRectLeft)
        if not rectL.isEmpty():
            source = QRect(rectL.topLeft() - rect.topLeft(), rectL.size())
            target = QRect(rectL.topLeft() - \
                           self._worldReferenceViewportRectLeft.topLeft(),
                           rectL.size())
            
            result.append((source, target))
            
            if self._worldReferenceViewportRectRight.isValid():
                rectR = rect.intersected(self._worldReferenceViewportRectRight)
                if not rectR.isEmpty():
                    source = QRect(rectR.topLeft() - rect.topLeft(), rectR.size())
                    target = QRect(rectR.topLeft() - \
                                   self._worldReferenceViewportRectRight.topLeft(),
                                   rectR.size())
                    if translateToScreen:
                        target.translate(self._worldReferenceViewportRectLeft.width,
                                         0)
                    result.append((source, target))
        return result
    
    def addObject(self, obj):
        super(GeoTiledMapData, self)._addObject(obj)
        self._oe.addObject(obj)
    
    def removeObject(self, obj):
        super(GeoTiledMapData, self)._removeObject(obj)
        self._oe.removeObject(obj)
    
    def update(self, obj):
        if obj:
            if obj.type_() == GeoMapObject.GroupType:
                self._oe.objectsForLatLonUpdate.append(obj)
                self._oe.objectsForPixelUpdate.append(obj)
                self.triggerUpdateMapDisplay()
            else:
                self._oe.invalidateObject(obj)
        else:
            self.triggerUpdateMapDisplay()
        
        