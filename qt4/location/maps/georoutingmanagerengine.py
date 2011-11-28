'''
Created on 16.11.2011

@author: michi
'''
from PyQt4.QtCore import QObject, pyqtSignal, QLocale
from ems.qt4.location.maps.georoutereply import GeoRouteReply #@UnresolvedImport
from ems.qt4.location.maps.georouterequest import GeoRouteRequest #@UnresolvedImport

class GeoRoutingManagerEngine(QObject):
    '''
    \brief The QGeoRoutingManagerEngine class provides an interface and
    convenience methods to implementers of QGeoServiceProvider plugins who want
    to provide access to geographic routing information.


    \inmodule QtLocation
    \since 1.1

    \ingroup maps-impl

    Subclasses of QGeoRoutingManagerEngine need to provide an implementation of
    calculateRoute().

    In the default implementation, supportsRouteUpdates() returns false and
    updateRoute() returns a QGeoRouteReply object containing a
    QGeoRouteReply::UnsupportedOptionError.

    If the routing service supports updating routes as they are being
    travelled, the subclass should provide an implementation of updateRoute()
    and call setSupportsRouteUpdates(true) at some point in time before
    updateRoute() is called.

    The function setSupportsRouteUpdates() is one of several functions which
    configure the reported capabilities of the engine.  If the capabilities
    of an engine differ from the default values these functions should be
    used so that the reported capabilies are accurate.

    It is important that this is done before calculateRoute(), updateRoute()
    or any of the capability reporting functions are used to prevent
    incorrect or inconsistent behaviour.

    A subclass of QGeoRouteManagerEngine will often make use of a subclass
    fo QGeoRouteReply internally, in order to add any engine-specific
    data (such as a QNetworkReply object for network-based services) to the
    QGeoRouteReply instances used by the engine.

    \sa QGeoRoutingManager
    '''
    
    _managerName = ""
    
    _managerVersion = -1
    
    
    _supportsRouteUpdates = False
    _supportsAlternativeRoutes = False
    _supportsExcludeAreas = False
    _supportedTravelModes = 0
    _supportedFeatureTypes = 0
    _supportedFeatureWeights = 0
    _supportedRouteOptimizations = 0
    _supportedSegmentDetails = 0
    _supportedManeuverDetails = 0
    _locale = QLocale()
    
    finished = pyqtSignal(GeoRouteReply)
    '''This signal is emitted when \a reply has finished processing.

    If reply::error() equals QGeoRouteReply::NoError then the processing
    finished successfully.
    
    This signal and QGeoRouteReply::finished() will be emitted at the same time.
    
    \note Do no delete the \a reply object in the slot connected to this signal.
    Use deleteLater() instead.'''
    
    error = pyqtSignal(int, str)
    '''This signal is emitted when an error has been detected in the processing of
    \a reply.  The QGeoRoutingManagerEngine::finished() signal will probably follow.
    
    The error will be described by the error code \a error.  If \a errorString is
    not empty it will contain a textual description of the error.
    
    This signal and QGeoRouteReply::error() will be emitted at the same time.
    
    \note Do no delete the \a reply object in the slot connected to this signal.
    Use deleteLater() instead.'''
    
    def __init__(self, parameters, parent=None):
        '''
        Constructs a new engine with the specified \a parent, using \a parameters
        to pass any implementation specific data to the engine.
        
        @param parameters: Hash of params
        @type parameters: dict
        @param parent: The parent QObject
        @type parent: QObject
        '''
        QObject.__init__(self, parent)
    
    def _setManagerName(self, managerName):
        '''
        Sets the name which this engine implementation uses to distinguish itself
        from the implementations provided by other plugins to \a managerName.
    
        The combination of managerName() and managerVersion() should be unique
        amongst plugin implementations.
        
        @param managerName: the new managerName
        @type managerName: basestring
        '''
        self._managerName = managerName
    
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
        
        @param managerVersion: The version of the manager
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
    
    def calculateRoute(self, request):
        '''
        QGeoRouteReply* QGeoRoutingManagerEngine::calculateRoute(const QGeoRouteRequest& request)

        Begins the calculation of the route specified by \a request.
    
        A QGeoRouteReply object will be returned, which can be used to manage the
        routing operation and to return the results of the operation.
    
        This engine and the returned QGeoRouteReply object will emit signals
        indicating if the operation completes or if errors occur.
    
        Once the operation has completed, QGeoRouteReply::routes can be used to
        retrieve the calculated route or routes.
    
        If \a request includes features which are not supported by this engine, as
        reported by the methods in this engine, then a
        QGeoRouteReply::UnsupportedOptionError will occur.
    
        The user is responsible for deleting the returned reply object, although
        this can be done in the slot connected to QGeoRoutingManagerEngine::finished(),
        QGeoRoutingManagerEngine::error(), QGeoRouteReply::finished() or
        QGeoRouteReply::error() with deleteLater().
        
        @param request: The GeoRouteRequest
        @type request: GeoRouteRequest
        '''
        raise NotImplementedError("Please implement calculateRoute(request)")
    
    def updateRoute(self, route, position):
        '''
        Begins the process of updating \a route based on the current position \a
        position.
    
        A QGeoRouteReply object will be returned, which can be used to manage the
        routing operation and to return the results of the operation.
    
        This engine and the returned QGeoRouteReply object will emit signals
        indicating if the operation completes or if errors occur.
    
        If supportsRouteUpdates() returns false an
        QGeoRouteReply::UnsupportedOptionError will occur.
    
        Once the operation has completed, QGeoRouteReply::routes can be used to
        retrieve the updated route.
    
        The returned route could be entirely different to the original route,
        especially if \a position is far enough away from the initial route.
        Otherwise the route will be similar, although the remaining time and
        distance will be updated and any segments of the original route which
        have been traversed will be removed.
    
        The user is responsible for deleting the returned reply object, although
        this can be done in the slot connected to QGeoRoutingManagerEngine::finished(),
        QGeoRoutingManagerEngine::error(), QGeoRouteReply::finished() or
        QGeoRouteReply::error() with deleteLater().
        
        @param route: The old route
        @type route: GeoRoute
        @param position: The new position
        @type position: GeoCoordinate
        '''
        raise NotImplementedError("Please implement updateRoute(route, position)")
    
    def _setSupportsRouteUpdates(self, supported):
        '''
        Sets whether this engine supports updating routes to \a supported.
    
        It is important that subclasses use this method to ensure that the engine
        reports its capabilities correctly.  If this function is not used the
        engine will report that it does not support updating routes.
        @param supported: If supported True
        @type supported: bool
        '''
        self._supportsRouteUpdates = supported
    
    def supportsRouteUpdates(self):
        '''
        Returns whether this engine supports updating routes.
        @rtype: bool
        '''
        return self._supportsRouteUpdates
    
    def _setSupportsAlternativeRoutes(self, supported):
        '''
        Sets whether this engine supports request for alternative routes to \a supported.

        It is important that subclasses use this method to ensure that the engine
        reports its capabilities correctly.  If this function is not used the
        engine will report that it does not support alternative routes.
        @param supported: If supported True
        @type supported: bool
        @rtype: bool
        '''
        self._supportsAlternativeRoutes = supported
    
    def supportsAlternativeRoutes(self):
        '''
        Returns whether this engine supports request for alternative routes.
        @rtype: bool
        '''
        return self._supportsAlternativeRoutes
    
    def _setSupportsExcludeAreas(self, supported):
        '''
        Sets whether this engine supports request for excluding areas from routes to \a supported.

        It is important that subclasses use this method to ensure that the engine
        reports its capabilities correctly.  If this function is not used the
        engine will report that it does not support excluding areas.
        
        @param supported: If supported True
        @type supported: bool
        '''
        self._supportsExcludeAreas = supported
    
    def supportsExcludeAreas(self):
        '''
        Returns whether this engine supports the exclusion of areas from routes.
        @rtype: bool
        '''
        return self._supportsExcludeAreas
    
    def _setSupportedTravelModes(self, travelModes):
        '''
        Sets the travel modes supported by this engine to \a travelModes.

        It is important that subclasses use this method to ensure that the engine
        reports its capabilities correctly.  If this function is not used the
        engine will report that it supports no travel modes at all.
        
        @param travelModes: The supported Travelmode a | b | c
        @type travelModes: int
        '''
        self._supportedTravelModes = travelModes
    
    def supportedTravelModes(self):
        '''
        Returns the travel modes supported by this engine.
        @rtype: int
        '''
        return self._supportedTravelModes
    
    def _setSupportedFeatureTypes(self, featureTypes):
        '''
        Sets the types of features that this engine can take into account
        during route planning to \a featureTypes.
    
        It is important that subclasses use this method to ensure that the engine
        reports its capabilities correctly.  If this function is not used the
        engine will report that it supports no feature types at all.
        
        @param featureTypes: The new featureTypes
        @type featureTypes: int
        '''
        self._supportedFeatureTypes = featureTypes
    
    def supportedFeatureTypes(self):
        '''
        Returns the types of features that this engine can take into account
        during route planning.
        @rtype: int
        '''
        return self._supportedFeatureTypes
    
    def _setSupportedFeatureWeights(self, featureWeights):
        '''
        Sets the weightings which this engine can apply to different features
        during route planning to \a featureWeights.
    
        It is important that subclasses use this method to ensure that the engine
        reports its capabilities correctly.  If this function is not used the
        engine will report that it supports no feaure weights at all.
        
        @param featureWeights: The featureWeights a | b
        @type featureWeights: int
        '''
        self._supportedFeatureWeights = featureWeights
        self._supportedFeatureWeights |= GeoRouteRequest.NeutralFeatureWeight
    
    def supportedFeatureWeights(self):
        '''
        Returns the weightings which this engine can apply to different features
        during route planning.
        @rtype: int
        '''
        return self._supportedFeatureWeights
    
    def _setSupportedRouteOptimizations(self, optimizations):
        '''
        Sets the route optimizations supported by this engine to \a optimizations.

        It is important that subclasses use this method to ensure that the engine
        reports its capabilities correctly.  If this function is not used the
        engine will report that it supports no route optimizations at all.
        
        @param optimizations: The optimizations
        @type optimizations: int
        '''
        self._supportedRouteOptimizations = optimizations
    
    def supportedRouteOptimizations(self):
        '''
        Returns the route optimizations supported by this engine.
        @rtype: int
        '''
        return self._supportedRouteOptimizations
    
    def _setSupportedSegmentDetails(self, segmentDetails):
        '''
        Sets the levels of detail for routing segments which can be
        requested by this engine to \a segmentDetails.
    
        It is important that subclasses use this method to ensure that the engine
        reports its capabilities correctly.  If this function is not used the
        engine will report that it supports no segment detail at all.
        
        @param segmentDetails: The level of details
        @type segmentDetails: int
        '''
        self._supportedSegmentDetails = segmentDetails
    
    def supportedSegmentDetails(self):
        '''
        Returns the levels of detail for routing segments which can be
        requested by this engine.
        @rtype: int
        '''
        return self._supportedSegmentDetails
    
    def _setSupportedManeuverDetails(self, maneuverDetails):
        '''
        Sets the levels of detail for navigation manuevers which can be
        requested by this engine to \a maneuverDetails.
    
        It is important that subclasses use this method to ensure that the engine
        reports its capabilities correctly.  If this function is not used the
        engine will report that it supports no maneuver details at all.
        
        @param maneuverDetails: The supported details
        @type maneuverDetails: int
        '''
        self._supportedManeuverDetails = maneuverDetails
    
    def maneuverDetails(self):
        '''
        Returns the levels of detail for navigation maneuvers which can be
        requested by this engine.
        @rtype: int
        '''
        return self._supportedManeuverDetails
    
    def setLocale(self, locale):
        '''
        Sets the locale to be used by the this manager to \a locale.

        If this routing manager supports returning addresses and instructions
        in different languages, they will be returned in the language of \a locale.
    
        The locale used defaults to the system locale if this is not set.
        
        @param locale: The new locale
        @type locale: QLocale
        '''
        self._locale = locale
    
    def locale(self):
        '''
         Returns the locale used to hint to this routing manager about what
        language to use for addresses and instructions.
        @rtype: QLocale
        '''
        return self._locale
    
    
        