'''
Created on 15.11.2011

@author: michi
'''
from ems.qt4.location.maps.geomaneuver import GeoManeuver

class GeoRouteSegment(object):
    '''
    \brief The QGeoRouteSegment class represents a segment of a route.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps-routing

    A QGeoRouteSegment instance has information about the physcial layout
    of the route segment, the length of the route and estimated time required
    to traverse the route segment and an optional QGeoManeuver associated with
    the end of the route segment.

    QGeoRouteSegment instances can be thought of as edges on a routing
    graph, with QGeoManeuver instances as optional labels attached to the
    vertices of the graph.
    '''
    
    _valid = False
    
    _travelTime = 0
    
    _distance = 0.0
    
    _path = []
    
    _maneuver = GeoManeuver
    
    _nextSegment = None
    
    def __init__(self, other=None):
        '''
        Constructs an invalid route segment object.

        The route segment will remain invalid until one of setNextRouteSegment(),
        setTravelTime(), setDistance(), setPath() or setManeuver() is called.
        
        @param other: Another RouteSegment (optional)
        @type other: GeoRouteSegment
        '''
        self._maneuver = GeoManeuver()
        
        if isinstance(other, GeoRouteSegment):
            self.__ilshift__(other)
    
    def __ilshift__(self, other):
        '''
        self <<= other
        
        replacement for c++ overloaded = operator
        
        @param other: Right operand
        @type other: GeoRouteSegment
        @rtype: GeoRouteSegment
        '''
        for prop in ('_valid', '_travelTime','_distance','_path','_maneuver',
                     '_nextSegment'):
            self.__setattr__(prop, other.__getattribute__(prop))
        return self
    
    def __eq__(self, other):
        '''
        self == other
        
        Returns whether this route segment and \a other are equal.

        The value of nextRouteSegment() is not considered in the comparison.
        
        @param other: Right operand
        @type other: GeoRouteSegment
        @rtype: bool
        '''
        for prop in ('_valid', '_travelTime','_distance','_path','_maneuver'):
            if self.__getattribute__(prop) != other.__getattribute__(prop):
                return False
        return True
    
    def __ne__(self, other):
        '''
        self != other
        
        Returns whether this route segment and \a other are not equal.

        The value of nextRouteSegment() is not considered in the comparison.
        
        @param other: Right operand
        @type other: GeoRouteSegment
        '''
        return not self.__eq__(other)
    
    def isValid(self):
        '''
        Returns whether this route segment is valid or not.

        If nextRouteSegment() is called on the last route segment of a route, the
        returned value will be an invalid route segment.
        @rtype: bool
        '''
        return self._valid
    
    def setNextRouteSegment(self, routeSegment):
        '''
        Sets the next route segment in the route to \a routeSegment.
        
        @param routeSegment: The next RouteSegment
        @type routeSegment: GeoRouteSegment
        '''
        self._valid = True
        self._nextSegment = routeSegment
    
    def nextRouteSegment(self):
        '''
        Returns the next route segment in the route.

        Will return an invalid route segment if this is the last route
        segment in the route.
        @rtype: GeoRouteSegment
        '''
        if self._valid and self._nextSegment:
            return GeoRouteSegment(self._nextSegment)
        
        segment = GeoRouteSegment()
        segment._valid = False
        return segment
    
    def setTravelTime(self, secs):
        '''
        Sets the estimated amount of time it will take to traverse this segment of
        the route, in seconds, to \a secs.
        
        @param travelTime: The traveltime of this segment
        @type travelTime: int
        '''
        self._valid = True
        self._travelTime = secs
    
    def travelTime(self):
        '''
        Returns the estimated amount of time it will take to traverse this segment
        of the route, in seconds.
        @rtype: int
        '''
        return self._travelTime
    
    def setDistance(self, distance):
        '''
        Sets the distance covered by this segment of the route, in metres, to \a distance.
        
        @param distance: The distance between the origin and end
        @type distance: float
        '''
        self._valid = True
        self._distance = distance
    
    def distance(self):
        '''
        Returns the distance covered by this segment of the route, in metres.
        @rtype: float
        '''
        return self._distance
    
    def setPath(self, path):
        '''
        Sets the geometric shape of this segment of the route to \a path.

        The coordinates in \a path should be listed in the order in which they
        would be traversed by someone traveling along this segment of the route.
        
        @param path: A list of GeoCoordinate objects
        @type path:
        '''
        self._valid = True
        self._path = path
    
    def path(self):
        '''
        Returns the geometric shape of this route segment of the route.

        The coordinates should be listed in the order in which they
        would be traversed by someone traveling along this segment of the route.
        @rtype: list
        '''
        return self._path
    
    def setManeuver(self, maneuver):
        '''
        Sets the maneuver for this route segement to \a maneuver.
        
        @param maneuver: The maneuver
        @type maneuver: int
        '''
        self._maneuver = maneuver
    
    def maneuver(self):
        '''
        Returns the manevuer for this route segment.

        Will return an invalid QGeoManeuver if no information has been attached
        to the endpoint of this route segment.
        @rtype: int
        '''
        return self._maneuver
    