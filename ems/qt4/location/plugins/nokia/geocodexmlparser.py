'''
Created on 16.11.2011

@author: michi
'''
from PyQt4.QtCore import QXmlStreamReader, QString
from ems.qt4.location.geoplace import GeoPlace
from ems.qt4.location.geoaddress import GeoAddress #@UnresolvedImport
from ems.qt4.location.geocoordinate import GeoCoordinate
from ems.qt4.location.geoboundingbox import GeoBoundingBox

class GeoCodeXmlParser(object):
    _m_reader = QXmlStreamReader
    _m_results = []
    _m_errorString = ""
    
    def __init__(self):
        self._m_reader = QXmlStreamReader()
        self._errorCallback = None
    
    def setErrorCallback(self, callback):
        if callable(callback):
            self._errorCallback = callback
            
    
    def parse(self, source):
        '''
        @param source: QIODevice
        @type source: QIODevice
        @rtype: bool
        '''
        if self._m_reader:
            del self._m_reader
        self._m_reader = QXmlStreamReader(source)
    
        if not self._parseRootElement():
            self._m_errorString = self._m_reader.errorString()
            return False;
        
    
        self._m_errorString = "";
    
        return True
    
    def _raiseError(self, errorMsg):
        self._m_reader.raiseError(QString(errorMsg))
        #return
        #print "ich bin dat"
        if callable(self._errorCallback):
            self._errorCallback(errorMsg)
    
    def results(self):
        '''
        @rtype: list
        '''
        return self._m_results
    
    def errorString(self):
        '''
        @rtype: basestring
        '''
        return self._m_errorString
    
    def _parseRootElement(self):
        '''
        <xsd:element name="places">
            <xsd:complexType>
                <xsd:sequence>
                    <xsd:element minOccurs="0" maxOccurs="unbounded" name="place" type="gc:Place"/>
                </xsd:sequence>
                <xsd:attribute name="resultCode" type="gc:ResultCodes"/>
                <xsd:attribute name="resultDescription" type="xsd:string"/>
                <xsd:attribute name="resultsTotal" type="xsd:nonNegativeInteger"/>
            </xsd:complexType>
        </xsd:element>
    
        <xsd:simpleType name="ResultCodes">
            <xsd:restriction base="xsd:string">
                <xsd:enumeration value="OK"/>
                <xsd:enumeration value="FAILED"/>
            </xsd:restriction>
        </xsd:simpleType>
        @rtype: bool
        '''
        if self._m_reader.readNextStartElement():
            if self._m_reader.name() == "places":
                if self._m_reader.attributes().hasAttribute("resultCode"):
                    result = self._m_reader.attributes().value("resultCode")
                    if result == "FAILED":
                        resultDesc = self._m_reader.attributes().value("resultDescription").toString()
                        if resultDesc.isEmpty():
                            resultDesc = "The attribute \"resultCode\" of the element \"places\" indicates that the request failed."
                        
                        self._raiseError(resultDesc)
                        
                        return False
                    elif result != "OK":
                        self._raiseError("The attribute \"resultCode\" of the element \"places\" has an unknown value (value was {0}).".format(result.toString()))
                
                while self._m_reader.readNextStartElement():
                    if self._m_reader.name() == "place":
                        place = GeoPlace()
                        
                        if not self._parsePlace(place):
                            return False
                        
                        self._m_results.append(place)
                    else:
                        self._raiseError("The element \"places\" did not expect a child element named \"{0}\".".format(self._m_reader.name().toString()))
                        return False
            else:
                self._raiseError("The root element is expected to have the name \"places\" (root element was named \"{0}\").".format(self._m_reader.name().toString()))
                return False      
        else:
            self._raiseError("Expected a root element named \"places\" (no root element found).")
            return False
        
        if (self._m_reader.readNextStartElement()):
            self._raiseError("A single root element named \"places\" was expected (second root element was named \"{0}\")".format(self._m_reader.name().toString()))
            return False
        
        return True
    
    def _parsePlace(self, place):
        '''
        <xsd:complexType name="Place">
            <xsd:all>
                <xsd:element name="location" type="gc:Location"/>
                <xsd:element minOccurs="0" name="address" type="gc:Address"/>
                <xsd:element minOccurs="0" name="alternatives" type="gc:Alternatives"/>
            </xsd:all>
            <xsd:attribute name="title" type="xsd:string" use="required"/>
            <xsd:attribute name="language" type="gc:LanguageCode" use="required"/>
        </xsd:complexType>
    
        <xsd:simpleType name="LanguageCode">
            <xsd:restriction base="xsd:string">
                <xsd:length value="3"/>
            </xsd:restriction>
        </xsd:simpleType>
        
        @param place: GeoPlace
        @type place: GeoPlace
        '''
        if not self._m_reader.isStartElement() or self._m_reader.name() != 'place':
            raise TypeError("Place is no startelement or not place tag")
        
        if not self._m_reader.attributes().hasAttribute("title"):
            self._raiseError("The element \"place\" did not have the required attribute \"title\".")
            return False
        
        place.nokiaName = self._m_reader.attributes().value("title")
        
        if not self._m_reader.attributes().hasAttribute("language"):
            pass
            #self._raiseError("The element \"place\" did not have the required attribute \"language\".")
            #return False
        else:
            lang = self._m_reader.attributes().value("language").toString()
            if lang.size() != 3:
                self._raiseError("The attribute \"language\" of the element \"place\" was not of length 3 (length was {0}).".format(lang.length()))
                return False
        
        parsedLocation = False
        parsedAddress = False
        parsedAlternatives = False
        
        while (self._m_reader.readNextStartElement()):
            name = self._m_reader.name().toString()
            if name == "location":
                if parsedLocation:
                    self._raiseError("The element \"place\" has multiple child elements named \"location\" (exactly one expected)")
                    return False
            
                if not self._parseLocation(place):
                    return False
            
                parsedLocation = True
            elif name == "address":
                if parsedAddress:
                    self._raiseError("The element \"place\" has multiple child elements named \"address\" (at most one expected)")
                    return False
                
                address = GeoAddress()
                if not self._parseAddress(address):
                    return False
                else:
                    place.setAddress(address)
                    
                    parsedAddress = True
            elif name == "alternatives":
                if parsedAlternatives:
                    self._raiseError("The element \"place\" has multiple child elements named \"alternatives\" (at most one expected)")
                    return False
                
                # skip alternatives for now
                # need to work out if we have a use for them at all
                # and how to store them if we get them
                self._m_reader.skipCurrentElement()
                
                parsedAlternatives = True
            else:
                self._raiseError("The element \"place\" did not expect a child element named \"{0}\".".format(self._m_reader.name().toString()))
                return False
            
        if not parsedLocation:
            self._raiseError("The element \"place\" has no child elements named \"location\" (exactly one expected)")
            return False
        
        return True
    
    def _parseLocation(self, place):
        '''
        <xsd:complexType name="Location">
            <xsd:all>
                <xsd:element name="position" type="gc:GeoCoord"/>
                <xsd:element minOccurs="0" name="boundingBox" type="gc:GeoBox"/>
            </xsd:all>
        </xsd:complexType>
    
        <xsd:complexType name="GeoBox">
            <xsd:sequence>
                <xsd:element name="northWest" type="gc:GeoCoord"/>
                <xsd:element name="southEast" type="gc:GeoCoord"/>
            </xsd:sequence>
        </xsd:complexType>
        
        @param place: GeoPlace
        @type place: GeoPlace
        '''
        if not self._m_reader.isStartElement() or self._m_reader.name() != 'location':
            raise TypeError("Place is no startelement or not location tag")
        
        parsedPosition = False
        parsedBounds = False
        
        while self._m_reader.readNextStartElement():
            name = self._m_reader.name().toString()
            if name == "position":
                if parsedPosition:
                    self._raiseError("The element \"location\" has multiple child elements named \"position\" (exactly one expected)")
                    return False
                
                coord = GeoCoordinate()
                if not self._parseCoordinate(coord, 'position'):
                    return False
                
                place.setCoordinate(coord)
                
                parsedPosition = True
            elif name == "boundingBox":
                if parsedBounds:
                    self._raiseError("The element \"location\" has multiple child elements named \"boundingBox\" (at most one expected)")
                    return False
                
                bounds = GeoBoundingBox()
                
                if not self._parseBoundingBox(bounds):
                    return False
                
                place.setViewport(bounds)
                
                parsedBounds = True
            else:
                self._raiseError("The element \"location\" did not expect a child element named \"{0}\".".format(self._m_reader.name().toString()))
                return False
            
        if not parsedPosition:
            self._raiseError("The element \"location\" has no child elements named \"position\" (exactly one expected)")
            return False
        return True
    
    def _parseAddress(self, address):
        '''
        <xsd:complexType name="Address">
            <xsd:sequence>
                <xsd:element minOccurs="0" maxOccurs="1" name="country" type="xsd:string"/>
                <xsd:element minOccurs="0" maxOccurs="1" name="countryCode" type="gc:CountryCode"/>
                <xsd:element minOccurs="0" maxOccurs="1" name="state" type="xsd:string"/>
                <xsd:element minOccurs="0" maxOccurs="1" name="county" type="xsd:string"/>
                <xsd:element minOccurs="0" maxOccurs="1" name="city" type="xsd:string"/>
                <xsd:element minOccurs="0" maxOccurs="1" name="district" type="xsd:string"/>
                <xsd:element minOccurs="0" maxOccurs="1" name="thoroughfare" type="gc:Thoroughfare"/>
                <xsd:element minOccurs="0" maxOccurs="1" name="postCode" type="xsd:string"/>
            </xsd:sequence>
            <xsd:attribute name="type" type="xsd:string"/>
        </xsd:complexType>
    
        <xsd:simpleType name="CountryCode">
            <xsd:restriction base="xsd:string">
                <xsd:length value="3" fixed="true"/>
            </xsd:restriction>
        </xsd:simpleType>
    
        <xsd:complexType name="Thoroughfare">
            <xsd:sequence>
                <xsd:element minOccurs="0" name="name" type="xsd:string"/>
                <xsd:element minOccurs="0" name="number" type="xsd:string"/>
            </xsd:sequence>
        </xsd:complexType>
        
        @param address: The address
        @type address: GeoAddress
        '''
        if not self._m_reader.isStartElement() or self._m_reader.name() != 'address':
            raise TypeError("Place is no startelement or not location tag")
        
        if not self._m_reader.readNextStartElement():
            return True
        
        if self._m_reader.name() == "country":
            address.setCountry(self._m_reader.readElementText())
            if not self._m_reader.readNextStartElement():
                return True
        
        if self._m_reader.name() == "countryCode":
            address.setCountryCode(self._m_reader.readElementText())
    
            if address.countryCode().length() != 3:
                self._raiseError("The text of the element \"countryCode\" was not of length 3 (length was {0}).".format(address.countryCode().length()))
                return False
            
    
            if not self._m_reader.readNextStartElement():
                return True
            
        if self._m_reader.name() == "state":
            address.setState(self._m_reader.readElementText())
            if not self._m_reader.readNextStartElement():
                return True
        
        if self._m_reader.name() == "county":
            address.setCounty(self._m_reader.readElementText())
            if not self._m_reader.readNextStartElement():
                return True
        
        if self._m_reader.name() == "city":
            address.setCity(self._m_reader.readElementText())
            if not self._m_reader.readNextStartElement():
                return True
        
        if self._m_reader.name() == "district":
            address.setDistrict(self._m_reader.readElementText())
            if not self._m_reader.readNextStartElement():
                return True
        
        inThoroughfare = False
        
        if self._m_reader.name() == "thoroughfare":
            inThoroughfare = self._m_reader.readNextStartElement()
            
            if inThoroughfare and (self._m_reader.name() == "name"):
                address.setStreet(self._m_reader.readElementText())
                if not self._m_reader.readNextStartElement():
                    inThoroughfare = False
            
            if inThoroughfare and (self._m_reader.name() == "number"):
                address.setStreet(self._m_reader.readElementText() + " " + address.street())
                if not self._m_reader.readNextStartElement():
                    inThoroughfare = False
            
            if inThoroughfare:
                self._raiseError("The element \"thoroughFare\" did not expect the child element \"{0}\" at this point (unknown child element or child element out of order).".format(self._m_reader.name().toString()))
                return False
            
            if not self._m_reader.readNextStartElement():
                return True
        
        if self._m_reader.name() == "postCode":
            address.setPostcode(self._m_reader.readElementText())
            if not self._m_reader.readNextStartElement():
                return True
        
        self._raiseError("The element \"address\" did not expect the child element \"{0}\" at this point (unknown child element or child element out of order).".format(self._m_reader.name().toString()))
        return False
    
    def _parseBoundingBox(self, bounds):
        '''
        <xsd:complexType name="GeoBox">
            <xsd:sequence>
                <xsd:element name="northWest" type="gc:GeoCoord"/>
                <xsd:element name="southEast" type="gc:GeoCoord"/>
            </xsd:sequence>
        </xsd:complexType>
        
        @param bounds: The bounds
        @type bounds: GeoBoundingBox
        '''
        if not self._m_reader.isStartElement() or self._m_reader.name() != 'boundingBox':
            raise TypeError("Place is no startelement or not boundingBox tag")
        
        if not self._m_reader.readNextStartElement():
            self._raiseError("The element \"boundingBox\" was expected to have 2 child elements (0 found)")
            return False
        
        nw = GeoCoordinate()
        
        if self._m_reader.name() == "northWest":
            if not self._parseCoordinate(nw, "northWest"):
                return False
        else:
            self._raiseError("The element \"boundingBox\" expected this child element to be named \"northWest\" (found an element named \"{0}\")".format(self._m_reader.name().toString()))
            return False
        
        if not self._m_reader.readNextStartElement():
            self._raiseError("The element \"boundingBox\" was expected to have 2 child elements (1 found)")
            return False
        
        se = GeoCoordinate()
        
        if self._m_reader.name() == "southEast":
            if not self._parseCoordinate(se, "southEast"):
                return False
        else:
            self._raiseError("The element \"boundingBox\" expected this child element to be named \"southEast\" (found an element named \"{0}\")".format(self._m_reader.name().toString()))
            return False
        
        if self._m_reader.readNextStartElement():
            self._raiseError("The element \"boundingBox\" was expected to have 2 child elements (more than 2 found)")
            return False
        
        
        bounds.setTopLeft(nw)
        bounds.setBottomRight(se)
        
        return True
    
    def _parseCoordinate(self, coordinate, elementName):
        '''
        <xsd:complexType name="GeoCoord">
            <xsd:sequence>
                <xsd:element name="latitude" type="gc:Latitude"/>
                <xsd:element name="longitude" type="gc:Longitude"/>
            </xsd:sequence>
        </xsd:complexType>
    
        <xsd:simpleType name="Latitude">
            <xsd:restriction base="xsd:float">
                <xsd:minInclusive value="-90.0"/>
                <xsd:maxInclusive value="90.0"/>
            </xsd:restriction>
        </xsd:simpleType>
    
        <xsd:simpleType name="Longitude">
            <xsd:restriction base="xsd:float">
                <xsd:minInclusive value="-180.0"/>
                <xsd:maxInclusive value="180.0"/>
            </xsd:restriction>
        </xsd:simpleType>
        
        @param coordinate: The GeoCoordinate which will be filled
        @type coordinate: GeoCoordinate
        @param elementName: The name of the element to extract
        @type elementName: basestring
        '''
        if not self._m_reader.isStartElement() or self._m_reader.name() != elementName:
            raise TypeError("{0} is no startelement or not {1} tag".format(elementName, elementName))
        
        if not self._m_reader.readNextStartElement():
            self._raiseError("The element \"{0}\" was expected to have 2 child elements (0 found)".format(elementName))
            return False
        
        if self._m_reader.name() == "latitude":
            
            s = self._m_reader.readElementText()
            lat = float(unicode(s))
            
            if lat < -90.0 or 90.0 < lat:
                self._raiseError("The element \"latitude\" expected a value between -90.0 and 90.0 inclusive (value was {0})".format(lat))
                return False
            
            coordinate.setLatitude(lat)
        else:
            self._raiseError("The element \"{0}\" expected this child element to be named \"latitude\" (found an element named \"{1}\")".format(elementName, self._m_reader.name().toString()))
        
        if not self._m_reader.readNextStartElement():
            self._raiseError("The element \"{0}\" was expected to have 2 child elements (1 found)".format(elementName))
            return False
        
        if self._m_reader.name() == "longitude":
            
            s = self._m_reader.readElementText()
            lng = float(s)
            
            if lng < -180.0 or 180.0 < lng:
                self._raiseError("The element \"longitude\" expected a value between -180.0 and 180.0 inclusive (value was {0})".format(lng))
                return False
        
            coordinate.setLongitude(lng)
        
        else:
            self._raiseError("The element \"{0}\" expected this child element to be named \"longitude\" (found an element named \"{1}\")".format(elementName, self._m_reader.name().toString()))
        
        if self._m_reader.readNextStartElement():
            self._raiseError("The element \"{0}\" was expected to have 2 child elements (more than 2 found)".format(elementName))
            return False
        
        return True
        
        
        