'''
Created on 15.11.2011

@author: michi
'''
from ems.qt4.location.geocoordinate import GeoCoordinate
class GeoRouteRequest(object):
    '''
    \brief The QGeoRouteRequest class represents the parameters and restrictions
    which define a request for routing information.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps-routing

    The default state of a QGeoRouteRequest instance will result in a request
    for basic route segment and navigation maneuvers describing the fastest
    route by car which covers the given waypoints.

    There may be signifcant variation in the features supported by different
    providers of routing information, or even in the features supported by
    the same provider if different levels of authorization are used.

    There are several functions in QGeoRoutingManager which can be used to
    check which features are supported with the current provider and
    authorization level.
    \sa QGeoRoutingManager
    '''
    
    'TravelMode Enum'
    
    CarTravel = 0x0001
    'The route will be optimized for someone who is driving a car.'
    
    PedestrianTravel = 0x0002
    'The route will be optimized for someone who is walking.'
    
    BicycleTravel = 0x0004
    'The route will be optimized for someone who is riding a bicycle.'
    
    PublicTransitTravel = 0x0008
    'The route will be optimized for someone who is making use of public transit.'
    
    TruckTravel = 0x0010
    'The route will be optimized for someone who is driving a truck.'
    
    'enum FeatureType'
    NoFeature = 0x00000000
    '''Used by QGeoRoutingManager::supportedFeatureTypes() to indicate that
        no features will be taken into account when planning the route.'''
    
    TollFeature = 0x00000001
    'Consdier tollways when planning the route.'
    
    HighwayFeature = 0x00000002
    'Consider highways when planning the route.'
    
    PublicTransitFeature = 0x00000004
    'Consider public transit when planning the route.'
    
    FerryFeature = 0x00000008
    'Consider ferries when planning the route.'
    
    TunnelFeature = 0x00000010
    'Consider tunnels when planning the route.'
    
    DirtRoadFeature = 0x00000020
    'Consider dirt roads when planning the route.'
    
    ParksFeature = 0x00000040
    'Consider parks when planning the route.'
    
    MotorPoolLaneFeature = 0x00000080
    'Consider motor pool lanes when planning the route.'
    
    
    '''enum FeatureWeight:
     Defines the weight to associate with a feature during  the
    planning of a route.

    These values will be used in combination with
    QGeoRouteRequest::Feature to determine if they should or should
    not be part of the route.
    '''
    NeutralFeatureWeight = 0x00000000
    '''The presence or absence of the feature will not affect the
        planning of the route.'''
    
    PreferFeatureWeight = 0x00000001
    '''Routes which contain the feature will be preferred over those that do
        not.'''
    
    RequireFeatureWeight = 0x00000002
    '''Only routes which contain the feature will be considered, otherwise
        no route will be returned.'''
    
    AvoidFeatureWeight = 0x00000004
    '''Routes which do not contain the feature will be preferred over those
        that do.'''
    
    DisallowFeatureWeight = 0x00000008
    '''Only routes which do not contain the feature will be considered,
        otherwise no route will be returned.'''
    
    'enum RouteOptimization'
    ShortestRoute = 0x0001
    'Minimize the length of the journey.'
    
    FastestRoute = 0x0002
    'Minimize the traveling time for the journey.'
    
    MostEconomicRoute = 0x0004
    'Minimize the cost of the journey.'
    
    MostScenicRoute = 0x0008
    'Maximize the scenic potential of the journey.'
    
    'enum SegmentDetail'
    NoSegmentData = 0x0000
    ''' No segment data should be included with the route.  A route requested
        with this level of segment detail will initialise
        QGeoRouteSegment::path() as a straight line between the positions of
        the previous and next QGeoManeuver instances.'''
    
    BasicSegmentData = 0x0001
    '''Basic segment data will be included with the route.  This will include
        QGeoRouteSegment::path().'''
    
    'enum ManeuverDetail'
    NoManeuvers = 0x0000
    'No maneuvers should be included with the route.'
    
    BasicManeuvers = 0x0001
    '''Basic manevuers will be included with the route. This will
        include QGeoManeuver::instructionText().'''
    
    _waypoints = []
    
    _excludeAreas = []
    
    _numberAlternativeRoutes = 0
    
    _travelModes = 0x0001
    
    _featureWeights = {}
    
    _routeOptimization = 0x0002
    
    _segmentDetail = 0x0001
    
    _maneuverDetail = 0x0001
    
    
    def __init__(self, waypointsOrOriginOrOther=[], destination=None):
        '''
        This signatures are included:
        
        GeoRouteRequest(waypoints):
        Constructs a request to calculate a route through the coordinates \a waypoints.
        The route will traverse the elements of \a waypoints in order.
        
        GeoRouteRequest(origin, destination):
        Constructs a request to calculate a route between \a origin and
        \a destination. (both GeoCoordinate)
        
        GeoRouteRequest(other):
        Constructs a route request object from the contents of \a other.
        
        
        @param waypointsOrOriginOrOther:
        @type waypointsOrOriginOrOther:
        @param destination:
        @type destination:
        '''
        
        if isinstance(waypointsOrOriginOrOther, list):
            self._waypoints = waypointsOrOriginOrOther
            
        if isinstance(waypointsOrOriginOrOther, GeoCoordinate):
            self._waypoints = []
            self._waypoints.append(waypointsOrOriginOrOther)
            self._waypoints.append(destination)
        
        if isinstance(waypointsOrOriginOrOther, GeoRouteRequest):
            self.__ilshift__(waypointsOrOriginOrOther)
    
    def __ilshift__(self, other):
        '''
        self <<= other
        Assigns \a other to this route request object and then returns a reference
        to this route request object.
        
        replacement for C++ = overloading
        @param other: GeoRouteRequest
        @type other: GeoRouteRequest
        @rtype: GeoRouteRequest
        '''
        for prop in ('_waypoints', '_excludeAreas', '_numberAlternativeRoutes',
            '_numberAlternativeRoutes', '_travelModes', '_featureWeights',
            '_routeOptimization', '_segmentDetail', '_maneuverDetail'):
            self.__setattr__(prop, other.__getattribute__(prop))
        return self
    
    def __eq__(self, other):
        '''
        self == other
        
        @param other: Right operand
        @type other: GeoRouteRequest
        @rtype: bool
        '''
        for prop in ('_waypoints', '_excludeAreas', '_numberAlternativeRoutes',
            '_numberAlternativeRoutes', '_travelModes', '_featureWeights',
            '_routeOptimization', '_segmentDetail', '_maneuverDetail'):
            if self.__getattribute__(prop) != other.__getattribute__(prop):
                return False
        
        return True
    
    def __ne__(self, other):
        '''
        self != other
        
        Returns whether this route request and \a other are equal.
        
        @param other: Right operand
        @type other: GeoRouteRequest
        @rtype: bool
        '''
        return not self.__eq__(other)
    
    def setWaypoints(self, waypoints):
        '''
        Sets \a waypoints as the waypoints that the route should pass through.

        The waypoints should be given in order from origin to destination.
    
        This request will be invalid until the waypoints have been set to a
        list containing two or more coordinates.
        
        @param waypoints: The new waypoints
        @type waypoints: list
        '''
        self._waypoints = waypoints
    
    def waypoints(self):
        '''
        Returns the waypoints that the route will pass through.
        @rtype: list
        '''
        return self._waypoints
    
    def setExcludeAreas(self, areas):
        '''
        Sets \a areas as excluded areas that the route must not cross.
        
        @param areas: The new areas which will be excluded in route planning
        @type areas: list
        '''
        self._excludeAreas = areas
    
    def excludeAreas(self):
        '''
        Returns areas the route must not cross.
        @rtype: list
        '''
        return self._excludeAreas
    
    def setNumberAlternativeRoutes(self, alternatives):
        '''
        Sets the number of alternative routes to request to \a alternatives.

        The default value is 0.
        
        @param alternatives: Alternative route count
        @type alternatives: int
        '''
        self._numberAlternativeRoutes = alternatives
    
    def numberAlternativeRoutes(self):
        '''
        Returns the number of alternative routes which will be requested.
        @rtype: int
        '''
        return self._numberAlternativeRoutes
    
    def setTravelModes(self, travelModes):
        '''
        Sets the travel modes which should be considered during the planning of the
        route to \a travelModes.
    
        The default value is QGeoRouteRequest::CarTravel.
        
        @param travelModes: The bits ob travel
        @type travelModes: int
        @see: travelMode Enum
        '''
        self._travelModes = travelModes
    
    def travelModes(self):
        '''
        Returns the travel modes which this request specifies should be considered
        during the planning of the route.
        @rtype: int
        '''
        return self._travelModes
    
    def setFeatureWeight(self, featureType, featureWeight):
        '''
        Assigns the weight \a featureWeight to the feauture \a featureType during
        the planning of the route.
    
        By default all features are assigned a weight of NeutralFeatureWeight.
    
        It is impossible to assign a weight to QGeoRouteRequest::NoFeature.
        
        @param featureType: The featureType which will be weighted
        @type featureType: int
        @param featureWeight: The featureWeight which will be given
        @type featureWeight: int
        @see: featureType Enum featureWeight Enum
        '''
        if featureWeight != GeoRouteRequest.NeutralFeatureWeight:
            if featureType != GeoRouteRequest.NoFeature:
                self._featureWeights[featureType] = featureWeight
        else:
            del self._featureWeights[featureType]
    
    def featureWeight(self, featureType):
        '''
        Returns the weight assigned to \a featureType in the planning of the route.

        If no feature weight has been specified for \a featureType then
        NeutralFeatureWeight will be returned.
        
        @param featureType: The featureType requested
        @type featureType: int
        @rtype: int
        '''
        if self._featureWeights.has_key(featureType):
            return self._featureWeights[featureType]
        return GeoRouteRequest.NeutralFeatureWeight
    
    def featureTypes(self):
        '''
        Returns the list of features that will be considered when planning the
        route.  Features with a weight of NeutralFeatureWeight will not be returned.
        @rtype: int
        '''
        return self._featureWeights.keys()
    
    def setRouteOptimization(self, optimization):
        '''
        Sets the optimization criteria to use while planning the route to
        \a optimization.
    
        The default value is QGeoRouteRequest::FastestRoute.
        
        @param optimization: The optimization type
        @type optimization: int
        @see: RouteOptimization Enum
        '''
        self._routeOptimization = optimization
    
    def routeOptimization(self):
        '''
        Returns the optimization criteria which this request specifies should be
        used while planning the route.
        @rtype: int
        '''
        return self._routeOptimization
    
    def setSegmentDetail(self, segmentDetail):
        '''
        Sets the level of detail to use when representing routing segments to
        \a segmentDetail.
        
        @param segmentDetail: The detail level of segments
        @type segmentDetail: int
        @see: SegmentDetail Enum
        '''
        self._segmentDetail = segmentDetail
    
    def segmentDetail(self):
        '''
        Returns the level of detail which will be used in the representation of
        routing segments.
        @rtype: int
        '''
        return self._segmentDetail
    
    def setManeuverDetail(self, maneuverDetail):
        '''
        Sets the level of detail to use when representing routing maneuvers to
        \a maneuverDetail.
    
        The default value is QGeoRouteRequest::BasicManeuvers.
        
        @param maneuverDetail: the new detail level of maneuvers
        @type maneuverDetail: int
        @see: ManeuverDetail Enum
        '''
        self._maneuverDetail = maneuverDetail
    
    def maneuverDetail(self):
        '''
        Returns the level of detail which will be used in the representation of
        routing maneuvers.
        @rtype: int
        @see: ManeuverDetail Enum
        '''
        return self._maneuverDetail