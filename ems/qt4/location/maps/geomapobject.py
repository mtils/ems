'''
Created on 13.10.2011

@author: michi
'''
from PyQt4.QtCore import QObject, pyqtSignal

from ems.qt4.location.geoboundingbox import GeoBoundingBox #@UnresolvedImport
from geomapobjectinfo import GeoMapObjectInfo #@UnresolvedImport
from ems.qt4.location.geocoordinate import GeoCoordinate #@UnresolvedImport

class GeoMapObject(QObject):
    '''
    The QGeoMapObject class is a graphical item to be displayed on a map.
    
    QGeoMapObject is the base class used to display graphical items on a map.

    Subclasses of QGeoMapObject exist in order to simplify the task of
    creating and managing map objects of various kinds.

    QGeoMapCustomObject is the most generic of these objects in that it
    allows QGraphicsItems to be added to a map, however as not all mapping
    plugins use the Qt Graphics View framework so clients should use
    QGraphicsGeoMap::supportsCustomMapObjects() before using
    QGeoMapCustomObject.

    QGeoMapObject instances can also be grouped into heirarchies in order to
    simplify the process of creating compound objects and managing groups of
    objects (see QGeoMapGroupObject)
    '''
    
    '''Enum Type: Describes the type of a map object.'''
    
    zValueChanged = pyqtSignal(int)
    '''This signal is emitted when the z value of the map object
    has changed.

    The new value is zValue.'''
    
    visibleChanged = pyqtSignal(bool)
    '''This signal is emitted when the visible state of the map object
    has changed.

    The new value is visible.'''
    
    selectedChanged = pyqtSignal(bool)
    '''This signal is emitted when the selected state of the map object
    has changed.

    The new vlaue is selected.'''
    
    originChanged = pyqtSignal(GeoCoordinate)
    '''This signal is emitted when the origin of the map object has changed.

    The new value is origin.'''
    
    transformTypeChanged = pyqtSignal(int)
    '''This signal is emitted when the transform type of the map object has changed.

    The new value is transformType.'''
    
    unitsChanged = pyqtSignal(int)
    '''This signal is emitted when the coordinate units of the map object have changed.

    The new value is units.'''
    
    NullType = 0
    #An empty QGeoMapObject.
    GroupType = 1
    #A QGeoMapObject used to organize other map objects into groups.
    RectangleType = 2
    #A QGeoMapObject used to display a rectangular region.
    CircleType = 3
    #A QGeoMapObject used to display a circular region.
    PolylineType = 4
    #A QGeoMapObject used to display a multi-segment line.
    PolygonType = 5
    #A QGeoMapObject used to display a polygonal region.
    PixmapType = 6
    #A QGeoMapObject used to display a pixmap on a map.
    TextType = 7
    #A QGeoMapObject used to display text on a map
    RouteType = 8
    #A QGeoMapObject used to display a route.
    CustomType = 9
    #A QGeoMapObject displaying a custom GraphicsItem.
    
    '''Enum CoordinateUnit: Describes the units of measurement used for a map object's
    graphics item.'''
    PixelUnit = 0
    '''Units are in pixels on the screen. Pixel coordinate (0,0) is
        translated to the origin coordinate.'''
    MeterUnit = 1
    '''Units are in meters on the ground -- a local Transverse Mercator
        coordinate system (on the WGS84 ellipsoid) is used for translation,
        centered on the origin coordinate.'''
    RelativeArcSecondUnit = 2
    '''Units are in arc seconds relative to the origin coordinate (along the
        WGS84 ellipsoid).'''
    AbsoluteArcSecondUnit = 3
    '''Units are in arc seconds on WGS84, origin ignored.'''
    
    ''' Enum TransformType: Describes the type of transformation applied to change this object's
    coordinate system into screen coordinates.'''
    BilinearTransform = 0
    '''This object's bounding box is taken, and transformed at each of its
        corners into screen coordinates. A bilinear interpolation is then used
        to draw the rest of the object's GraphicsItem.'''
    ExactTransform = 1
    '''Individual key points on the object are transformed and the GraphicsItem
        is constructed in direct pixel coordinates. This is only available for
        certain subclasses, depending on the implementation of QGeoMapData used.'''
    
    
    _zValue = 0
    _visible = True
    _selected = False
    _mapData = None
    _info = None
    _transformType = 1
    _origin = None
    _units = 0
    
    serial = 0
    
    def __init__(self, mapData=None):
        '''
         Constructs a new map object associated with \a mapData.

        The object will be in pixel coordinates, with exact transform.
        
        @param mapData: The mapData
        @type mapData: GeoMapData
        '''
        QObject.__init__(self, None)
        
        self._zValue = 0
        self._visible = True
        self._selected = False
        self._mapData = None
        self._info = None
        self._transformType = 1
        self._origin = None
        self._units = 0
        
        serial = 0
        
        if mapData is not None:
            self.setMapData(mapData)
        
        
    
    def type_(self):
        '''
        Returns the type of this map object.
        
        @return: int
        '''
        return self.NullType
    
    def setZValue(self, zValue):
        '''
        This property holds the z-value of the map object.

        The z-value determines the order in which the objects are drawn on the
        screen.  Objects with the same value will be drawn in the order that
        they were added to the map or map object.
    
        This is the same behaviour as QGraphicsItem.
        
        @param zValue: The z val
        @type zValue: int
        '''
        if self._zValue != zValue:
            self._zValue = zValue
            self.zValueChanged.emit(self._zValue)
    
    def zValue(self):
        '''
        Returns the zValue
        @see setZValue
        @return: int
        '''
        return self._zValue
    
    def setVisible(self, visible):
        '''
        This property holds whether the map object is visible.
        
        @param visible: Visibility
        @type visible: bool
        '''
        if self._visible != visible:
            self._visible = visible
            
            self.visibleChanged.emit(self._visible)
    
    def isVisible(self):
        '''
        @see setVisible()
        @return: bool
        '''
        return self._visible
    
    def setSelected(self, selected):
        '''
        This property holds whether the map object is selected.
        
        @param selected: Selected or not thats the question
        @type selected: bool
        '''
        if self._selected != selected:
            self._selected = selected
            self.selectedChanged.emit(self._selected)
    
    def isSelected(self):
        '''
        @see setSelected()
        @return: bool
        '''
        return self._selected
    
    def boundingBox(self):
        '''
        Returns a bounding box which contains this map object.

        The default implementation requires the object to be added to a map
        before this function returns a valid bounding box.
        @return GeoBoundingBox
        '''
        if not self._info:
            return GeoBoundingBox()
        return self._info.boundingBox()
    
    def contains(self, coordinate):
        '''
        Returns whether \a coordinate is contained with the boundary of this
        map object.
    
        The default implementation requires the object to be added to a map
        before this function is able to return true.
        
        @param coordinate: The coord
        @type coordinate: GeoCoordinate
        '''
        if not self._info:
            return False
        return self._info.contains(coordinate)
    
    def __lt__(self, other):
        '''
        self < other
        
        internal!
        
        @param other: The right operand
        @type other: GeoMapObject
        '''
        return self._zValue < other.zValue() or\
               (self._zValue == other.zValue and self.serial < other.serial)
        
    def __gt__(self, other):
        '''
        self > other
        
        internal!
        
        @param other: The right operand
        @type other: GeoMapObject
        '''
        return self._zValue > other.zValue() or\
               (self._zValue == other.zValue() and self.serial > other.serial)
    
    def setMapData(self, mapData):
        '''
        Associates the QGeoMapData instance mapData with this map object.

        This will create an appropriate QGeoMapObjectInfo instance for
        this QGeoMapObject and will connect the appropriate signals to it
        so that it can be kept up to date.
        
        @param mapData: The associated GeoMapData Object
        @type mapData: GeoMapData
        '''
        
        if self._mapData is mapData:
            return
        
        if self._info:
            del self._info
            self._info = None
        
        self._mapData = mapData
        
        if not self._mapData:
            return
        
        self._info = mapData.createMapObjectInfo(self)
        
        if not self._info:
            return
        
        self._mapData.windowSizeChanged.connect(self._info.windowSizeChanged)
        self._mapData.zoomLevelChanged.connect(self._info.zoomLevelChanged)
        self._mapData.centerChanged.connect(self._info.centerChanged)
        
        self.zValueChanged.connect(self._info.zValueChanged)
        self.visibleChanged.connect(self._info.visibleChanged)
        self.selectedChanged.connect(self._info.selectedChanged)
        self.originChanged.connect(self._info.originChanged)
        self.transformTypeChanged.connect(self._info.transformTypeChanged)
        self.unitsChanged.connect(self._info.unitsChanged)
        
        self._info.init()
    
    def mapData(self):
        '''
        Returns the QGeoMapData instance associated with this object.

        Will return None if not QGeoMapData instance has been set.
        @return: GeoMapData
        '''
        return self._mapData
    
    def info(self):
        '''
        Returns the QGeoMapObjectInfo instance which implements the
        QGeoMapData specific behaviours of this map object.
    
        This will mostly be useful when implementing custom QGeoMapData
        subclasses.
        
        @return: GeoMapObjectInfo
        '''
        return self._info
    
    def transformType(self):
        '''
        This property holds the transformation type used to draw the object.
        
        @return: int
        '''
        return self._transformType
    
    def setTransformType(self, transformType):
        '''
        @see transformType
        
        @param transformType: the type
        @type transformType: int
        '''
        if transformType == self._transformType:
            return
        self._transformType = transformType
        self.transformTypeChanged.emit(self._transformType)
    
    def origin(self):
        '''
        This property holds the origin of the object's coordinate system.
    
        How the origin coordinate is used depends on the selected coordinate
        system, see GeoMapObject.TransformType for more details.
        
        @return: GeoCoordinate
        '''
        return self._origin
    
    def setOrigin(self, origin):
        '''
        Sets the origin of the object to \a origin.
        
        @param origin: The origin
        @type origin: GeoCoordinate
        '''
        if origin == self._origin:
            return
        self._origin = origin
        self.originChanged.emit(self._origin)
    
    def units(self):
        '''
        This property holds the units of measurement for the object.
        @return int
        '''
        return self._units
    
    def setUnits(self, unit):
        '''
        Sets the coordinate units of the object to unit.

        Note that setting this property will reset the transformType property to
        the default for the units given. For PixelUnit, this is ExactTransform,
        and for all others, BilinearTransform.
        
        @param units: The units
        @type units: int
        '''
        if unit == self._units:
            return
    
        self._units = unit
    
        if unit == GeoMapObject.PixelUnit:
            self.setTransformType(GeoMapObject.ExactTransform)
        else:
            self.setTransformType(GeoMapObject.BilinearTransform)
    
        self.unitsChanged.emit(unit)
    
    