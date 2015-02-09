'''
Created on 24.10.2011

@author: michi
'''
from PyQt4.QtCore import QObject
from ems.qt4.location.maps.geomappingmanagerengine import GeoMappingManagerEngine

class GeoMappingManager(QObject):
    '''
    \brief The QGeoMappingManager class provides support for displaying
    and interacting with maps.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps-mapping

    A QGeoMappingManager instance can create QGeoMapData instances with
    createMapData(). The QGeoMapData instances can be used to contain and
    manage information concerning what a particular QGraphicsGeoMap is viewing.

    The functions in this class will typically not be used by clients of this
    API, as the most common uses will only need to obtain a QGeoMappingManager
    instance and associate it with a QGraphicsGeoMap instance:
    \code
        QGeoServiceProvider serviceProvider("nokia");
        QGeoMappingManager *manager = serviceProvider.mappingManager();
        QGraphicsGeoMap *geoMap = new QGraphicsGeoMap(manager);
    \endcode

    This could have been simplified by having the plugin return a
    QGraphicsGeoMap instance instead, but this approach allows users to
    subclass QGraphicsGeoMap in order to override the standard event handlers
    and implement custom map behaviours.
    '''
    
    _engine = GeoMappingManagerEngine
    
    def __init__(self, engine, parent=None):
        '''
        Constructs a new manager with the specified \a parent and with the
        implementation provided by \a engine.
    
        This constructor is used internally by QGeoServiceProviderFactory. Regular
        users should acquire instances of QGeoMappingManager with
        QGeoServiceProvider::mappingManager()
        
        @param engine: The GeoMappingManagerEngine
        @type engine: GeoMappingManagerEngine
        @param parent: Parent QObject
        @type parent: QObject
        '''
        self._engine = engine
        QObject.__init__(self, parent)
        if self._engine:
            self._engine.setParent(self)
        else:
            raise TypeError("Please provide a valid GeoMappingManagerEngine")
    
    def managerName(self):
        '''
        Returns the name of the engine which implements the behaviour of this
        mapping manager.
    
        The combination of managerName() and managerVersion() should be unique
        amongst the plugin implementations.
        @rtype: basestring
        '''
        return self._engine.managerName()
    
    def managerVersion(self):
        '''
        Returns the version of the engine which implements the behaviour of this
        mapping manager.
    
        The combination of managerName() and managerVersion() should be unique
        amongst the plugin implementations.
        @rtype: int
        '''
        return self._engine.managerVersion()
    
    def createMapData(self):
        '''
        Returns a new QGeoMapData instance which will be managed by this manager.
        @rtype: GeoMapData
        '''
        return self._engine.createMapData()
    
    def supportedMapTypes(self):
        '''
        Returns a list of the map types supported by this manager.
        @rtype: list
        '''
        return self._engine.supportedMapTypes()
    
    def supportedConnectivityModes(self):
        '''
        Returns a list of the connectivity modes supported by this manager.
        @rtype: list
        '''
        return self._engine.supportedConnectivityModes()
    
    def minimumZoomLevel(self):
        '''
        Returns the minimum zoom level supported by this manager.

        Larger values of the zoom level correspond to more detailed views of the
        map.
        @rtype: int
        '''
        return self._engine.minimumZoomLevel()
    
    def maximumZoomLevel(self):
        '''
        Returns the maximum zoom level supported by this manager.

        Larger values of the zoom level correspond to more detailed views of the
        map.
        @rtype: int
        '''
        return self._engine.maximumZoomLevel()
    
    def supportsBearing(self):
        '''
        Return whether bearing is supported by this manager.
        @rtype: bool
        '''
        return self._engine.supportsBearing()
    
    def supportsTilting(self):
        '''
        Return whether tilting is supported by this manager.
        @rtype: bool
        '''
        return self._engine.supportsTilting()
    
    def minimumTilt(self):
        '''
        Returns minimum tilt supported by this manager.

        Value in degrees where 0 is equivalent to 90 degrees between view and earth's
        surface i.e. looking straight down to earth.
        @rtype: int
        '''
        return self._engine.minimumTilt()
    
    def maximumTilt(self):
        '''
        Returns maximum tilt supported by this manager.

        Value in degrees where 0 is equivalent to 90 degrees between view and earth's
        surface i.e. looking straight down to earth.
        @rtype: int
        '''
        return self._engine.maximumTilt()
    
    def supportsCustomMapObjects(self):
        '''
        Returns whether custom map objects are supported by this engine.

        Custom map objects are map objects based on QGraphicsItem instances, which
        are hard to support in cases where the map rendering is not being
        performed by the Qt Graphics View framwork.
        @rtype: bool
        '''
        return self._engine.supportsCustomMapObjects()
    
    def setLocale(self, locale):
        '''
        Sets the locale to be used by the this manager to \a locale.

        If this mapping manager supports returning map labels
        in different languages, they will be returned in the language of \a locale.
    
        The locale used defaults to the system locale if this is not set.
        @param locale: The locale
        @type locale: QLocale
        '''
        return self._engine.setLocale(locale)
    
    def locale(self):
        '''
        Returns the locale used to hint to this mapping manager about what
        language to use for map labels.
        @rtype: QLocale
        '''
        return self._engine.locale()