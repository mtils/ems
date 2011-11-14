
from PyQt4.QtCore import QObject, QLocale

class GeoMappingManagerEngine(QObject):
    '''
    \brief The QGeoMappingManagerEngine class provides an interface and convenience methods
    to implementors of QGeoServiceProvider plugins who want to provides support for displaying
    and interacting with maps.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps-impl

    Subclasses of QGeoMappingManagerEngine need to provide an implementations
    of createMapData(). The QGeoMapData instances returned by createMapData()
    can be used to contain and manage information concerning what a particular
    QGraphicsGeoMap is viewing.

    Most of the other functions configure the reported capabilities of the engine.
    It is important that these functions are called before createMapData() or any of the
    capability reporting functions are used to prevent incorrect or
    inconsistent behaviour.
    '''
    
    _managerName = unicode()
    
    _managerVersion = -1
    
    _supportedMapTypes = []
    
    _supportedConnectivityModes = []
    
    _minimumZoomLevel = 0.0
    
    _maximumZoomLevel = 0.0
    
    _supportsBearing = False
    
    _supportsTilting = False
    
    _minimumTilt = 0.0
    
    _maximumTilt = 0.0
    
    _supportsCustomMapObjects = False
    
    _locale = QLocale
    
    
    def __init__(self, parameters, parent=None):
        '''
        Constructs a new engine with the specified \a parent, using \a parameters
        to pass any implementation specific data to the engine.
        
        @param parameters:
        @type parameters:
        @param parent:
        @type parent:
        '''
        self._managerVersion = -1
        self._minimumZoomLevel = 0.0
        self._maximumZoomLevel = 0.0
        self._supportsBearing = False
        self._supportsTilting = False
        self._minimumTilt = 0.0
        self._maximumTilt = 0.0
        self._supportsCustomMapObjects = False
        QObject.__init__(self, parent)
    
    def _setManagerName(self, name):
        '''
        Sets the name which this engine implementation uses to distinguish itself
        from the implementations provided by other plugins to \a managerName.
    
        The combination of managerName() and managerVersion() should be unique
        amongst plugin implementations.
        
        @param name: the name
        @type name: basestring
        '''
        self._managerName = name
    
    def managerName(self):
        '''
        Returns the name which this engine implementation uses to distinguish
        itself from the implementations provided by other plugins.
    
        The combination of managerName() and managerVersion() should be unique
        amongst plugin implementations.
        @rtype: basestring
        '''
        return self._managerName
    
    def _setManagerVersion(self, managerVersion):
        '''
        Sets the version of this engine implementation to \a managerVersion.

        The combination of managerName() and managerVersion() should be unique
        amongst plugin implementations.
        
        @param managerVersion: The version
        @type managerVersion: int
        '''
        self._managerVersion = managerVersion
        
    def managerVersion(self):
        '''
        Returns the version of this engine implementation.

        The combination of managerName() and managerVersion() should be unique
        amongst plugin implementations.
        @rtype: int
        '''
        return self._managerVersion
    
    def createMapData(self):
        '''
        QGeoMapData* QGeoMappingManagerEngine::createMapData()

        Returns a new QGeoMapData instance which will be managed by
        this manager.
    
        A QGeoMapData instance contains and manages the information about
        what a QGraphicsGeoMap is looking at.  A  single manager can be used by several
        QGraphicsGeoMap instances since each instance has an associated QGeoMapData instance.
    
        The QGeoMapData instance can be treated as a kind of session object, or
        as a model in a model-view-controller architecture, with QGraphicsGeoMap
        as the view and QGeoMappingManagerEngine as the controller.
    
        Subclasses of QGeoMappingManagerEngine are free to override this function
        to return subclasses of QGeoMapData in order to customize the
        map.
        '''
        raise NotImplementedError("Please implement createMapData()")
    
    def supportedMapTypes(self):
        '''
        Returns a list of the map types supported by this engine.
        @rtype: list
        '''
        return self._supportedMapTypes
    
    def supportedConnectivityModes(self):
        '''
        Returns a list of the connectivity modes supported by this engine.
        @rtype: list
        '''
        return self._supportedConnectivityModes
    
    def minimumZoomLevel(self):
        '''
        Returns the minimum zoom level supported by this engine.

        Larger values of the zoom level correspond to more detailed views of the
        map.
        @rtype: float
        '''
        return self._minimumZoomLevel
    
    def maximumZoomLevel(self):
        '''
         Returns the maximum zoom level supported by this engine.

        Larger values of the zoom level correspond to more detailed views of the
        map.
        @rtype: float
        '''
        return self._maximumZoomLevel
    
    def _setSupportedMapTypes(self, mapTypes):
        '''
        Sets the list of map types supported by this engine to \a mapTypes.
    
        Subclasses of QGeoMappingManagerEngine should use this function to ensure
        that supportedMapTypes() provides accurate information.
        
        @param mapTypes: the new supported MapTypes
        @type mapTypes: list
        '''
        self._supportedMapTypes = mapTypes
    
    def _setSupportedConnectivityModes(self, connectivityModes):
        '''
        Sets the list of connectivity modes supported by this engine to \a connectivityModes.

        Subclasses of QGeoMappingManagerEngine should use this function to ensure
        that supportedConnectivityModes() provides accurate information.
    
        If createMapData does not specify a connectivity mode the first mode from
        \a connectivityModes will be used, or QGraphicsGeoMap::NoConnectivity will
        be used if \a connectivityModes is empty.
        
        @param connectivityModes: The new connectivityModes
        @type connectivityModes: list
        '''
        self._supportedConnectivityModes = connectivityModes
    
    def _setMinimumZoomLevel(self, minimumZoomLevel):
        '''
        Sets the minimum zoom level supported by this engine to \a minimumZoom.

        Larger values of the zoom level correspond to more detailed views of the
        map.
    
        Subclasses of QGeoMappingManagerEngine should use this function to ensure
        minimumZoomLevel() provides accurate information.
        
        @param minimumZoomLevel: The new minimumZoomLevel
        @type minimumZoomLevel: float
        '''
        self._minimumZoomLevel = minimumZoomLevel
    
    def _setMaximumZoomLevel(self, maximumZoom):
        '''
        Sets the maximum zoom level supported by this engine to \a maximumZoom.

        Larger values of the zoom level correspond to more detailed views of the
        map.
    
        Subclasses of QGeoMappingManagerEngine should use this function to ensure
        maximumZoomLevel() provides accurate information.
        
        @param maximumZoom: The new maxZoom
        @type maximumZoom: float
        '''
        self._maximumZoomLevel = maximumZoom
    
    def supportsBearing(self):
        '''
        Return whether bearing is supported by this engine.
        @rtype: bool
        '''
        return self._supportsBearing
    
    def supportsTilting(self):
        '''
        Return whether tilting is supported by this engine.
        @rtype: bool
        '''
        return self._supportsTilting
    
    def minimumTilt(self):
        '''
        Returns the minimum tilt supported by this engine.

        Value in degrees where 0 is equivalent to 90 degrees between view and earth's
        surface i.e. looking straight down to earth.
        @rtype: float
        '''
        return self._minimumTilt
    
    def maximumTilt(self):
        '''
        Returns the maximum tilt supported by this engine.

        Value in degrees where 0 is equivalent to 90 degrees between view and earth's
        surface i.e. looking straight down to earth.
        @rtype: float
        '''
        return self._maximumTilt
    
    def _setMinimumTilt(self, minimumTilt):
        '''
        Sets the minimum tilt supported by this engine to \a minimumTilt.

        Value in degrees where 0 is equivalent to 90 degrees between view and earth's
        surface i.e. looking straight down to earth.
    
        Subclasses of QGeoMappingManagerEngine should use this function to ensure
        minimumTilt() provides accurate information. If no minimum value is set
        by the subclass the value of 0 is used.
        
        @param minimumTilt: the new minimumTilt
        @type minimumTilt: float
        '''
        self._minimumTilt = minimumTilt
    
    def _setMaximumTilt(self, maximumTilt):
        '''
        Sets the maximum tilt supported by this engine to \a maximumTilt.

        Value in degrees where 0 is equivalent to 90 degrees between view and earth's
        surface i.e. looking straight down to earth.
    
        Subclasses of QGeoMappingManagerEngine should use this function to ensure
        maximumTilt() provides accurate information. If no maximum value is set
        by the subclass the value of 0 is used.
        
        @param maximumTilt: The new maximumTilt
        @type maximumTilt: float
        '''
        self._maximumTilt = maximumTilt
    
    def _setSupportsBearing(self, supportsBearing):
        '''
        Sets whether bearing is supported by this engine to \a supportsBearing.

        Subclasses of QGeoMappingManagerEngine should use this function to ensure
        supportsBearing() provides accurate information. If no value is set
        by the subclass then bearing support is disabled and supportsBearing set
        to false.
        
        @param supportsBearing: Support it or not
        @type supportsBearing: bool
        '''
        self._supportsBearing = supportsBearing
    
    def _setSupportsTilting(self, supportsTilting):
        '''
        Sets whether tilting is supported by this engine to \a supportsTilting.

        Subclasses of QGeoMappingManagerEngine should use this function to ensure
        supportsTilting() provides accurate information. If no value is set
        by the subclass then tilting support is disabled and supportsTilting set
        to false.
        
        @param supportsTilting: True is supports, otherwise False
        @type supportsTilting: bool
        '''
        self._supportsTilting = supportsTilting
    
    def supportsCustomMapObjects(self):
        '''
        Returns whether custom map objects are supported by this engine.

        Custom map objects are map objects based on QGraphicsItem instances, which
        are hard to support in cases where the map rendering is not being
        performed by the Qt Graphics View framwork.
        @rtype: bool
        '''
        return self._supportsCustomMapObjects
    
    def _setSupportsCustomMapObjects(self, supportsCustomMapObjects):
        '''
        Sets whether custom map objects are supported by this engine to \a supportsCustomMapObjects.

        Custom map objects are map objects based on QGraphicsItem instances, which
        are hard to support in cases where the map rendering is not being
        performed by the Qt Graphics View framwork.
        
        @param supportsCustomMapObjects: If Supports True
        @type supportsCustomMapObjects: bool
        '''
        self._supportsCustomMapObjects = supportsCustomMapObjects
    
    def setLocale(self, locale):
        '''
        Sets the locale to be used by the this manager to \a locale.

        If this mapping manager supports returning map labels
        in different languages, they will be returned in the language of \a locale.
    
        The locale used defaults to the system locale if this is not set.
        
        @param locale: The new locale
        @type locale: QLocale
        '''
        self._locale = locale
    
    def locale(self):
        '''
        Returns the locale used to hint to this mapping manager about what
        language to use for map labels.
        @rtype: QLocale
        '''
        return self._locale
