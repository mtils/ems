'''
Created on 15.11.2011

@author: michi
'''
class GeoAddress(object):
    '''
    \brief The QGeoAddress class represents an address

    \inmodule QtLocation
    \since 1.1

    \ingroup location

    This class represents an address of a location.
    '''
    
    _sCountry = unicode() #!< country field
    _sCountryCode = unicode() #!< country code field
    _sState = unicode() #!< state field
    _sCounty = unicode() #/!< county field
    _sCity = unicode() #!< city field
    _sDistrict = unicode() #!< district field
    _sStreet = unicode() #!< street name field
    _sPostCode = unicode() #!< post code field
    
    def __init__(self, other=None):
        '''
        If other passed, constructs a copy of \a other.
        
        @param other: Optional other GeoAddress
        @type other: GeoAddress
        '''
        if isinstance(other, GeoAddress):
            self.__ilshift__(other)
    
    def __ilshift__(self, other):
        '''
        self <<= other
        
        replacement for c++ = operator overloading
        @param other: The other GeoAddress
        @type other: GeoAddress  
        '''
        self._sCountry = other._sCountry
        self._sCountryCode = other._sCountryCode
        self._sState = other._sState
        self._sCounty = other._sCounty
        self._sCity = other._sCity
        self._sDistrict = other._sDistrict
        self._sStreet = other._sStreet
        self._sPostCode = other._sPostCode
    
    def __eq__(self, other):
        '''
        self == other
        
        Returns true if this address is equal to \a other,
        otherwise returns false.
        
        @param other: The right operand
        @type other: GeoAddress
        '''
        if not isinstance(other, GeoAddress):
            return False
        for prop in ('_sCountry', '_sCountryCode', '_sState', '_sCounty',
                     '_sCity', '_sDistrict', '_sStreet', '_sPostCode'):
            if self.__getattribute__(prop) != other.__getattribute__(prop):
                return False
        return True
    
    def __ne__(self, other):
        '''
        self != other
        
        Returns true if this address is not equal to \a other,
           otherwise returns false.
        @param other: The right operand
        @type other: GeoAddress
        '''
        return not self.__eq__(other)
    
    def country(self):
        '''
        Returns the country name.
        @rtype: basestring
        '''
        return self._sCountry
    
    def setCountry(self, country):
        '''
        Sets the \a country name.
        
        @param country: The country name
        @type country: basestring
        '''
        self._sCountry = country#
    
    def countryCode(self):
        '''
        Returns the country code according to ISO 3166-1 alpha-3
        @rtype: str
        '''
        return self._sCountryCode
    
    def setCountryCode(self, countryCode):
        '''
        Sets the \a countryCode according to ISO 3166-1 alpha-3
        
        @param countryCode: the new countryCode
        @type countryCode: str
        '''
        self._sCountryCode = countryCode
    
    def state(self):
        '''
        Returns the state.  The state is considered the first subdivision below country.
        @rtype: basestring
        '''
        return self._sState
    
    def setState(self, state):
        '''
        Sets the \a state.
        
        @param state: State
        @type state: basestring
        '''
        self._sState = state
    
    def county(self):
        '''
        Returns the county.  The county is considered the second subdivision below country.
        @rtype: basestring
        '''
        return self._sCounty
    
    def setCounty(self, county):
        '''
        Sets the \a county.
        
        @param county: The county
        @type county: basestring
        '''
        self._sCounty = county
    
    def city(self):
        '''
        Returns the city.
        @rtype: basestring
        '''
        return self._sCity
    
    def setCity(self, city):
        '''
        Sets a city
        
        @param city: The city
        @type city: basestring
        '''
        self._sCity = city
    
    def district(self):
        '''
        Returns the district.  The district is considered the subdivison below city.
        @rtype: basestring
        '''
        return self._sDistrict
    
    def setDistrict(self, district):
        '''
        Sets a district
        
        @param district: The district
        @type district: basestring
        '''
        self._sDistrict = district
    
    def street(self):
        '''
         Returns the street-level component of the address.

        This typically includes a street number and street name
        but may also contain things like a unit number, a building
        name, or anything else that might be used to
        distinguish one address from another.
        '''
        return self._sStreet
    
    def setStreet(self, street):
        '''
        Sets the street-level component of the address to \a street.

        This typically includes a street number and street name
        but may also contain things like a unit number, a building
        name, or anything else that might be used to
        distinguish one address from another.
        
        @param street: The street and housenr or number etc
        @type street: basestring
        '''
        self._sStreet = street
    
    def postcode(self):
        '''
        Returns the post code.
        @rtype: basestring
        '''
        return self._sPostCode
    
    def setPostCode(self, postcode):
        '''
        Sets the postcode
        
        @param postcode: Sets a postcode
        @type postcode: basestring
        '''
        self._sPostCode = postcode
    
    def isEmpty(self):
        '''
        Returns whether this address is empty. An address is considered empty
        if \i all of its fields are empty.
        @rtype: bool
        '''
        for prop in ('_sCountry', '_sCountryCode', '_sState', 'sCounty',
                     '_sCity', '_sDistrict', '_sStreet', '_sPostCode'):
            if len(self.__getattribute__(prop).strip()) > 0:
                return False
        return True
    
    def __nonzero__(self):
        return not self.isEmpty()
    
    def clear(self):
        '''
        Clears the all the address' data fields.
        '''
        self._sCountry = ""
        self._sCountryCode = ""
        self._sState = ""
        self._sCounty = ""
        self._sCity = ""
        self._sDistrict = ""
        self._sStreet = ""
        self._sPostCode = ""
        