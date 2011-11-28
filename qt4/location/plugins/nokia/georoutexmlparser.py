'''
Created on 17.11.2011

@author: michi
'''
from PyQt4.QtCore import QXmlStreamReader, QString

from ems.qt4.location.maps.geomaneuver import GeoManeuver
from ems.qt4.location.maps.georoutesegment import GeoRouteSegment #@UnresolvedImport
from ems.qt4.location.maps.georouterequest import GeoRouteRequest #@UnresolvedImport
from ems.qt4.location.maps.georoute import GeoRoute #@UnresolvedImport
from ems.qt4.location.geoboundingbox import GeoBoundingBox
from ems.qt4.location.geocoordinate import GeoCoordinate

class GeoManeuverContainer(object):
    maneuver = GeoManeuver()
    id_ = ""
    toId = ""
    def __init__(self):
        self.maneuver = GeoManeuver()

class GeoRouteSegmentContainer(object):
    segment = GeoRouteSegment()
    id_ = ""
    maneuverId = ""
    def __init__(self):
        self.segment = GeoRouteSegment()
    
class GeoRouteXmlParser(object):
    
    _m_request = GeoRouteRequest
    
    _m_reader = QXmlStreamReader
    
    _m_results = []
    
    _m_errorString = ""
    
    _maneuvers = []
    
    _segments = []
    
    def __init__(self, request):
        '''
        @param request: GeoRouteRequest
        @type request: GeoRouteRequest
        '''
        self._m_request = request
        self._m_reader = None
    
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
            return False
        
        self._m_errorString = ""
        return True
    
    def results(self): 
        '''
        List of GeoRoute objects
        @rtype: list
        '''
        return self._m_results
    
    def errorString(self):
        '''
        @rtype:QString
        '''
        return self._m_reader.errorString()
    
    def _parseRootElement(self):
        '''
        @rtype: bool
        '''
        
        if not self._m_reader.readNextStartElement():
            self._m_reader.raiseError("Expected a root element named \"CalculateRoute\" (no root element found).")
            return False
        
        updateroute = False
        if self._m_reader.name() != "CalculateRoute" and self._m_reader.name() != "GetRoute":
            self._m_reader.raiseError(QString("The root element is expected to have the name \"CalculateRoute\" or \"GetRoute\" (root element was named \"%1\").").arg(self._m_reader.name().toString()))
            return False
        elif self._m_reader.name() == "GetRoute":
            updateroute = True
        
        if self._m_reader.readNextStartElement():
            if self._m_reader.name() != "Response":
                self._m_reader.raiseError(QString("Expected a element named \"Response\" (element was named \"%1\").").arg(self._m_reader.name().toString()))
                return False

        while self._m_reader.readNextStartElement():
            if self._m_reader.name() == "MetaInfo":
                self._m_reader.skipCurrentElement()
            elif self._m_reader.name() == "Route":
                route = GeoRoute()
                route.setRequest(self._m_request)
                if updateroute:
                    route.setTravelMode(int(self._m_request.travelModes()))
                if not self.parseRoute(route):
                    continue #route parsing failed move on to the next
                self._m_results.append(route)
            elif self._m_reader.name() == 'Progress':
                #TODO: updated route progress
                self._m_reader.skipCurrentElement()
            else:
                self._m_reader.raiseError(QString("Did not expect a child element named \"%1\".").arg(self._m_reader.name().toString()))
                return False
        return True
    
    def parseRoute(self, route):
        '''
        @param route: GeoRoute
        @type route: GeoRoute
        @rtype: bool
        '''
        elementName = "Route"
        if not self._m_reader.isStartElement() or self._m_reader.name() != elementName:
            raise TypeError("{0} is no startelement or not {1} tag".format(elementName, elementName))
        
        self._maneuvers = []
        self._segments = []
        
        self._m_reader.readNext()
        succeeded = True
        
        
        while not (self._m_reader.tokenType() == QXmlStreamReader.EndElement \
                   and self._m_reader.name() == "Route"):
#            print "    {0}".format(self._m_reader.name())
            elementSkipped = False
            if self._m_reader.tokenType() == QXmlStreamReader.StartElement and succeeded:
                if self._m_reader.name() == "RouteId":
                    route.setRouteId(self._m_reader.readElementText())
                
                elif self._m_reader.name() == "Mode":
                    succeeded = self._parseMode(route)
                elif self._m_reader.name() == "Shape":
                    elementName = self._m_reader.name().toString()
                    path = []
                    succeeded = self._parseGeoPoints(self._m_reader.readElementText(), path, elementName)
                    if succeeded:
                        route.setPath(path)
                elif self._m_reader.name() == "BoundingBox":
                    bounds = GeoBoundingBox()
                    succeeded = self._parseBoundingBox(bounds)
                    if succeeded:
                        route.setBounds(bounds)
                elif self._m_reader.name() == "Leg":
                    succeeded = self._parseLeg()
                elif self._m_reader.name() == "Summary":
                    succeeded = self._parseSummary(route)
                else:
                    self._m_reader.skipCurrentElement()
                    elementSkipped = True
                    
            if not elementSkipped:
                self._m_reader.readNext()
        
        if succeeded:
            succeeded = self._postProcessRoute(route)
    
        return succeeded
    
    def _parseLeg(self):
        '''
        @rtype: bool
        '''
        elementName = "Leg"
        if not self._m_reader.isStartElement() or self._m_reader.name() != elementName:
            raise TypeError("{0} is no startelement or not {1} tag".format(elementName, elementName))
        
        self._m_reader.readNext()
        succeeded = True
        while not (self._m_reader.tokenType() == QXmlStreamReader.EndElement \
                   and self._m_reader.name() == "Leg"):
            if self._m_reader.tokenType() == QXmlStreamReader.StartElement and succeeded:
                if self._m_reader.name() == "Maneuver":
                    succeeded = self._parseManeuver()
                elif self._m_reader.name() == "Link":
                    succeeded = self._parseLink()
                else:
                    self._m_reader.skipCurrentElement()
                    
            self._m_reader.readNext()
        
        return succeeded
    
    def _postProcessRoute(self, route):
        '''
        @param route: GeoRoute
        @type route: GeoRoute
        '''
        
        routeSegments = []
        
        maneuverIndex = 0
        
        segLength = len(self._segments)
        
        for i in range(segLength):
            while maneuverIndex < len(self._maneuvers) and not len(self._maneuvers[maneuverIndex].toId):
                segment = GeoRouteSegment()
                segment.setManeuver(self._maneuvers[maneuverIndex].maneuver)
                path = [] # use instruction position as one point segment path
                path.append(self._maneuvers[maneuverIndex].maneuver.position())
                segment.setPath(path)
                routeSegments.append(segment)
                maneuverIndex += 1
                
            segment = self._segments[i].segment
            if (maneuverIndex < len(self._maneuvers)) and \
                self._segments[i].id_ == self._maneuvers[maneuverIndex].toId:
                segment.setManeuver(self._maneuvers[maneuverIndex].maneuver)
                maneuverIndex += 1
            routeSegments.append(segment)
        
        compactedRouteSegments = []
        compactedRouteSegments.append(routeSegments.pop(0))
        
        while len(routeSegments) > 0:
            segment = routeSegments.pop(0)
            
            lastIndex = len(compactedRouteSegments)-1
#            if lastIndex < 0:
#                break
            lastSegment = compactedRouteSegments[lastIndex]
            
            if lastSegment.maneuver().isValid():
                compactedRouteSegments.append(segment)
            else:
                compactedRouteSegments.pop()
                lastSegment.setDistance(lastSegment.distance() + segment.distance())
                lastSegment.setTravelTime(lastSegment.travelTime() + segment.travelTime())
                path = lastSegment.path()
                #print type(path)
                for coord in segment.path():
                    path.append(coord)
                #path.append(segment.path())
                lastSegment.setPath(path)
                lastSegment.setManeuver(segment.maneuver())
                compactedRouteSegments.append(lastSegment)
    
        if len(compactedRouteSegments) > 0:
            route.setFirstRouteSegment(compactedRouteSegments[0])
            for i in range(len(compactedRouteSegments)-1):
                compactedRouteSegments[i].setNextRouteSegment(compactedRouteSegments[i + 1])
        
        self._maneuvers = []
        self._segments = []
        
        return True
    
    def _parseMode(self, route):
        '''
        @param route: GeoRoute
        @type route: GeoRoute
        @rtype: bool
        '''
        elementName = "Mode"
        if not self._m_reader.isStartElement() or self._m_reader.name() != elementName:
            raise TypeError("{0} is no startelement or not {1} tag".format(elementName, elementName))
        self._m_reader.readNext()
        while not (self._m_reader.tokenType() == QXmlStreamReader.EndElement \
                   and self._m_reader.name() == "Mode"):
#            print "        {0}".format(self._m_reader.name())
            #elementSkipped = False
            if self._m_reader.tokenType() == QXmlStreamReader.StartElement:
                if self._m_reader.name() == "TransportModes":
                    value = self._m_reader.readElementText()
                    if value == "car":
                        route.setTravelMode(GeoRouteRequest.CarTravel)
                    elif value == "pedestrian":
                        route.setTravelMode(GeoRouteRequest.PedestrianTravel)
                    elif value == "publicTransport":
                        route.setTravelMode(GeoRouteRequest.PublicTransitTravel)
                    elif value == "bicycle":
                        route.setTravelMode(GeoRouteRequest.BicycleTravel)
                    elif value == "truck":
                        route.setTravelMode(GeoRouteRequest.TruckTravel)
                    else: #unsupported optimization
                        return False
                else:
                    self._m_reader.skipCurrentElement()
                    #elementSkipped = True
            
            self._m_reader.readNext()
            
        return True
    
    def _parseSummary(self, route):
        '''
        @param route: GeoRoute
        @type route: GeoRoute
        @rtype: bool
        '''
        elementName = "Summary"
        if not self._m_reader.isStartElement() or self._m_reader.name() != elementName:
            raise TypeError("{0} is no startelement or not {1} tag".format(elementName, elementName))
        
        self._m_reader.readNext()
        
        while not (self._m_reader.tokenType() == QXmlStreamReader.EndElement \
                   and self._m_reader.name() == "Summary"):
            if self._m_reader.tokenType() == QXmlStreamReader.StartElement:
                if self._m_reader.name() == "Distance":
                    route.setDistance(self._m_reader.readElementText().toDouble()[0])
                elif self._m_reader.name() == "TrafficTime":
                    route.setTravelTime(self._m_reader.readElementText().toDouble()[0])
                else:
                    self._m_reader.skipCurrentElement()
            
            self._m_reader.readNext()
        return True
    
    def _parseCoordinates(self, coord):
        '''
        @param coord: GeoCoordinate
        @type coord: GeoCoordinate
        @rtype: bool
        '''
        currentElement = self._m_reader.name().toString()
        self._m_reader.readNext()
        
        while not (self._m_reader.tokenType() == QXmlStreamReader.EndElement 
                   and self._m_reader.name() == currentElement):
            if self._m_reader.tokenType() == QXmlStreamReader.StartElement:
                name = self._m_reader.name().toString()
                value = self._m_reader.readElementText()
                if name == "Latitude":
                    coord.setLatitude(value.toDouble()[0])
                elif name == "Longitude":
                    coord.setLongitude(value.toDouble()[0])
            
            self._m_reader.readNext()
        return True
    
    def _parseManeuver(self):
        '''
        @rtype: bool
        '''
        elementName = "Maneuver"
        if not self._m_reader.isStartElement() or self._m_reader.name() != elementName:
            raise TypeError("{0} is no startelement or not {1} tag".format(elementName, elementName))
        
        if not self._m_reader.attributes().hasAttribute("id"):
            self._m_reader.raiseError("The element \"Maneuver\" did not have the required attribute \"id\".")
            return False
        
        maneuverContainter = GeoManeuverContainer()
        maneuverContainter.id_ = self._m_reader.attributes().value("id").toString()
        
        self._m_reader.readNext()
        
        while not (self._m_reader.tokenType() == QXmlStreamReader.EndElement \
                   and self._m_reader.name() == "Maneuver"):
            if self._m_reader.tokenType() == QXmlStreamReader.StartElement:
                if self._m_reader.name() == "Position":
                    coordinates = GeoCoordinate()
                    if self._parseCoordinates(coordinates):
                        maneuverContainter.maneuver.setPosition(coordinates)
                elif self._m_reader.name() == "Instruction":
                    maneuverContainter.maneuver.setInstructionText(self._m_reader.readElementText())
                elif self._m_reader.name() == "ToLink":
                    maneuverContainter.toId = self._m_reader.readElementText()
                elif self._m_reader.name() == "TravelTime":
                    maneuverContainter.maneuver.setTimeToNextInstruction(self._m_reader.readElementText().toInt())
                elif self._m_reader.name() == "Length":
                    maneuverContainter.maneuver.setDistanceToNextInstruction(self._m_reader.readElementText().toDouble()[0])
                elif self._m_reader.name() == "Direction":
                    value = self._m_reader.readElementText()
                    if value == "forward":
                        maneuverContainter.maneuver.setDirection(GeoManeuver.DirectionForward)
                    elif value == "bearRight":
                        maneuverContainter.maneuver.setDirection(GeoManeuver.DirectionBearRight)
                    elif value == "lightRight":
                        maneuverContainter.maneuver.setDirection(GeoManeuver.DirectionLightRight)
                    elif value == "right":
                        maneuverContainter.maneuver.setDirection(GeoManeuver.DirectionRight)
                    elif value == "hardRight":
                        maneuverContainter.maneuver.setDirection(GeoManeuver.DirectionHardRight)
                    elif value == "uTurnRight":
                        maneuverContainter.maneuver.setDirection(GeoManeuver.DirectionUTurnRight)
                    elif value == "uTurnLeft":
                        maneuverContainter.maneuver.setDirection(GeoManeuver.DirectionUTurnLeft)
                    elif value == "hardLeft":
                        maneuverContainter.maneuver.setDirection(GeoManeuver.DirectionHardLeft)
                    elif value == "left":
                        maneuverContainter.maneuver.setDirection(GeoManeuver.DirectionLeft)
                    elif value == "lightLeft":
                        maneuverContainter.maneuver.setDirection(GeoManeuver.DirectionLightLeft)
                    elif value == "bearLeft":
                        maneuverContainter.maneuver.setDirection(GeoManeuver.DirectionBearLeft)
                    else:
                        maneuverContainter.maneuver.setDirection(GeoManeuver.NoDirection)
                else:
                    self._m_reader.skipCurrentElement()
                
            self._m_reader.readNext()
            
        self._maneuvers.append(maneuverContainter)
        return True
    
    def _parseLink(self):
        '''
        @rtype: bool
        '''
        elementName = "Link"
        if not self._m_reader.isStartElement() or self._m_reader.name() != elementName:
            raise TypeError("{0} is no startelement or not {1} tag".format(elementName, elementName))    
        self._m_reader.readNext()
        
        segmentContainer = GeoRouteSegmentContainer()
        
        while not (self._m_reader.tokenType() == QXmlStreamReader.EndElement \
                   and self._m_reader.name() == "Link"):
            if self._m_reader.tokenType() == QXmlStreamReader.StartElement:
                if self._m_reader.name() == "LinkId":
                    segmentContainer.id_ = self._m_reader.readElementText()
                elif self._m_reader.name() == "Shape":
                    elementName = self._m_reader.name().toString()
                    path = []
                    self._parseGeoPoints(self._m_reader.readElementText(), path, elementName)
                    segmentContainer.segment.setPath(path)
                elif self._m_reader.name() == "Length":
                    segmentContainer.segment.setDistance(self._m_reader.readElementText().toDouble()[0])
                elif self._m_reader.name() == "Maneuver":
                    segmentContainer.maneuverId = self._m_reader.readElementText()
                else:
                    self._m_reader.skipCurrentElement()
            self._m_reader.readNext()
        
        self._segments.append(segmentContainer)
        return True
    
    def _parseGeoPoints(self, strPoints, geoPoints, elementName):
        '''
        @param strPoints: The points as string
        @type strPoints: QString
        @param geoPoints: list of GeoCoordinate objects
        @type geoPoints: list
        @param elementName: QString from parser
        @type elementName: QString
        '''
        rawPoints = strPoints.split(' ')
        
        for i in range(len(rawPoints)):
            coords = rawPoints[i].split(',')
            
            if len(coords) != 2:
                self._m_reader.raiseError(QString("Each of the space separated values of \"%1\" is expected to be a comma separated pair of coordinates (value was \"%2\")").arg(elementName).arg(rawPoints[i]))
                return False
            
            
            latString = coords[0]
            lat = latString.toDouble()[0]
            
            lngString = coords[1]
            lng = lngString.toDouble()[0]
            
            geoPoint = GeoCoordinate(lat, lng)
            
            geoPoints.append(geoPoint)
        
        return True
    
    def _parseBoundingBox(self, bounds):
        '''
        @param bounds: GeoBoundingBox
        @type bounds: GeoBoundingBox
        @rtype: bool
        '''
        elementName = "BoundingBox"
        if not self._m_reader.isStartElement() or self._m_reader.name() != elementName:
            raise TypeError("{0} is no startelement or not {1} tag".format(elementName, elementName))
        
        tl = GeoCoordinate()
        br = GeoCoordinate()
        
        self._m_reader.readNext()
        
        while not (self._m_reader.tokenType() == QXmlStreamReader.EndElement \
                   and self._m_reader.name() == "BoundingBox"):
            if self._m_reader.tokenType() == QXmlStreamReader.StartElement:
                if self._m_reader.name() == "TopLeft":
                    coordinates = GeoCoordinate()
                    if self._parseCoordinates(coordinates):
                        tl = coordinates
                elif self._m_reader.name() == "BottomRight":
                    coordinates = GeoCoordinate()
                    if self._parseCoordinates(coordinates):
                        br = coordinates
                else:
                    self._m_reader.skipCurrentElement()
            
            self._m_reader.readNext()
    
        if tl.isValid() and br.isValid():
            bounds.setTopLeft(tl)
            bounds.setBottomRight(br)
            return True
    
        return False
