'''
Created on 20.10.2011

@author: michi
'''
import time
from PyQt4.QtCore import QObject, pyqtSignal, QSizeF, QPointF, QRectF

from graphicsgeomap import GraphicsGeoMap #@UnresolvedImport
from geomapgroupobject import GeoMapGroupObject #@UnresolvedImport
from ems.qt4.location.geocoordinate import GeoCoordinate #@UnresolvedImport
from ems.qt4.location.geoboundingbox import GeoBoundingBox #@UnresolvedImport

class GeoMapData(QObject):
    '''
    The QGeoMapData class are used as a bridge between QGraphicsGeoMap and
    QGeoMappingManager.


    Instances of QGeoMapData are created with
    QGeoMappingManager::createMapData(), and are used internally by
    QGraphicsGeoMap to manage the state of the map and the associated
    QGeoMapObject instances.

    Plugin implementers will need to provide implementations of
    coordinateToScreenPosition(const QGeoCoordinate &coordinate) and
    QGeoCoordinate screenPositionToCoordinate(const QPointF &screenPosition).

    The other virtual functions can be overridden. If the screen position to
    coordinate tranformations are expensive then overriding these functions may
    allow optimizations based on caching parts of the geometry information.

    Subclasses should override createMapObjectInfo() so that QGeoMapObjectInfo
    instances will be created for each QGeoMapObject type in order to provide
    the QGeoMapData subclass specific behaviours for the map objects.
    '''
    _engine = None
    _containerObject = None
    _windowSize = None
    _zoomLevel = -1.0
    _bearing = 0
    _tilt = 0
    _center = None
    _mapType = 0
    _connectivityMode = 0
    _overlays = []
    
    __blockPropertyChangeSignals = False
    
    
    windowSizeChanged = pyqtSignal(QSizeF)
    '''This signal is emitted when the size of the window which contains
    the map has changed.'''
    
    zoomLevelChanged = pyqtSignal(float)
    '''This signal is emitted when the zoom level of the map has changed.
    The new value is zoomLevel.'''
    
    bearingChanged = pyqtSignal(float)
    '''This signal is emitted when the bearing of the map has changed.
    The new value is \a bearing.'''
    
    tiltChanged = pyqtSignal(float)
    '''This signal is emitted when the tilt of the map has changed.
    The new value is tilt.'''
    
    centerChanged = pyqtSignal(GeoCoordinate)
    '''This signal is emitted when the center of the map has changed.

    The new value is \a coordinate.'''
    
    mapTypeChanged = pyqtSignal(int)
    '''This signal is emitted when the type of the map has changes.
    The value is \a mapType.'''
    
    connectivityModeChanged = pyqtSignal(int)
    '''This signal is emitted when the connectivity mode used to fetch the
    map data has changed. The new value is connectivityMode.'''
    
    updateMapDisplay = pyqtSignal(QRectF)
    '''This signal is emitted when the region target of the window which
    contains the map needs to be updated.
    If target is empty then the entire map will be updated.'''
    
    
    
    def __init__(self, engine):
        QObject.__init__(self, None)
        self._engine = engine
        if len(engine.supportedConnectivityModes()) > 0:
            self.setConnectivityMode(engine.supportedConnectivityModes()[0])
        else:
            self.setConnectivityMode(GraphicsGeoMap.NoConnectivity)
        self._windowSize = QSizeF()
        
    
    
    def init(self):
        '''
        This function is run after the GeoMapData instance has been
        constructed.
    
        Any subclasses which override this function should make sure that
        GeoMapData.init() is called within the body of the overriding function.
        '''
        self._containerObject = GeoMapGroupObject()
        self._containerObject.setMapData(self)
    
    def engine(self):
        '''
        Returns the mapping engine that this map data object is associated with.
        @return: GeoMappingManagerEngine
        '''
        return self._engine
    
    def containerObject(self):
        '''
        Returns the GeoMapObject which acts as the parent to all QGeoMapObject
        instances which are added to the map by the user.
        
        @return: GeoMapObject 
        '''
        return self._containerObject
    
    def setWindowSize(self, size):
        '''
        Sets the size of the map viewport to size.

        The size will be adjusted by the associated QGraphicsGeoMap as it resizes.
        
        @param size: The new size
        @type size: QSizeF
        '''
        if self._windowSize == size:
            return
        self._windowSize = size
        
        if not self.__blockPropertyChangeSignals:
            self.windowSizeChanged.emit(self._windowSize)
    
    def windowSize(self):
        '''
        Returns the size of the map viewport.

        The size will be adjusted by the associated QGraphicsGeoMap as it resizes.
        @return: QSizeF
        '''
        return self._windowSize
    
    def setZoomLevel(self, zoomLevel):
        '''
        Sets the zoom level of the map to zoomLevel.

        Larger values of the zoom level correspond to more detailed views of the
        map.
    
        If zoomLevel is less than minimumZoomLevel() then minimumZoomLevel()
        will be used, and if zoomLevel is  larger than
        maximumZoomLevel() then maximumZoomLevel() will be used.
        
        @param zoomLevel: The zoomLevel
        @type zoomLevel: float
        '''
        zoomLevel = float(zoomLevel)
        zoomLevel = min(zoomLevel, self._engine.maximumZoomLevel())
        zoomLevel = max(zoomLevel, self._engine.minimumZoomLevel())
        
        if self._zoomLevel == zoomLevel:
            return
        
        self._zoomLevel = zoomLevel
        if not self.__blockPropertyChangeSignals:
            self.zoomLevelChanged.emit(self._zoomLevel)
    
    def zoomLevel(self):
        '''
        Returns the zoom level of the map.

        Larger values of the zoom level correspond to more detailed views of the
        map.
        
        @return: float 
        '''
        return self._zoomLevel
    
    def supportsBearing(self):
        '''
        Returns whether bearing is supported by this engine.
        
        @return: bool
        '''
        return self._engine.supportsBearing()
    
    def setBearing(self, bearing):
        '''
        Sets the bearing of the map to \a bearing.

        Value in degrees in the range of 0-360. 0 being equivalent to 0 degrees from
        north.
        
        @param bearing: The bearing
        @type bearing: int
        '''
        if not self.supportsBearing():
            return
        
        bearing = min(bearing, 360)
        bearing = max(bearing, 0)
        
        self._bearing = bearing
        
        if not self.__blockPropertyChangeSignals:
            self.bearingChanged.emit(self._bearing)
    
    def bearing(self):
        '''
        Returns the current bearing of the map.

        Value in degrees in the range of 0-360. 0 being equivalent to 0 degrees from
        north.
        
        @return: int
        '''
        return self._bearing
    
    def supportsTilting(self):
        '''
        Returns whether tilting is supported by this engine.
        
        @return: bool
        '''
        return self._engine.supportsTilting()
    
    def minimumTilt(self):
        '''
        Returns minimum tilt supported by this engine.
        
        @return: int
        '''
        return self._engine.minimumTilt()
    
    def maximumTilt(self):
        '''
        Returns maximum tilt supported by this engine.
        
        @return: int
        '''
        return self._engine.maximumTilt()
    
    def setTilt(self, tilt):
        '''
        Sets the tilt of the map to tilt.

        Value in degrees where 0 is equivalent to 90 degrees between view and earth's
        surface i.e. looking straight down to earth.
    
        If tilt is less than minimumTilt() then minimumTilt()
        will be used, and if tilt is  larger than
        maximumTilt() then maximumTilt() will be used.
        
        @param tilt: The tilt
        @type tilt: int
        '''
        if not self.supportsTilting():
            return
        
        tilt = min(tilt, self._engine.maximumTilt())
        tilt = max(tilt, self._engine.minimumTilt())
        
        if self._tilt == tilt:
            return
        
        self._tilt = tilt
        
        if not self.__blockPropertyChangeSignals:
            self.tiltChanged.emit(self._tilt)
    
    def tilt(self):
        '''
        Returns the current tilt of the map.

        Value in degrees where 0 is equivalent to 90 degrees between view and earth's
        surface i.e. looking straight down to earth.
        
        @return: int
        '''
        return self._tilt
    
    def pan(self, dx, dy):
        '''
        Pans the map view dx pixels in the x direction and dy pixels
        in the y direction.
    
        The x and y axes are specified in Graphics View Framework coordinates.
        By default this will mean that positive values of dx move the
        viewed area to the right and that positive values of dy move the
        viewed area down.
    
        Subclasses should call QGeoMapData::setCenter() when the pan has completed.
        
        @param dx: The x panning
        @type dx: int
        @param dy: The y panning
        @type dy: int
        '''
        pos = self.coordinateToScreenPosition(self.center())
        self.setCenter(self.screenPositionToCoordinate(QPointF(pos.x() + dx,
                                                               pos.y() + dy)))
    
    def setCenter(self, center):
        '''
        Centers the map viewport on the coordinate \a center.
        
        @param center: The center coord
        @type center: GeoCoordinate
        '''
        if self._center == center:
            return
        self._center = center
        
        if not self.__blockPropertyChangeSignals:
            self.centerChanged.emit(self._center)
    
    def center(self):
        '''
        Returns the coordinate of the point in the center of the map viewport.
        
        @return: GeoCoordinate
        '''
        return self._center
    
    def setMapType(self, mapType):
        '''
        Changes the type of map data to display to mapType.
        
        @param mapType: The mapType
        @type mapType: int
        '''
        if self._mapType == mapType:
            return
        
        self._mapType = mapType
        
        if not self.__blockPropertyChangeSignals:
            self.mapTypeChanged.emit(self._mapType)
    
    def mapType(self):
        '''
        Returns the type of map data which is being displayed.
        
        @return: int
        '''
        return self._mapType
    
    def setConnectivityMode(self, mode):
        '''
        Changes the connectivity mode of this map to connectivityMode

        @param mode: The ConnectivityMode
        @type mode: int
        '''
        if self._connectivityMode == mode:
            return
        
        self._connectivityMode = mode
        
        if not self.__blockPropertyChangeSignals:
            self.connectivityModeChanged.emit(self._connectivityMode)
    
    def connectivityMode(self):
        '''
        Returns the connectivity mode for this map.
        
        @return: int
        '''
        return self._connectivityMode
    
    def mapObjects(self):
        '''
        Returns the map objects associated with this map.
        
        @return: list
        '''
        return self._containerObject.childs
    
    def addMapObject(self, mapObject):
        '''
        Adds mapObject to the list of map objects managed by this map.

        The children objects are drawn in order of the QGeoMapObject::zValue()
        value.  Children objects having the same z value will be drawn
        in the order they were added.
    
        The map will take ownership of the mapObject.
        
        @param mapObject: The GeoMapObject to be added
        @type mapObject: GeoMapObject
        '''
        self._addObject(mapObject)
    
    def removeMapObject(self, mapObject):
        '''
        Removes mapObject from the list of map objects managed by this map.
        The map will release ownership of the mapObject.
        
        @param mapObject: The GeoMapObject which will be deleted
        @type mapObject: GeoMapObject
        '''
        self._removeObject(mapObject)
    
    def clearMapObjects(self):
        '''
        Clears the map objects associated with this map.

        The map objects will be deleted.
        '''
        self._clearObjects()
    
    def viewport(self):
        '''
        Returns a bounding box corresponding to the physical area displayed
        in the viewport of the map.
    
        The bounding box which is returned is defined by the upper left and
        lower right corners of the visible area of the map.
        
        @return: GeoBoundingBox
        '''
        raise NotImplementedError('Please implement viewport()')
    
    def fitInViewport(self, bounds, preserveViewportCenter=False):
        '''
        Attempts to fit the bounding box bounds into the viewport of the map.

        This method will change the zoom level to the maximum zoom level such
        that all of bounds is visible within the resulting viewport.
    
        If preserveViewportCenter is false the map will be centered on the
        bounding box bounds before the zoom level is changed, otherwise the
        center of the map will not be changed.
        
        @param bounds: The bounds
        @type bounds: GeoBoundingBox
        @param preserveViewportCenter: Preserve or not
        @type preserveViewportCenter: bool
        '''
        raise NotImplementedError('Please implement fitInViewport()')
    
    def mapObjectsAtScreenPosition(self, screenPosition):
        '''
        Returns the list of visible map objects managed by this map which
        contain the point \a screenPosition within their boundaries.
        
        @param screenPosition: The position on screen
        @type screenPosition: QPointF
        @return: list
        '''
        results = []
        coord = self.screenPositionToCoordinate(screenPosition)
        childObjectCount = len(self._containerObject.childs)
        
        for i in range(childObjectCount):
            obj = self._containerObject.childObjects[i]
            if obj.contains(coord) and obj.isVisible():
                results.append(obj)
            
        return results
    
    def mapObjectsInScreenRect(self, screenRect):
        '''
        Returns the list of visible map objects managed by this map which are displayed at
        least partially within the on screen rectangle screenRect.
        
        @param screenRect: The screenRect
        @type screenRect: QRectF
        '''
        results = []
        
        topLeft = self.screenPositionToCoordinate(screenRect.topLeft())
        bottomRight = self.screenPositionToCoordinate(screenRect.bottomRight())
        
        bounds = GeoBoundingBox(topLeft, bottomRight)
        childObjectCount = len(self._containerObject.childs)
        
        for i in range(childObjectCount):
            obj = self._containerObject.childs[i]
            if bounds.intersects(obj.boundingBox()) and object.isVisible():
                results.append(obj)
        
        return results
    
    def mapObjectsInViewport(self):
        '''
        Returns the list of visible map objects manager by this widget which
        are displayed at least partially within the viewport of the map.
        
        @return list
        '''
        return self.mapObjectsInScreenRect(QRectF(0.0,
                                                  0.0,
                                                  self._windowSize.width(),
                                                  self._windowSize.height()))
    
    def coordinateToScreenPosition(self, coordinate):
        '''
        Returns the position on the screen at which \a coordinate is displayed.

        An invalid QPointF will be returned if \a coordinate is invalid or is not
        within the current viewport.
        
        @param coordinate: The coordinate to translate
        @type coordinate: GeoCoordinate
        @return: QPointF
        '''
        raise NotImplementedError("Please implement coordinateToScreenPosition()")
    
    def screenPositionToCoordinate(self, screenPosition):
        '''
        Returns the coordinate corresponding to the point in the viewport at \a
        screenPosition.
    
        An invalid QGeoCoordinate will be returned if \a screenPosition is invalid
        or is not within the current viewport.
    
        @param screenPosition: The screenpos
        @type screenPosition: QPointF
        @return: GeoCoordinate
        '''
        raise NotImplementedError("Please implement screenPositionToCoordinate()")
    
    def paint(self, painter, option):
        '''
        Paints the map and everything associated with it on \a painter, using the
        options \a option.
    
        This will paint the map with paintMap(), then the map overlays with
        QGeoMapOverlay::paint(), then the map objects with paintObjects(), and
        finally paintProviderNotices().
    
        @param painter: The painter
        @type painter: QPainter
        @param option: The styleoption
        @type option: QStyleOptionGraphicsItem
        '''
        #print "GeoMapData.paint", time.time()
        self.paintMap(painter, map)
        
        for i in range(len(self._overlays)):
            self._overlays[i].paint(painter, option)
        
        self.paintObjects(painter, option)
        
        self.paintProviderNotices(painter, option)
    
    def paintMap(self, painter, option):
        '''
        Paints the map on painter, using the options option.

        The map overlays, map objects and the provider notices (such as copyright
        and powered by notices) are painted in separate methods, which are combined
        in the paint() method.
    
        The default implementation does not paint anything.
        @param painter: The painter
        @type painter: QPainter
        @param option: The StyleOption
        @type option: QStyleOptionGraphicsItem
        '''
        pass
    
    def paintObjects(self, painter, option):
        '''
        Paints the map objects on painter, using the options option.

        The default implementation makes use of the coordinateToScreenPosition
        implemented by the subclass to perform object positioning and rendering.
    
        This implementation should suffice for most common use cases, and supports
        the full range of coordinate systems and transforms available to a
        QGeoMapObject.
        
        @param painter: The painter
        @type painter: QPainter
        @param option: The StyleOption
        @type option: QStyleOptionGraphicsItem
        '''
        pass
    
    def paintProviderNotices(self, painter, option):
        '''
        Paints the provider notices on \a painter, using the options \a option.

        The provider notices are things like the copyright and powered by notices.
    
        The provider may not want the client developers to be able to move the
        notices from their standard positions and so we have not provided API
        support for specifying the position of the notices at this time.
    
        If support for hinting at the position of the notices is to be provided by
        plugin parameters, the suggested parameter keys are
        "mapping.notices.copyright.alignment" and
        "mapping.notices.poweredby.alignment", with type Qt::Alignment.
    
        The default implementation does not paint anything.
        
        @param painter: The painter
        @type painter: QPainter
        @param option: The StyleOption
        @type option: QStyleOptionGraphicsItem
        '''
        pass
    
    def createMapObjectInfo(self, obj):
        '''
        Creates a QGeoMapObjectInfo instance which implements the behaviours o
        the map object \a object which are specific to this QGeoMapData.
    
        The default implementation returns None.
        
        @param obj: The MapObject
        @type obj: GeoMapObject
        '''
        return None
    
    def mapOverlays(self):
        '''
        Returns the map overlays associated with this map.
        @return: list
        '''
        return self._overlays
    
    def addMapOverlay(self, overlay):
        '''
        Adds overlay to the list of map overlays associated with this map.

        The overlays will be drawn in the order in which they were added.
    
        The map will take ownership of overlay.
        
        @param overlay: The overlay to add
        @type overlay: GeoMapOverlay
        '''
        if not overlay:
            return
        overlay.setMapData(self)
        self._overlays.append(overlay)
    
    def removeMapOverlay(self, overlay):
        '''
        Removes overlay from the list of map overlays associated with this map.

        The map will release ownership of overlay.
        
        @param overlay: The overlay to remove
        @type overlay: GeoMapOverlay
        '''
        if not overlay:
            return
        
        self._overlays.remove(overlay)
    
    def clearMapOverlays(self):
        '''
        Clears the map overlays associated with this map.

        The map overlays will be deleted.
        '''
        for overlay in self._overlays:
            del overlay
        
        self._overlays = []
    
    def setBlockPropertyChangeSignals(self, block):
        '''
        Sets whether changes to properties will trigger their corresponding signals to \a block.

        By default the QGeoMapData implementations of the property functions are used
        which cause the property notification signals to be emitted immediately.
    
        Calling this function with \a block set to true will prevent these
        signals from being called, which will allow a subclass to defer the
        emission of the signal until a later time.
    
        If this function needs to be called it should be used as soon as possible,
        preferably in the constructor of the QGeoMapData subclass.
        
        @param block: Block or not
        @type block: bool
        '''
        self.__blockPropertyChangeSignals = block
    
    def _addObject(self, obj):
        '''
        @param obj: Obj, what else?
        @type obj: GeoMapObject
        '''
        self._containerObject.addChildObject(obj)
    
    def _removeObject(self, obj):
        '''
        @param obj: The obj to remove
        @type obj: GeoMapObject
        '''
        self._containerObject.removeChildObject(obj)
    
    def _clearObjects(self):
        for obj in self._containerObject.childs:
            self._removeObject(obj)
            del obj
            
    def emitUpdateDisplay(self, rect=QRectF()):
        self.updateMapDisplay.emit(rect)
    
    def _updateMapDisplay(self, rect=QRectF()):
        self.updateMapDisplay.emit(rect)