'''
Created on 24.10.2011

@author: michi
'''
from geoboundingarea import GeoBoundingArea #@UnresolvedImport
from ems.qt4.location.geocoordinate import GeoCoordinate


class GeoBoundingCircle(GeoBoundingArea):
    '''
    \brief The QGeoBoundingCircle class defines a circular geographic area.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps

    The circle is defined in terms of a QGeoCoordinate which specifies the
    center of the circle and a qreal which specifies the radius of the circle
    in metres.

    The circle is considered invalid if the center coordinate is invalid
    or if the radius is less than zero.
    '''
    _center = GeoCoordinate
    
    _radius = 0.0
    
    
    def __init__(self, centerOrOther=None, radius=None):
        '''
        Constructs a new, invalid bounding circle.
        
        GeoBoundingCircle(GeoCoordinate center, float radius)
        Constructs a new bounding circle centered at \a center and with a radius of \a
        radius metres.
        
        GeoBoundingCircle(GeoBoundingCircle other)
        Constructs a new bounding circle from the contents of \a other.
        
        @param centerOrOther: GeoCoordinate or GeoBoundingCircle (optional)
        @type centerOrOther: GeoCoordinate|GeoBoundingBox
        @param radius: Optional radius
        @type radius: float
        '''
        if isinstance(centerOrOther, GeoCoordinate):
            self._center = centerOrOther
            if not isinstance(radius, (float, int)):
                raise TypeError("If you construct with center, pass a radius")
            self._radius = float(radius)
        if isinstance(centerOrOther, GeoBoundingCircle):
            self.__ilshift__(centerOrOther)
    
    def __ilshift__(self, other):
        '''
        self <<= other
        
        replacement for c++ = operator overloading
        @param other: The right operand
        @type other: GeoBoundingBox
        @rtype: GeoBoundingBox
        '''
        self._center = other.center()
        self._radius = other.radius()
        return self
    
    def __eq__(self, other):
        '''
        Returns whether this bounding circle is equal to \a other.
        
        self == other
        @param other: Right operand
        @type other: GeoBoundingCircle
        @rtype: bool
        '''
        return self._center == other.center() and\
            self._radius == other.radius()
    
    def __ne__(self, other):
        '''
        Returns whether this bounding circle is not equal to \a other.
        
        self != other
        @param other: Right operand
        @type other: GeoBoundingCircle
        @rtype: bool
        '''
        return not self.__eq__(other)
    
    def type_(self):
        '''
        Returns QGeoBoundingArea::CircleType to identify this as a
        QGeoBoundingCircle instance.
    
        This function is provided to help find the specific type of
        aQGeoBoundingArea instance.
        @rtype: int
        '''
        return GeoBoundingArea.CircleType
    
    def isValid(self):
        '''
        Returns whether this bounding circle is valid.

        A valid bounding circle has a valid center coordinate and a radius
        greater than or equal to zero.
        @rtype: bool
        '''
        if isinstance(self._center, GeoCoordinate):
            return (self._center.isValid() and self._radius >= -1e-7)
        return False
    
    def isEmpty(self):
        '''
        Returns whether this bounding circle has a geometrical area of zero.

        Returns true if this bounding circle is invalid.
        '''
        return (not self.isValid() or (self._radius <= 1e-7))
    
    def setCenter(self, center):
        '''
        Sets the center coordinate of this bounding circle to \a center.
        
        @param center: GeoCoordinate
        @type center: GeoCoordinate
        '''
        self._center = center
    
    def center(self):
        '''
        Returns the center coordinate of this bounding circle.
        @rtype: GeoCoordinate
        '''
        return self._center
    
    def setRadius(self, radius):
        '''
        Sets the radius in metres of this bounding circle to \a radius.
        
        @param radius: the new radius
        @type radius: float
        '''
        self._radius = radius
    
    def radius(self):
        '''
        Returns the radius in meters of this bounding circle.
        
        @rtype: float
        '''
        return self._radius
    
    def contains(self, coordinate):
        '''
        Returns whether the coordinate \a coordinate is contained within this
        bounding circle.
        
        @param coordinate: The other coordinate
        @type coordinate: GeoCoordinate
        @rtype: bool
        '''
        if not self.isValid() or not coordinate.isValid():
            return False
        
        if self._center.distanceTo(coordinate) <= self._radius:
            return True
        return False
    
    def translate(self, degreesLatitude, degreesLongitude):
        '''
        Translates this bounding circle by \a degreesLatitude northwards and \a
        degreesLongitude eastwards.
    
        Negative values of \a degreesLatitude and \a degreesLongitude correspond to
        southward and westward translation respectively.
        
        @param degreesLatitude: north degrees
        @type degreesLatitude: float
        @param degreesLongitude: east degrees
        @type degreesLongitude: float
        '''
        
        # TODO handle dlat, dlon larger than 360 degrees
    
        lat = self._center.latitude()
        lon = self._center.longitude()
    
        lat += degreesLatitude
        lon += degreesLongitude
    
        if lon < -180.0:
            lon += 360.0
        if lon > 180.0:
            lon -= 360.0
    
        if lat > 90.0:
            lat = 180.0 - lat
            if lon < 0.0:
                lon = 180.0
            else:
                lon -= 180
        
    
        if lat < -90.0:
            lat = 180.0 + lat
            if lon < 0.0:
                lon = 180.0
            else:
                lon -= 180
        
        self._center = GeoCoordinate(lat, lon)
    
    def translated(self, degreesLatitude, degreesLongitude):
        '''
        Returns a copy of this bounding circle translated by \a degreesLatitude northwards and \a
        degreesLongitude eastwards.
    
        Negative values of \a degreesLatitude and \a degreesLongitude correspond to
        southward and westward translation respectively.
        
        @param degreesLatitude: north degrees
        @type degreesLatitude: float
        @param degreesLongitude: east degrees
        @type degreesLongitude: float
        @rtype: GeoBoundingCircle
        '''
        result = GeoBoundingCircle(self)
        result.translate(degreesLatitude, degreesLongitude)
        return result
    
    
    
