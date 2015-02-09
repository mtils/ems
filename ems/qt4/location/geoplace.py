'''
Created on 26.10.2011

@author: michi
'''
from ems.qt4.location.geoboundingbox import GeoBoundingBox
from ems.qt4.location.geocoordinate import GeoCoordinate
from ems.qt4.location.geoaddress import GeoAddress #@UnresolvedImport

class GeoPlace(object):
    '''
    \brief The QGeoPlace class represents basic information about a place.

    \inmodule QtLocation
    \since 1.1

    \ingroup location

    A QGeoPlace contains a coordinate and the corresponding address, along
    with an optional bounding box describing the minimum viewport necessary
    to display the entirety of the place.

    A QGeoPlace may contain an QLandmark instance.  The isLandmark() function
    can be used to determine if this is the case, and the
    QLandmark(const QGeoPlace &place) constructor can be used to restore
    access to the landmark data.

    For example:
    \code
    QGeoPlace p;
    QLandmark l;
    ...
    if (p.isLandmark())
        l = QLandmark(p)
    \endcode
    '''
    
    'PLaceType Enum'
    GeoPlaceType = 0
    LandmarkType = 1
    
    _viewport = GeoBoundingBox
    
    _coordinate = GeoCoordinate
    
    _address = GeoAddress
    
    _type = 0
    
    def __init__(self, other=None):
        '''
        Constructs a copy of \a other if passed
        
        @param other: Other GeoPlace (optional)
        @type other: GeoPlace
        '''
        if isinstance(other, GeoPlace):
            self.__ilshift__(other)
    
    def __ilshift__(self, other):
        '''
        self <<= other
        Replacement for C++ = operator overloading
         
        @param other: Right operand
        @type other: GeoPlace
        @rtype: GeoPLace
        '''
        for prop in ('_type','_viewport','_coordinate','_address'):
            self.__setattr__(prop, other.__getattribute__(prop))
        return self
    
    def __eq__(self, other):
        '''
        self == other
        
        Returns true if \a other is equal to this place,
        otherwise returns false.
        
        @param other: Right operand
        @type other: GeoPlace
        @rtype: bool
        '''
        for prop in ('_type','_viewport','_coordinate','_address'):
            if self.__getattribute__(prop) != other.__getattribute__(prop):
                return False
        
        return True
    
    def __ne__(self, other):
        '''
        self != other
        
        Returns true if \a other is not equal to this place,
        otherwise returns false.
        
        @param other: Right operand
        @type other: GeoPlace
        '''
        return not self.__eq__(other)
    
    def isLandmark(self):
        '''
        This function returns whether this QGeoPlace instance contain all of the
        information required to construct a QLandmark instance.
    
        If so, the QLandmark(const QGeoPlace &place) constructor can be used to
        restore access to the landmark data.
        @rtype: bool
        '''
        return (self._type == GeoPlace.LandmarkType)
    
    def viewport(self):
        '''
        Returns the viewport associated with this place.

        The viewport is a suggestion for a size and position of a map window
        which aims to view this palce.
        @rtype: GeoBoundingBox
        '''
        return self._viewport
    
    def setViewport(self, viewport):
        '''
        Sets the viewport associated with this place to \a viewport.

        The viewport is a suggestion for a size and position of a map window
        which aims to view this place.
        
        @param viewport: The new viewport
        @type viewport: GeoBoundingBox
        '''
        self._viewport = viewport
    
    def coordinate(self):
        '''
        Returns the coordinate that this place is located at.
        @rtype: GeoCoordinate
        '''
        return self._coordinate
    
    def setCoordinate(self, coordinate):
        '''
        Sets the \a coordinate that this place is located at.
        
        @param coordinate: The new coordinate
        @type coordinate: GeoCoordinate
        '''
        self._coordinate = coordinate
    
    def address(self):
        '''
        Returns the address of this place.
        @rtype: GeoCoordinate
        '''
        return self._address
    
    def setAddress(self, address):
        '''
        Sets the \a address of this place.
        
        @param address: New Address
        @type address: GeoAddress
        '''
        self._address = address