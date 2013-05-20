'''
Created on 13.10.2011

@author: michi
'''
import time

from PyQt4.QtCore import pyqtSignal, QSizeF, QPointF, QRectF
from PyQt4.QtGui import QGraphicsWidget, QPainterPath

from ems.qt4.location.geocoordinate import GeoCoordinate #@UnresolvedImport
from ems.qt4.location.geoboundingbox import GeoBoundingBox #@UnresolvedImport


class GraphicsGeoMap(QGraphicsWidget):
    '''
    class QGraphicsGeoMap
    The QGraphicsGeoMap class is used to display a map and manager the
    interactions between the user and the map.
    
    Most of the functionality is provided by QGeoMappingManager, which
    handles most aspects of the display.

    The map viewport can be panned, the zoom level can be changed and the
    center coordinate of the viewport can be set explicitly.

    The screenPositionToCoordinate() and coordinateToScreenPoisition()
    functions can be used to convert between positions on the screen and
    global coordinates.

    Mouse and keyboard events should be handled by subclassing QGraphicsGeoMap
    and providing implementations of the event handling functions present in
    QGraphicsWidget.
    '''
    
    #MapType Enum
    
    NoMap = 0
    
    StreetMap = 1
    
    SatelliteMapDay = 2
    
    SatelliteMapNight = 3
    
    TerrainMap = 4
    
    #ConnectivityMode Enum
    
    NoConnectivity = 0
    
    OfflineMode = 1
    
    OnlineMode = 2
    
    HybridMode = 3
    
    zoomLevelChanged = pyqtSignal(float)
    centerChanged = pyqtSignal(GeoCoordinate)
    mapTypeChanged = pyqtSignal(int)
    connectivityModeChanged = pyqtSignal(int)
    bearingChanged = pyqtSignal(float)
    tiltChanged = pyqtSignal(float)
    
    panActive = False
    
    def __init__(self, manager, parent=None):
        '''
        Creates a new mapping widget, with the mapping operations managed by
        manager, and the specified parent.
    
        Note that the manager will typically be accessed from an instance of
        QGeoServiceProvider:
        <code>
            QGeoServiceProvider serviceProvider("nokia");
            QGeoMappingManager *manager = serviceProvider.mappingManager();
            QGraphicsGeoMap *widget = new QGraphicsGeoMap(manager);
        </code>
        
        @param manager: The GeoMappingManager
        @type manager: GeoMappingManager
        @param parent: The parent GraphicsItem
        @type parent: QGraphicsItem
        '''
        QGraphicsWidget.__init__(self, parent)
        
        self.manager = manager
        
        self.mapData = self.manager.createMapData()
        self.mapData.init() 
        
        #self.connect(self.mapData.)
        self.mapData.updateMapDisplay.connect(self.updateMapDisplay)
        
        self.setMapType(self.StreetMap)
        
        self.mapData.setWindowSize(self.size())
        #self.mapData.setWindowSize(QSizeF(500,500))
        
        self.mapData.zoomLevelChanged.connect(self.zoomLevelChanged)
        self.mapData.bearingChanged.connect(self.bearingChanged)
        self.mapData.tiltChanged.connect(self.tiltChanged)
        self.mapData.mapTypeChanged.connect(self.mapTypeChanged)
        self.mapData.centerChanged.connect(self.centerChanged)
        self.mapData.connectivityModeChanged.connect(self.connectivityModeChanged)
        
        self.setFlag(self.ItemIsFocusable)
        self.setFocus()
        
        self.setMinimumSize(QSizeF(0,0))
        self.setPreferredSize(QSizeF(500,500))
    
    def resizeEvent(self, event):
        '''
        Reimplemented method
        
        @param event: The ResiveEvent
        @type event: QGraphicsSceneResizeEvent
        '''
        if self.mapData:
            self.mapData.setWindowSize(event.newSize())
    
    def shape(self):
        '''
        @return: QPainterPath
        '''
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path
    
    def paint(self, painter, option, widget=None):
        '''
        Delegates Painting to self.mapData
        
        @param painter: The Painter
        @type painter: QPainter
        @param option: Style Options
        @type option: QStyleOptionGraphicsItem
        @param widget: No Idea
        @type widget: QWidget
        '''
        
        try:
            self.mapData.paint(painter, option)
        except AttributeError:
            pass
    
    def updateMapDisplay(self, target):
        '''
        Updates the map
        
        @param target: The target rect
        @type target: QRectF
        '''
        #starttime = time.time()
        #print "GraphicsGeoMap.updateMapDisplay({0})".format(target)
        #self.update()
        try:
            if isinstance(target, QRectF) and target.isValid():
                self.update(target)
            else:
                self.update()
        except RuntimeError: #Obj deletion Problems
            pass
        
        #print "GraphicsGeoMap.updateMapDisplay and {0}".format(time.time() - starttime)
    
    def minimumZoomLevel(self):
        '''This property holds the minimum zoom level supported by the
        QGeoMappingManager associated with this widget.

        Larger values of the zoom level correspond to more detailed views of the
        map.
        
        @return float
        
        '''
        if self.manager:
            return self.manager.minimumZoomLevel()
        
        return -1
    
    def maximumZoomLevel(self):
        '''
        This property holds the maximum zoom level supported by the
        QGeoMappingManager associated with this widget.

        Larger values of the zoom level correspond to more detailed views of the
        map.
        
        @return: float
        '''
        if self.manager:
            return self.manager.maximumZoomLevel()
        
        return -1
    
    def setZoomLevel(self, zoomLevel):
        '''
        This property holds the zoom level of the map.

        Larger values of the zoom level correspond to more detailed views of the
        map.
    
        If zoomLevel is less than minimumZoomLevel then minimumZoomLevel
        will be used, and if zoomLevel is  larger than
        maximumZoomLevel then maximumZoomLevel will be used.
    
        @param zoomLevel: The Level to zoom
        @type zoomLevel: float
        '''
        if self.mapData:
            self.mapData.setZoomLevel(zoomLevel)
    
    def zoomLevel(self):
        '''
        @see: setZoomLevel
        @return float
        '''
        if self.mapData:
            return self.mapData.zoomLevel()
        return -1
    
    def supportsBearing(self):
        '''
        This property holds whether bearing is supported by the
        QGeoMappingManager associated with this widget.
        
        @return bool
        '''
        if self.mapData:
            return self.mapData.supportsBearing()
        return False
    
    def setBearing(self, bearing):
        '''
        This property holds the bearing of the map.

        Value in degrees where 0 is equivalent to 90 degrees between view and earth's
        surface i.e. looking straight down to earth.
        
        @param bearing: Bearing value
        @type bearing: float
        '''
        if self.mapData:
            self.mapData.setBearing(bearing)
        
    def bearing(self):
        '''
        @see setBearing
        @return float
        '''
        if self.mapData:
            return self.mapData.bearing()
        return 0
    
    def supportsTilting(self):
        '''
        This property holds whether tilting is supported by the
        QGeoMappingManager associated with this widget.
        
        @return bool
        '''
        if self.mapData:
            return self.mapData.supportsTilting()
        return False
    
    def minimumTilt(self):
        '''
        This property holds the minimum tilt supported by the
        QGeoMappingManager associated with this widget.
    
        Value in degrees where 0 is equivalent to 90 degrees between view and earth's
        surface i.e. looking straight down to earth.
        
        @return float
        '''
        
        if self.mapData:
            return self.mapData.minimumTilt()
        return 0
    
    def maximumTilt(self):
        '''
        This property holds the maximum tilt supported by the
        QGeoMappingManager associated with this widget.
    
        Value in degrees where 0 is equivalent to 90 degrees between view and earth's
        surface i.e. looking straight down to earth.
        
        @return float
        '''
        if self.mapData:
            return self.mapData.maximumTilt()
        return 0
    
    def setTilt(self, tilt):
        '''
        This property holds the tilt of the map.

        Value in degrees where 0 is equivalent to 90 degrees between view and earth's
        surface i.e. looking straight down to earth.
    
        If tilt is less than minimumTilt() then minimumTilt()
        will be used, and if \a tilt is  larger than
        maximumTilt() then maximumTilt() will be used.
        
        @param tilt: Tilting value
        @type tilt: float
        '''
        if self.mapData:
            self.mapData.setTilt(tilt)
    
    def tilt(self):
        '''
        @see setTilt()
        @return float
        '''
        if self.mapData:
            return self.mapData.tilt()
        return 0
    
    def pan(self, dx, dy):
        '''
        Pans the map view \a dx pixels in the x direction and \a dy pixels
        in the y direction.
        
        The x and y axes are specified in Graphics View Framework coordinates.
        By default this will mean that positive values of \a dx move the
        viewed area to the right and that positive values of \a dy move the
        viewed area down.
        
        After the panning has occurred the centerChanged() signal will be emitted.
        
        @param dx: x Direction
        @type dx: int
        @param dy: y Direction
        @type dy: int
        '''
        
        if self.mapData:
            self.mapData.pan(dx, dy)
            self.update()
    
    def setCenter(self, center):
        '''
        This property holds the coordinate at the center of the map viewport.

        Panning the map can be more efficient than changing the center by small
        increments.
        
        @param center: The center of the map viewport
        @type center: GeoCoordinate
        '''
        
        if self.mapData:
            self.mapData.setCenter(center)
    
    def center(self):
        '''
        @see setCenter
        @return GeoCoordinate
        '''
        if self.mapData:
            return self.mapData.center()
        return GeoCoordinate()
    
    def supportedMapTypes(self):
        '''
        This property holds the type of map data displayed by the map.

        Setting mapType to a type not present in supportedMapTypes() will do
        nothing.
        
        @return: int
        '''
        if self.manager:
            return self.manager.supportedMapTypes()
        return (self.NoMap, self.StreetMap, self.SatelliteMapDay,
                self.SatelliteMapNight, self.TerrainMap)
    
    def setMapType(self, mapType):
        '''
        This property holds the type of map data displayed by the map.
        
        Setting mapType to a type not present in supportedMapTypes() will do
        nothing.
        
        @param mapType: The type of the map
        @type mapType: int
        '''
        if self.mapData and self.manager:
            if not mapType in self.supportedMapTypes():
                return
            self.mapData.setMapType(mapType)
    

    def mapType(self):
        '''
        @see setMapType()
        @return int
        '''
        if self.mapData:
            return self.mapData.mapType()
        return self.NoMap
        
    def supportedConnectivityModes(self):
        '''
        Returns the connectivity modes supported by the QGeoMappingManager associated with
        this widget.
        
        @return tuple
        '''
        if self.manager:
            return self.manager.supportedConnectivityModes()
        
        return (self.NoConnectivity, self.OfflineMode, self.OnlineMode,
                self.HybridMode)
    
    def setConnectivityMode(self, connectivityMode):
        '''
        This property holds the connectivity mode used to obtain the map data.

        Setting connectivityMode to a mode not present in supportedConnectivityModes() will do
        nothing.
        
        @param connectivityMode: Declares how to obtain the data
        @type connectivityMode: int
        '''
        
        if self.mapData and self.manager:
            if connectivityMode not in self.manager.supportedConnectivityModes():
                return
            self.mapData.setConnectivityMode(connectivityMode)
    
    def connectivityMode(self):
        '''
        @see setConnectivityMode
        @return int
        '''
        if self.mapData:
            return self.mapData.connectivityMode
        return self.NoConnectivity
    
    def supportsCustomMapObjects(self):
        '''
        Returns whether custom map objects are supported by this engine.

        Custom map objects are map objects based on QGraphicsItem instances, which
        are hard to support in cases where the map rendering is not being
        performed by the Qt Graphics View framwork.
        
        @return bool
        '''
        
        if self.manager:
            return self.manager.supportsCustomMapObjects()
        return False
    
    def mapObjects(self):
        '''
        Returns the map objects associated with this map.
        '''
        if not self.mapData:
            return ()
        return self.mapData.mapObjects()
    
    def addMapObject(self, mapObject):
        '''
        Adds a mapObject to the list of map objects managed by this widget.

        If a mapObject is within the viewport of the map and
        QGeoMapObject::isVisible() returns true then the map will display the map
        object immediately.
    
        The map will take ownership of the \a mapObject.
    
        If supportsCustomMapObject() returns false and a mapObject is a custom map
        object then a mapObject will not be added to the map.
        
        @param mapObject: The mapobject to add
        @type mapObject: GeoMapObject
        '''
        
        if not mapObject or not self.mapData:
            return
        
        if (mapObject.type_() == mapObject.CustomType) and not \
            self.supportsCustomMapObjects():
            return
        
        self.mapData.addMapObject(mapObject)
        
        self.update()
    
    def removeMapObject(self, mapObject):
        '''
        Removes a mapObject from the list of map objects managed by this widget.

        If a mapObject is within the viewport of the map and
        QGeoMapObject::isVisible() returns true then the map will stop displaying
        the map object immediately.
    
        The map will release ownership of the a mapObject.
        
        @param mapObject: The Object which will be deleted
        @type mapObject: GeoMapObject
        '''

        if not mapObject or not self.mapData:
            return
        self.mapData.removeMapObject(mapObject)
        self.update()
        
    def clearMapObjects(self):
        '''
         Clears the map objects associated with this map.

         The map objects will be deleted.
        '''
        if not self.mapData:
            return
        self.mapData.clearMapObjects()
    
    def mapOverlays(self):
        '''
        Returns the map overlays associated with this map.
        
        @return list
        '''
        if not self.mapData:
            return []
        return self.mapData.mapOverlays()
    
    def addMapOverlay(self, overlay):
        '''
        Adds overlay to the list of map overlays associated with this map.

        The overlays will be drawn in the order in which they were added.
    
        The map will take ownership of overlay.
        
        @param overlay: The overlay which will be added
        @type overlay: GeoMapOverlay
        '''
        if not overlay or not self.mapData:
            return
        
        self.mapData.addMapOverlay(overlay)
        self.update()
    
    def removeMapOverlay(self, overlay):
        '''
        Removes a overlay from the list of map overlays associated with this map.

        The map will release ownership of a overlay.
    
        @param overlay: The overlay to remove
        @type overlay: GeoMapOverlay
        '''
        
        if not overlay or not self.mapData:
            return
        
        self.mapData.removeMapOverlay(overlay)
        
        self.update()
    
    def clearMapOverlays(self):
        '''
        Clears the map overlays associated with this map.
        The map overlays will be deleted.
        '''
        
        if not self.mapData:
            return
        self.mapData.clearMapOverlays()
    
    def viewport(self):
        '''
        Returns a bounding box corresponding to the physical area displayed
        in the viewport of the map.
    
        The bounding box which is returned is defined by the upper left and
        lower right corners of the visible area of the map.
        
        @return GeoBoundingBox
        '''
        if not self.mapData:
            return GeoBoundingBox()
        return self.mapData.viewport()
    
    def fitInViewport(self, bounds, preserveViewportCenter):
        '''
        Attempts to fit the bounding box bounds into the viewport of the map.

        This method will change the zoom level to the maximum zoom level such
        that all of bounds is visible within the resulting viewport.
    
        If preserveViewportCenter is false the map will be centered on the
        bounding box bounds before the zoom level is changed, otherwise the
        center of the map will not be changed.
        
        @param bounds: The bounding box to center in viewport
        @type bounds: GeoBoundingBox
        @param preserveViewportCenter: preserve current center
        @type preserveViewportCenter: bool
        '''
        
        if not self.mapData:
            return
        
        self.mapData.fitInViewport(bounds, preserveViewportCenter)
    
    def mapObjectsAtScreenPosition(self, screenPosition):
        '''
        Returns the list of visible map objects managed by this widget which
        contain the point screenPosition within their boundaries.
        
        @param screenPosition: The position on screen
        @type screenPosition: QPointF
        @return list
        '''
        
        if self.mapData:
            return self.mapData.mapObjectsAtScreenPosition(screenPosition)
        return []
    
    def mapObjectsInScreenRect(self, screenRect):
        '''
        Returns the list of visible map objects managed by this widget which are
        displayed at least partially within the on screen rectangle
        screenRect.
        
        @param screenRect: The screenrect asked for
        @type screenRect: QRectF
        @return list
        '''
        
        if self.mapData:
            return self.mapData.mapObjectsInScreenRect(screenRect)
        
        return []
    
    def mapObjectsInViewport(self):
        '''
        Returns the list of visible map objects manager by this widget which
        are displayed at least partially within the viewport of the map.
        
        @return: list
        '''
        
        if self.mapData:
            return self.mapData.mapObjectsInViewport()
        return []
    
    def coordinateToScreenPosition(self, coordinate):
        '''
        Returns the position on the screen at which coordinate is displayed.

        An invalid QPointF will be returned if coordinate is invalid or is not
        within the current viewport.
        
        
        @param coordinate: The queried coordinate
        @type coordinate: GeoCoordinate
        @return QPointF
        '''
        if self.mapData:
            return self.mapData.coordinateToScreenPosition(coordinate)
        return QPointF()
    
    def screenPositionToCoordinate(self, screenPosition):
        '''
        Returns the coordinate corresponding to the point in the viewport at \a
        screenPosition.
    
        An invalid QGeoCoordinate will be returned if screenPosition is invalid
        or is not within the current viewport.
        
        @param screenPosition: The queried screenposition
        @type screenPosition: QPointF
        @return GeoCoordinate
        '''
        if self.mapData:
            return self.mapData.screenPositionToCoordinate(screenPosition)
        
        return GeoCoordinate()
    
    def clearForDeletion(self):
        self.mapData.clearForDeletion()
        
