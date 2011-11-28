'''
Created on 10.11.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QPen

from geomapobject import GeoMapObject
from ems.qt4.location.maps.georoute import GeoRoute

class GeoMapRouteObject(GeoMapObject):
    '''
    \brief The QGeoMapRouteObject class is a QGeoMapObject used to draw
    a route on a map.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps-mapping-objects

    The route is specified by a QGeoRoute object.

    The route might be quite detailed, and so to improve performance the
    detail level can be set with QGeoMapRouteObject::detailLevel.

    The route object draws the route as a series of lines with a minimum
    on-screen harmattan length equal to the detail level.  This is done so that
    the small changes in direction of a road will be visible at high zoom
    levels but will not slow down the rendering at the lower zoom levels.
    '''
    
    routeChanged = pyqtSignal(GeoRoute)
    '''This signal is emitted when the route drawn by this route object
    has changed.

    The new value is \a route.'''
    
    penChanged = pyqtSignal(QPen)
    '''This signal is emitted when the pen used to draw this route object has
    changed.

    The new value is \a pen.'''
    
    detailLevelChanged = pyqtSignal(int)
    '''This signal is emitted when the level of detail used to draw this
    route object has changed.

    The new value is \a detailLevel.'''
    
    _route = None
    
    _pen = None
    
    _detailLevel = 6
    
    def __init__(self, route=None, mapData=None):
        '''
        @param route: GeoRoute (optional)
        @type route: GeoRoute
        @param mapData: GeoMapData (optional)
        @type mapData: GeoMapData
        '''
        GeoMapObject.__init__(self, mapData)
        self.setUnits(GeoMapObject.AbsoluteArcSecondUnit)
        self.setTransformType(GeoMapObject.ExactTransform)
        if route is not None:
            self._route = route
    
    def type_(self):
        return GeoMapObject.RouteType
    
    def route(self):
        '''
        \property QGeoMapRouteObject::route
        \brief This property holds the which will be displayed.
    
        The default value of this property is an empty route.
    
        If QGeoRoute::path() returns a list of less than 2 valid QGeoCoordinates
        then the route object will not be displayed.
        @rtype: GeoRoute
        '''
        return self._route
    
    def setRoute(self, route):
        '''
        assign a route
        @param route: GeoRoute
        @type route: GeoRoute
        '''
        self._route = route
        self.routeChanged.emit(self._route)
    
    def pen(self):
        '''
        \property QGeoMapRouteObject::pen
        \brief This property holds the pen that will be used to draw this object.
    
        The pen is used to draw the route.
    
        The pen will be treated like a cosmetic pen, which means that the width
        of the pen will be independent of the zoom level of the map.
        @rtype: QPen
        '''
        return self._pen
    
    def setPen(self, pen):
        '''
        Assign a QPen
        @param pen: QPen
        @type pen: QPen
        '''
        self._pen = pen
        self.penChanged.emit(self._pen)
    
    def detailLevel(self):
        '''
        \property QGeoMapRouteObject::detailLevel
        \brief This property holds the level of detail used to draw this object.
    
        A QGeoRoute instance can contain a large amount of information about the
        path taken by the route. This property is used as a hint to help reduce the
        amount of information that needs to be drawn on the map.
    
        The path taken by the route is represented as a list of QGeoCoordinate
        instances. This route object will draw lines between these coordinates, but
        will skip members of the list until the manhattan distance between the
        start point and the end point of the line is at least \a detailLevel.
    
        The default value of this property is 6.
        @rtype: int
        '''
        return self._detailLevel
    
    def setDetailLevel(self, detailLevel):
        if self._detailLevel != detailLevel:
            self._detailLevel = detailLevel
            self.detailLevelChanged.emit(self._detailLevel)
    
    