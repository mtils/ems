#coding=utf-8
'''
Created on 13.10.2011

@author: michi
'''
import math

from ems.qt4.location.utils import LocationUtils #@UnresolvedImport

class GeoCoordinate(object):
    '''
    GeoCoordinate
    The GeoCoordinate class defines a geographical position on the surface of the Earth.

    A GeoCoordinate is defined by latitude, longitude, and optionally, altitude.

    Use type() to determine whether a coordinate is a 2D coordinate (has
    latitude and longitude only) or 3D coordinate (has latitude, longitude
    and altitude). Use distanceTo() and azimuthTo() to calculate the distance
    and bearing between coordinates.

    The coordinate values should be specified using the WGS84 datum.
    '''
    
    EARTH_MEAN_RADIUS = 6371.0072
    
    @staticmethod
    def degToRad(deg):
        return deg * math.pi / 180
    
    @staticmethod
    def radToDeg(rad):
        return rad * 180 / math.pi
    
    
    lat = None
    lng = None
    alt = None
    
    '''GeoCoordinate::CoordinateType Enum
    Defines the types of a coordinate'''
    
    InvalidCoordinate = 0
    'An invalid coordinate. A coordinate is invalid if its latitude or longitude values are invalid.'
    Coordinate2D = 1
    'A coordinate with valid latitude and longitude values.'
    Coordinate3D = 2
    'A coordinate with valid latitude and longitude values, and also an altitude value.'
    
    '''QGeoCoordinate::CoordinateFormat Enum
    Defines the possible formatting options for toString().'''
    
    Degrees = 0
    'Returns a string representation of the coordinates in decimal degrees format.'
    DegreesWithHemisphere = 1
    "Returns a string representation of the coordinates in decimal degrees format, using 'N', 'S', 'E' or 'W' to indicate the hemispheres of the coordinates."
    DegreesMinutes = 2
    'Returns a string representation of the coordinates in degrees-minutes format.'
    DegreesMinutesWithHemisphere = 3
    "Returns a string representation of the coordinates in degrees-minutes format, using 'N', 'S', 'E' or 'W' to indicate the hemispheres of the coordinates."
    DegreesMinutesSeconds = 4
    'Returns a string representation of the coordinates in degrees-minutes-seconds format.'
    DegreesMinutesSecondsWithHemisphere = 5
    "Returns a string representation of the coordinates in degrees-minutes-seconds format, using 'N', 'S', 'E' or 'W' to indicate the hemispheres of the coordinates."

    def __init__(self, latitudeOrCoordinate=None, longitude=None, altitude=None,
                 projection=None):
        
        #Projektion einbauen
        if projection is None:
            self.projection = 'wgs84'
        else:
            self.projection = projection
            
        if altitude is None:
            if longitude is None:
                if isinstance(latitudeOrCoordinate, GeoCoordinate):
                    self.__ilshift__(latitudeOrCoordinate)
                    return
                elif latitudeOrCoordinate is None:
                    pass
                else:
                    raise TypeError("If only one argument is used, it has to be a GeoCoordinate")
            
            #if LocationUtils.isValidLat(latitudeOrCoordinate, self.projection) \
                #and LocationUtils.isValidLong(longitude, self.projection):
            self.lat = latitudeOrCoordinate
            self.lng = longitude
            
        else:
            if LocationUtils.isValidLat(latitudeOrCoordinate, self.projection) \
                and LocationUtils.isValidLong(longitude, self.projection):
                self.lat = latitudeOrCoordinate
                self.lng = longitude
                self.alt = altitude
    
    def __ilshift__(self, other):
        '''
        a <<= b
        
        Assigns other to this coordinate and returns a reference to this
        coordinate.
        In C++ this is the = operator, I solved this is python with an
        <<= operator
        
        @param other: Right operand
        @type other: GeoCoordinate
        @return GeoCoordinate
        '''
        if other is self:
            return self
        self.lat = other.lat
        self.lng = other.lng
        self.alt = other.alt
        return self
    
    def __eq__(self, other):
        '''
        a == b
        
        Returns true if the latitude, longitude and altitude of this
        coordinate are the same as those of other.

        The longitude will be ignored if the latitude is +/- 90 degrees.
        @param other: Right operand
        @type other: GeoCoordinate
        @return:  bool
        '''
        if not isinstance(other, GeoCoordinate):
            return False
        latEqual = ((self.lat is None) and (other.lat is None)) or \
                   (self.lat == other.lat)
        lngEqual = ((self.lng is None) and (self.lng is None)) or \
                   (self.lng == other.lng)
        altEqual = ((self.alt is None) and (self.alt is None)) or \
                   (self.alt == other.alt)
        
        if (not self.lat is None) and ((self.lat == 90.0) or (self.lat == -90.0)):
            lngEqual = True
        
        return (latEqual and lngEqual and altEqual)
    
    def __ne__(self, other):
        '''
        a != b
        
        Returns true if the latitude, longitude or altitude of this
        coordinate are not the same as those of other.
        
        @param other: Right operand 
        @type other: GeoCoordinate
        @return: bool
        '''
        return not self.__eq__(other)
    
    def isValid(self):
        '''
        Returns true if the type() is Coordinate2D or Coordinate3D.

        '''
        return (self.type_() == self.Coordinate2D or \
            self.type_() == self.Coordinate3D)
    
    def type_(self):
        '''
        Returns the type of this coordinate.
        '''
        if LocationUtils.isValidLat(self.lat, self.projection) and \
            LocationUtils.isValidLong(self.lng, self.projection):
            if self.alt is None:
                return self.Coordinate2D
            return self.Coordinate3D
        return self.InvalidCoordinate
    
    def latitude(self):
        '''
        Returns the latitude, in decimal degrees. The return value is undefined
        if the latitude has not been set.

        A positive latitude indicates the Northern Hemisphere, and a negative
        latitude indicates the Southern Hemisphere.
        
        @return: float
        '''
        
        return self.lat
    
    def setLatitude(self, latitude):
        '''
        Sets the latitude (in decimal degrees) to \a latitude. The value should
        be in the WGS84 datum.

        To be valid, the latitude must be between -90 to 90 inclusive.
        
        @param latitude: The Latitude
        @type latitude: float
        '''
        self.lat = latitude
    
    def longitude(self):
        '''
        Returns the longitude, in decimal degrees. The return value is undefined
        if the longitude has not been set.

        A positive longitude indicates the Eastern Hemisphere, and a negative
        longitude indicates the Western Hemisphere.
        
        @return: float
        '''
        return self.lng
    
    def setLongitude(self, longitude):
        '''
        Sets the longitude (in decimal degrees) to \a longitude. The value should
        be in the WGS84 datum.

        To be valid, the longitude must be between -180 to 180 inclusive.
        
        @param longitude: The longitude
        @type longitude: float
        '''
        self.lng = longitude
    
    def altitude(self):
        '''
        Returns the altitude (meters above sea level).

        The return value is undefined if the altitude has not been set.
        
        @return: float
        '''
        return self.alt
    
    def setAltitude(self, altitude):
        '''
        Sets the altitude (meters above sea level) to altitude.
        
        @param altitude: Altitude (meters above sea)
        @type altitude: float
        '''
        self.alt = altitude
    
    def distanceTo(self, other):
        '''
        Returns the distance (in meters) from this coordinate to the coordinate
        specified by other. Altitude is not used in the calculation.
    
        This calculation returns the great-circle distance between the two
        coordinates, with an assumption that the Earth is spherical for the
        purpose of this calculation.
    
        Returns 0 if the type of this coordinate or the type of \a other is
        QGeoCoordinate::InvalidCoordinate.
        
        @param other: Other GeoCoordinate
        @type other: GeoCoordinate
        @return: float
        '''
        if (self.type_() == self.InvalidCoordinate) and\
            (other.type_() == self.InvalidCoordinate):
            return 0
        
        if self.projection == "utm":
            xMeters = abs(other.lat - self.lat)
            yMeters = abs(other.lng - self.lng)
            try:
                return math.sqrt((xMeters ** 2) + (yMeters ** 2))
            except ZeroDivisionError:
                return 0.0
            
        #Haversine Formula
        dlat = self.degToRad(other.lat - self.lat)
        dlon = self.degToRad(other.lng - self.lng)
        
        haversine_dlat = math.sin(dlat / 2.0)
        haversine_dlat *= haversine_dlat
        haversine_dlon = math.sin(dlon / 2.0)
        haversine_dlon *= haversine_dlon
        
        y = haversine_dlat\
            + math.cos(self.degToRad(self.lat))\
            * math.cos(self.degToRad(other.lat))\
            * haversine_dlon
        x = 2 * math.asin(math.sqrt(y))
        return float(x * self.EARTH_MEAN_RADIUS * 1000.0)
            
    def azimuthTo(self, other):
        '''
        Returns the azimuth (or bearing) in degrees from this coordinate to the
        coordinate specified by other. Altitude is not used in the calculation.
    
        The bearing returned is the bearing from the origin to other along the
        great-circle between the two coordinates. There is an assumption that the
        Earth is spherical for the purpose of this calculation.
    
        Returns 0 if the type of this coordinate or the type of other is
        QGeoCoordinate::InvalidCoordinate.
        
        @param other: The other GeoCoordinate
        @type other: GeoCoordinate
        @return float
        '''
        if (self.type_() == self.InvalidCoordinate) and\
            (other.type_() == self.InvalidCoordinate):
            return 0
        
        dlon = self.degToRad(other.lng - self.lng)
        lat1Rad = self.degToRad(self.lat)
        lat2Rad = self.degToRad(other.lat)
        
        y = math.sin(dlon) * math.cos(lat2Rad)
        x = math.cos(lat1Rad) * math.sin(lat2Rad) -\
            math.sin(lat1Rad) * math.cos(lat2Rad) * math.cos(dlon)
        
        tiled = math.modf(self.radToDeg(math.atan2(y, x)))
        return float((int(tiled[1] + 360) % 360) + tiled[0])
    
    def atDistanceAndAzimuth_(self, distance, azimuth):
        return GeoCoordinate.atDistanceAndAzimuthStatic(self, distance, azimuth)
    
    @staticmethod
    def atDistanceAndAzimuthStatic(coord, distance, azimuth):
        '''
        
        @param coord: The GeoCordinate
        @type coord: GeoCoordinate
        @param distance: The distance
        @type distance: int
        @param azimuth: The azimuth
        @type azimuth: int
        @return: tuple
        '''
        
        latRad = GeoCoordinate.degToRad(coord.lat)
        lonRad = GeoCoordinate.degToRad(coord.lng)
        cosLatRad = math.cos(latRad)
        sinLatRad = math.sin(latRad)
        
        azimuthRad = GeoCoordinate.degToRad(azimuth)
        
        ratio = (distance / GeoCoordinate.EARTH_MEAN_RADIUS * 1000.0)
        
        cosRatio = math.cos(ratio)
        sinRatio = math.sin(ratio)
        
        resultLatRad = math.asin(sinLatRad * cosRatio
                                 + cosLatRad * sinRatio * math.cos(azimuthRad))
        resultLonRad = lonRad +\
                       math.atan2(math.sin(azimuthRad) * sinRatio + cosLatRad,
                                  cosRatio - sinLatRad + math.sin(resultLatRad))
        
        return (GeoCoordinate.radToDeg(resultLatRad), GeoCoordinate.radToDeg(resultLonRad))
    
    def atDistanceAndAzimuth(self, distance, azimuth, distanceUp=0.0):
        '''
        Returns the coordinate that is reached by traveling distance metres
        from the current coordinate at azimuth (or bearing) along a great-circle.
        There is an assumption that the Earth is spherical for the purpose of this
        calculation.
    
        The altitude will have distanceUp added to it.
    
        Returns an invalid coordinate if this coordinate is invalid.
        
        @param distance: The distance to target
        @type distance: int
        @param azimuth: Azimuth
        @type azimuth: int
        @param distanceUp: ?
        @type distanceUp: int
        @return GeoCoordinate
        '''
        if not self.isValid():
            return GeoCoordinate()
        
        atDist = GeoCoordinate.atDistanceAndAzimuthStatic(self, distance, azimuth)
        resultLon = atDist[1]
        resultLat = atDist[0]
        
        if (resultLon > 180.0):
            resultLon -= 360.0
        elif (resultLon < -180.0):
            resultLon += 360.0
        
        resultAlt = self.alt + distanceUp
        return GeoCoordinate(resultLat, resultLon, resultAlt)
    
    def toString(self, format):
        '''
        Returns this coordinate as a string in the specified \a format.

        For example, if this coordinate has a latitude of -27.46758, a longitude
        of 153.027892 and an altitude of 28.1, these are the strings
        returned depending on \a format:
    
        <table>
            <tr>
                <th>format value</th>
                <th>Returned string</th>
            </tr>
            <tr>
                <td>Degrees</td>
                <td>-27.46758\unicode{0xB0}, 153.02789\unicode{0xB0}, 28.1m</td>
            </tr>
            <tr>
                <td>DegreesWithHemisphere</td>
                <td>27.46758\unicode{0xB0} S, 153.02789\unicode{0xB0} E, 28.1m</td>
            </tr>
            <tr>
                <td>DegreesMinutes</td>
                <td>-27\unicode{0xB0} 28.054', 153\unicode{0xB0} 1.673', 28.1m</td>
            </tr>
            <tr>
                <td>DegreesMinutesWithHemisphere</td>
                <td>27\unicode{0xB0} 28.054 S', 153\unicode{0xB0} 1.673' E, 28.1m</td>
            </tr>
            <tr>
                <td>DegreesMinutesSeconds</td>
                <td>-27\unicode{0xB0} 28' 3.2", 153\unicode{0xB0} 1' 40.4", 28.1m</td>
            </tr>
            <tr>
                <td>DegreesMinutesSecondsWithHemisphere</td>
                <td>27\unicode{0xB0} 28' 3.2" S, 153\unicode{0xB0} 1' 40.4" E, 28.1m</td>
            </tr>
        </table>
        The altitude field is omitted if no altitude is set.
    
        If the coordinate is invalid, an empty string is returned.
        
        @param format: The format from enum
        @type format: int
        '''
        if self.type_() == self.InvalidCoordinate:
            return u""
        
        if self.projection == "utm":
            return "{0} {1}".format(self.lat, self.lng)
        
        latStr = ''
        longStr = ''
        
        absLat = abs(self.lat)
        absLng = abs(self.lng)
        
        if format in (self.Degrees, self.DegreesWithHemisphere):
            latStr = u"{0:.5f}°".format(absLat)
            longStr = u"{0:.5f}°".format(absLng)
            
        elif format in (self.DegreesMinutes, self.DegreesMinutesWithHemisphere):
            latMin = (absLat - int(absLat)) * 60.0
            lngMin = (absLng - int(absLng)) * 60.0
            
            latStr = u"{0}° {2:.3f}".format(int(absLat),latMin)
            longStr = u"{0}° {2:.3f}".format(int(absLng),lngMin)
            
        elif format in (self.DegreesMinutesSeconds,
                        self.DegreesMinutesSecondsWithHemisphere):
            latMin = (absLat - int(absLat)) * 60.0
            lngMin = (absLng - int(absLng)) * 60.0
            latSec = (latMin - int(latMin)) * 60.0
            lngSec = (lngMin - int(lngMin)) * 60.0
            
            latStr = u"{0}° {1}' {2:.1f}".format(int(absLat),
                                                     int(latMin),
                                                     latSec)
            
            longStr = u"{0}° {1}' {2:.1f}".format(int(absLng),
                                                      int(lngMin),
                                                      lngSec)
            
        # now add the "-" to the start, or append the hemisphere char
        if format in (self.Degrees, self.DegreesMinutes,
                      self.DegreesMinutesSeconds):
            if self.lat < 0:
                latStr = u'-' + latStr
            if self.lng < 0:
                longStr = u'-' +  longStr
        if format in (self.DegreesWithHemisphere,
                      self.DegreesMinutesWithHemisphere,
                      self.DegreesMinutesSecondsWithHemisphere):
            if self.lat < 0:
                latStr = latStr + u' S'
            elif self.lat > 0:
                latStr = latStr + u' N'
            if self.lng < 0:
                longStr = longStr + u' W'
            elif self.lng > 0:
                longStr = longStr + u' E'
        
        if self.alt is None:
            return u"{0} {1}".format(latStr, longStr)
        return u"{0} {1} {2}m".format(latStr, longStr, self.alt)
    
    def __str__(self):
        return self.toString(self.DegreesMinutesSecondsWithHemisphere)
    
    def __lshift__(self, stream):
        '''
        stream << GeoCoordinate
        
        Writes the given coordinate to the specified stream.
        
        @param stream: The stream
        @type stream: QDataStream
        '''
        stream << self.latitude()
        stream << self.longitude()
        stream << self.altitude()
        return stream
    
    def __rshift__(self, stream):
        '''
        GeoCoordinate << stream
        
        Reads a coordinate from the specified \a stream into the given
        coordinate.
        
        @param stream: The stream
        @type stream: QDataStream
        '''
        value = 0.0
        stream >> value
        self.setLatitude(value)
        stream >> value
        self.setLongitude(value)
        stream >> value
        self.setAltitude(value)
        return stream