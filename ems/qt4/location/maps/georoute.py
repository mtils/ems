'''
Created on 15.11.2011

@author: michi
'''
from ems.qt4.location.maps.georouterequest import GeoRouteRequest #@UnresolvedImport
from ems.qt4.location.geoboundingbox import GeoBoundingBox
from ems.qt4.location.maps.georoutesegment import GeoRouteSegment #@UnresolvedImport

class GeoRoute(object):
    '''
    \brief The QGeoRoute class represents a route between two points.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps-routing

    A QGeoRoute object contains high level information about a route, such
    as the length the route, the estimated travel time for the route,
    and enough information to render a basic image of the route on a map.

    The QGeoRoute object also contains a list of QGeoRouteSegment objecs which
    describe subsections of the route in greater detail.

    Routing information is normally requested using
    QGeoRoutingManager::calculateRoute(), which returns a QGeoRouteReply
    instance. If the operation is completed successfully the routing
    information can be accessed with QGeoRouteReply::routes()

    \sa QGeoRoutingManager
    '''
    
    _id = unicode()
    
    _request = GeoRouteRequest
    
    _bounds = GeoBoundingBox
    
    _travelTime = -1
    
    _distance = 0.0
    
    _travelMode = GeoRouteRequest.CarTravel
    
    _path = []
    
    _firstSegment = GeoRouteSegment
    
    def __init__(self, other=None):
        if isinstance(other, GeoRoute):
            self.__ilshift__(other)
    
    def __ilshift__(self, other):
        '''
        self <<= other
        
        Assigns the contents of \a other to this route and returns a reference to
        this route.
         
        @param other: Right operand
        @type other: GeoRoute
        @rtype: GeoRoute
        '''
        for prop in ('_id','_request','_bounds','_travelTime',
                     '_distance','_travelMode', '_path', '_firstSegment'):
            self.__setattr__(prop, other.__getattribute__(prop))
        return self
    
    def __eq__(self, other):
        '''
        Returns whether this route and \a other are equal.
        
        @param other: Right operand
        @type other: GeoRoute
        '''
        for prop in ('_id','_request','_bounds','_travelTime',
                     '_distance','_travelMode', '_path'):
            if self.__getattribute__(prop) != other.__getattribute__(prop):
                return False
        
        s1 = self._firstRouteSegment
        s2 = other.firstRouteSegment()
        
        while True:
            if s1.isValid() != s2.isValid():
                return False
            if not s1.isValid():
                break;
            if s1 != s2:
                return False
            s1 = s1.nextRouteSegment()
            s2 = s2.nextRouteSegment()
            
        return True
    
    def __ne__(self, other):
        '''
        Returns whether this route and \a other are not equal.
        
        @param other: Right operand
        @type other: GeoRoute
        '''
        return not self.__eq__(other)
    
    def setRouteId(self, routeId):
        '''
        Sets the ID of this route to \a id.

        Service providers which support the updating of routes commonly assign
        IDs to routes.  If this route came from such a service provider changing
        the ID will probably cause route updates to stop working.
        
        @param routeId: The route id
        @type routeId: basestring
        '''
        self._id = routeId
    
    def routeId(self):
        '''
        Returns the ID of this route.

        Service providers which support the updating of routes commonly assign
        IDs to routes.  If this route did not come from such a service provider
        the function will return an empty string.
        @rtype: basestring
        '''
        return self._id
    
    def setRequest(self, request):
        '''
        Sets the route request which describes the criteria used in the
        calculcation of this route to \a request.
        
        @param request: Sets the new request
        @type request: GeoRouteRequest
        '''
        self._request = request
    
    def request(self):
        '''
        Returns the route request which describes the criteria used in
        the calculation of this route.
        @rtype: GeoRouteRequest
        '''
        return self._request
    
    def setBounds(self, bounds):
        '''
        Sets the bounding box which encompasses the entire route to \a bounds.
        
        @param bounds: The bounds
        @type bounds: GeoBoundingBox
        '''
        self._bounds = bounds
    
    def bounds(self):
        '''
        Returns a bounding box which encompasses the entire route.
        @rtype: GeoBoundingBox
        '''
        return self._bounds
    
    def setFirstRouteSegment(self, routeSegment):
        '''
        Sets the first route segment in the route to \a routeSegment.
        
        @param routeSegment: The routeSegment
        @type routeSegment: GeoRouteSegment
        '''
        self._firstSegment = routeSegment
    
    def firstRouteSegment(self):
        '''
        Returns the first route segment in the route.

        Will return an invalid route segment if there are no route segments
        associated with the route.
    
        The remaining route segments can be accessed sequentially with
        QGeoRouteSegment::nextRouteSegment.
        @rtype: GeoRouteSegment
        '''
        return self._firstSegment
    
    def setTravelTime(self, secs):
        '''
        Sets the estimated amount of time it will take to traverse this route,
        in seconds, to \a secs.
        
        @param secs: The new traveltime in seconds
        @type secs: int
        '''
        self._travelTime = secs
    
    def travelTime(self):
        '''
        Returns the estimated amount of time it will take to traverse this route,
        in seconds.
        @rtype: int
        '''
        return self._travelTime
    
    def setDistance(self, distance):
        '''
        Sets the distance covered by this route, in metres, to \a distance.
        
        @param distance: Distance
        @type distance: float
        '''
        self._distance = distance
    
    def distance(self):
        '''
        Returns the distance covered by this route, in metres.
        @rtype: float
        '''
        return self._distance
    
    def setTravelMode(self, mode):
        '''
        Sets the travel mode for this route to \a mode.

        This should be one of the travel modes returned by request().travelModes().
        
        @param mode: The new travelmode
        @type mode: int
        @see: GeoRouteRequest TravelMode Enum
        '''
        self._travelMode = mode
    
    def travelMode(self):
        '''
        Returns the travel mode for the this route.

        This should be one of the travel modes returned by request().travelModes().
        @rtype: int
        '''
        return self._travelMode
    
    def setPath(self, path):
        '''
        Sets the geometric shape of the route to \a path.

        The coordinates in \a path should be listed in the order in which they
        would be traversed by someone traveling along this segment of the route.
        
        @param path: The new path, a list of GeoCoordinate objects
        @type path: list
        '''
        self._path = path
    
    def path(self):
        '''
        Returns the geometric shape of the route.

        The coordinates should be listed in the order in which they
        would be traversed by someone traveling along this segment of the route.
        @rtype: list
        '''
        return self._path
    
    