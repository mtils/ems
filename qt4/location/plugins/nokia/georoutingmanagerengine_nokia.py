'''
Created on 17.11.2011

@author: michi
'''
from PyQt4.QtCore import QUrl, QDateTime, QString, pyqtSlot, SIGNAL
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkProxy, \
    QNetworkRequest

from ems.qt4.location.maps.georoutingmanagerengine import GeoRoutingManagerEngine #@UnresolvedImport
from ems.qt4.location.maps.georouterequest import GeoRouteRequest #@UnresolvedImport
from ems.qt4.location.maps.georoutereply import GeoRouteReply #@UnresolvedImport

from ems.qt4.location.plugins.nokia.georoutereply_nokia import GeoRouteReplyNokia #@UnresolvedImport

class GeoRoutingManagerEngineNokia(GeoRoutingManagerEngine):
    
    _m_host = ""
    
    _m_token = ""
    
    _m_referer = ""
    
    _m_networkManager = QNetworkAccessManager
    
    def __init__(self, parameters, error=0, errorString=""):
        GeoRoutingManagerEngine.__init__(self, parameters)
        
        self._m_host = "prd.lbsp.navteq.com"
        from ems.qt4.location.plugins.nokia.geoserviceproviderfactory_nokia \
            import GeoServiceProviderFactoryNokia #@UnresolvedImport
        
        self._m_token = GeoServiceProviderFactoryNokia.defaultToken
        self._m_referer = GeoServiceProviderFactoryNokia.defaultReferer
        
        self._m_networkManager = QNetworkAccessManager(self)
        
        if parameters.has_key("routing.proxy"):
            proxy = parameters["routing.proxy"]
            if len(proxy):
                proxyUrl = QUrl(proxy)
                if proxyUrl.isValid():
                    self._m_networkManager.setProxy(QNetworkProxy(QNetworkProxy.HttpProxy, 
                                                                  proxyUrl.host(),
                                                                  proxyUrl.port(8080),
                                                                  proxyUrl.userName(),
                                                                  proxyUrl.password()))
        
        if parameters.has_key("routing.host"):
            host = parameters["routing.host"]
            if len(host):
                self._m_host = host
    
        if parameters.has_key("routing.referer"):
            self._m_referer = parameters["routing.referer"]
        
    
        if parameters.has_key("routing.token"):
            self._m_token = parameters["routing.token"]
        
        elif parameters.has_key("token"):
            self._m_token = parameters["token"]
        
        self._setSupportsRouteUpdates(True)
        self._setSupportsAlternativeRoutes(True)
        self._setSupportsExcludeAreas(True)
        
        featureTypes = 0
        featureTypes |= GeoRouteRequest.TollFeature
        featureTypes |= GeoRouteRequest.HighwayFeature
        featureTypes |= GeoRouteRequest.FerryFeature
        featureTypes |= GeoRouteRequest.TunnelFeature
        featureTypes |= GeoRouteRequest.DirtRoadFeature
        self._setSupportedFeatureTypes(featureTypes)
        
        featureWeights = 0
        featureWeights |= GeoRouteRequest.AvoidFeatureWeight
        self._setSupportedFeatureWeights(featureWeights)
        
        maneuverDetails = 0
        maneuverDetails |= GeoRouteRequest.BasicManeuvers
        self._setSupportedManeuverDetails(maneuverDetails)
        
        optimizations = 0
        optimizations |= GeoRouteRequest.ShortestRoute
        optimizations |= GeoRouteRequest.FastestRoute
        optimizations |= GeoRouteRequest.MostEconomicRoute
        self._setSupportedRouteOptimizations(optimizations)
        
        travelModes = 0
        travelModes |= GeoRouteRequest.CarTravel
        travelModes |= GeoRouteRequest.PedestrianTravel
        travelModes |= GeoRouteRequest.PublicTransitTravel
        self._setSupportedTravelModes(travelModes)
        
        segmentDetails = 0
        segmentDetails |= GeoRouteRequest.BasicSegmentData
        self._setSupportedSegmentDetails(segmentDetails)
    
    def calculateRoute(self, request):
        '''
        @param request: GeoRouteRequest
        @type request: GeoRouteRequest
        @rtype: GeoRouteReply
        '''
        
        reqString = self._calculateRouteRequestString(request)
        print reqString
        
        if not len(reqString):
            reply = GeoRouteReply(GeoRouteReply.UnsupportedOptionError,
                                  "The given route request options are not supported by this service provider.",
                                  self)
            self.error.emit(reply.error(), reply.errorString())
            return reply
        
        
        networkReply = self._m_networkManager.get(QNetworkRequest(QUrl(reqString)));
        reply = GeoRouteReplyNokia(request, networkReply, self)
        
        reply.finished.connect(self._routeFinished)
        reply.errorOccured.connect(self._routeError)
        
        return reply
    
    def _updateRoute(self, route, position):
        '''
        @param route: GeoRoute
        @type route: GeoRoute
        @param position: GeoCoordinate
        @type position: GeoCoordinate
        @rtype: GeoRouteReply
        '''
        reqString = self._updateRouteRequestString(route, position)
        
        if not len(reqString):
            reply = GeoRouteReply(GeoRouteReply.UnsupportedOptionError,
                                  "The given route request options are not supported by this service provider.",
                                  self)
            self.error.emit(reply, reply.error(), reply.errorString())
            return reply
        
        networkReply = self._m_networkManager.get(QNetworkRequest(QUrl(reqString)))
        updateRequest = GeoRouteRequest(route.request())
        updateRequest.setTravelModes(route.travelMode())
        reply = GeoRouteReplyNokia(updateRequest, networkReply, self)
        
        reply.finished.connect(self._routeFinished)
        reply.error.connect(self._routeError)
        
        return reply
    
    def _checkEngineSupport(self, request, travelModes):
        '''
        @param request: GeoRouteRequest
        @type request: GeoRouteRequest
        @param travelModes: int
        @type travelModes: int
        '''
        featureTypeList = request.featureTypes()
        featureTypeFlag = GeoRouteRequest.NoFeature
        featureWeightFlag = GeoRouteRequest.NeutralFeatureWeight
        
        for i in range(len(featureTypeList)):
            featureTypeFlag |= featureTypeList[i]
            featureWeightFlag |= request.featureWeight(featureTypeList[i])
        
    
        if (featureTypeFlag & self.supportedFeatureTypes()) != featureTypeFlag:
            return False
    
        if (featureWeightFlag & self.supportedFeatureWeights()) != featureWeightFlag:
            return False
    
    
        if (request.maneuverDetail() & self._supportedManeuverDetails) != request.maneuverDetail():
            return False
    
        if (request.segmentDetail() & self.supportedSegmentDetails()) != request.segmentDetail():
            return False
    
        if (request.routeOptimization() & self.supportedRouteOptimizations()) != request.routeOptimization():
            return False
    
        if (travelModes & self.supportedTravelModes()) != travelModes:
            return False
    
        return True
    
    def _calculateRouteRequestString(self, request):
        '''
        @param request: GeoRouteRequest
        @type request: GeoRouteRequest
        @rtype: basestring
        '''
        supported = self._checkEngineSupport(request, request.travelModes())
        
        if (request.numberAlternativeRoutes() != 0) and not self.supportsAlternativeRoutes():
            supported = False
    
        if not supported:
            return ""
        
        requestStrings = ["http://"]
        requestStrings.append(self._m_host)
        requestStrings.append("/routing/6.2/calculateroute.xml?referer=")
        requestStrings.append(self._m_referer)
    
        if len(self._m_token):
            requestStrings.append("&token=")
            requestStrings.append(self._m_token)
    
        numWaypoints = len(request.waypoints())
        if numWaypoints < 2:
            return ""
        
    
        for i in range(numWaypoints):
            requestStrings.append("&waypoint")
            requestStrings.append(unicode(i))
            requestStrings.append("=")
            requestStrings.append(GeoRoutingManagerEngineNokia._trimDouble(request.waypoints()[i].latitude()))
            requestStrings.append(",")
            requestStrings.append(GeoRoutingManagerEngineNokia._trimDouble(request.waypoints()[i].longitude()))
        
    
        requestStrings.append(self._modesRequestString(request, request.travelModes()))
    
        requestStrings.append("&alternatives=")
        requestStrings.append(unicode(request.numberAlternativeRoutes()))
    
        requestStrings.append(self._routeRequestString(request))
    
        return "".join(requestStrings)
    
    def _updateRequestString(self, route, position):
        '''
        @param route: GeoRoute
        @type route: GeoRoute
        @param position: GeoCoordinate
        @type position: GeoCoordinate
        @rtype: basestring
        '''
        
        if not self._checkEngineSupport(route.request(), route.travelMode()):
            return ""

        requestStrings = ["http://"]
        requestStrings.append(self._m_host)
        requestStrings.append("/routing/6.2/getroute.xml")
    
        requestStrings.append("?routeid=")
        requestStrings.append(route.routeId())
    
        requestStrings.append("&pos=")
        requestStrings.append(unicode(position.latitude()))
        requestStrings.append(",")
        requestStrings.append(unicode(position.longitude()))
    
        requestStrings.append(self._modesRequestString(route.request(), route.travelMode()))
    
        requestStrings.append(self._routeRequestString(route.request()))
    
        return u"".join(requestStrings)
    
    def _modesRequestString(self, request, travelModes):
        '''
        @param request: GeoRouteRequest
        @type request: GeoRouteRequest
        @param travelModes: int
        @type travelModes: int
        '''
        
        requestStrings = []

        optimization = request.routeOptimization()
    
        types = []
        if optimization & GeoRouteRequest.ShortestRoute:
            types.append("shortest")
        if optimization & GeoRouteRequest.FastestRoute:
            types.append("fastestNow")
        if optimization & GeoRouteRequest.MostEconomicRoute:
            types.append("economic")
        if optimization & GeoRouteRequest.MostScenicRoute:
            types.append("scenic")
    
        modes = []
        if travelModes & GeoRouteRequest.CarTravel:
            modes.append("car")
        if travelModes & GeoRouteRequest.PedestrianTravel:
            modes.append("pedestrian")
        if travelModes & GeoRouteRequest.PublicTransitTravel:
            modes.append("publicTransport")
        
        featureStrings = []
        featureTypes = request.featureTypes()
        for featureType in featureTypes:
            weight = request.featureWeight(featureType)
    
            if weight == GeoRouteRequest.NeutralFeatureWeight:
                continue
    
            weightString = ""
            if weight == GeoRouteRequest.PreferFeatureWeight:
                weightString = "1"
            elif weight == GeoRouteRequest.AvoidFeatureWeight:
                weightString = "-1"
            elif weight == GeoRouteRequest.DisallowFeatureWeight:
                weightString = "-3"
                
            
    
            if not len(weightString):
                continue
    
            if featureType == GeoRouteRequest.TollFeature:
                featureStrings.append("tollroad:" + weightString)
            elif featureType == GeoRouteRequest.HighwayFeature:
                featureStrings.append("motorway:" + weightString)
            elif featureType == GeoRouteRequest.FerryFeature:
                featureStrings.append("boatFerry:" + weightString)
                featureStrings.append("railFerry:" + weightString)
            elif featureType == GeoRouteRequest.TunnelFeature:
                featureStrings.append("tunnel:" + weightString)
            elif featureType == GeoRouteRequest.DirtRoadFeature:
                featureStrings.append("dirtRoad:" + weightString)
        
        i = 0
        for type_ in types:
            requestStrings.append("&mode")
            requestStrings.append(unicode(i))
            requestStrings.append("=")
            requestStrings.append(type_)
            requestStrings.append(";")
            requestStrings.append(",".join(modes))
            if len(featureStrings):
                requestStrings.append(";")
                requestStrings.append(",".join(featureStrings))
            i += 1
            
        return "".join(requestStrings)
    
    def _routeRequestString(self, request):
        '''
        @param request: GeoRouteRequest
        @type request: GeoRouteRequest
        @rtype: basestring
        '''
        requestStrings = []

        numAreas = len(request.excludeAreas())
        if numAreas > 0:
            requestStrings.append("&avoidareas")
            for i in range(numAreas):
                if i == 0:
                    requestStrings.append("=")
                else:
                    requestStrings.append(";")
                box = request.excludeAreas()[i]
                requestStrings.append(GeoRoutingManagerEngineNokia._trimDouble(box.topLeft().latitude()))
                requestStrings.append(",")
                requestStrings.append(GeoRoutingManagerEngineNokia._trimDouble(box.topLeft().longitude()))
                requestStrings.append(",")
                requestStrings.append(GeoRoutingManagerEngineNokia._trimDouble(box.bottomRight().latitude()))
                requestStrings.append(",")
                requestStrings.append(GeoRoutingManagerEngineNokia._trimDouble(box.bottomRight().longitude()))
        
        legAttributes = []
        if request.segmentDetail() & GeoRouteRequest.BasicSegmentData:
            requestStrings.append("&linkattributes=sh,le") #shape,length
            legAttributes.append("links")
        
    
        if request.maneuverDetail() & GeoRouteRequest.BasicManeuvers:
            legAttributes.append("maneuvers");
            requestStrings.append("&maneuverattributes=po,tt,le,di") #position,traveltime,length,direction
            if not (request.segmentDetail() & GeoRouteRequest.NoSegmentData):
                requestStrings.append(",li") #link
        
        requestStrings.append("&routeattributes=sm,sh,bb,lg") #summary,shape,boundingBox,legs
        if len(legAttributes) > 0:
            requestStrings.append("&legattributes=")
            requestStrings.append(",".join(legAttributes))
        
    
        requestStrings.append("&departure=")
        dt = QDateTime.currentDateTime().toUTC().toString("yyyy-MM-ddThh:mm:ssZ")
        requestStrings.append(unicode(dt))
    
        requestStrings.append("&instructionformat=text")
    
        requestStrings.append("&language=")
        requestStrings.append(unicode(self.locale().name()))
    
        return "".join(requestStrings)
    
    @staticmethod
    def _trimDouble(degree, decimalDigits=10):
        '''
        @param degree: float
        @type degree: float
        @param decimalDigits: int
        @type decimalDigits: int
        '''
        sDegree = QString.number(degree, 'g', decimalDigits)

        index = sDegree.indexOf('.')
    
        if index == -1:
            return unicode(sDegree)
        else:
            return unicode(QString.number(degree, 'g', decimalDigits + index))
    
    @pyqtSlot()
    def _routeFinished(self):
        reply = self.sender()
        
        if not reply:
            return
        
        if self.receivers(SIGNAL("finished(PyQt_PyObject)")) == 0:
            reply.deleteLater()
            return
        
        self.finished.emit(reply)
    
    def _routeError(self, error, errorString):
        '''
        @param error: Error Code
        @type error: int
        @param errorString: Error Msg (Dev msg)
        @type errorString: str
        '''
        reply = self.sender()
        
        if not reply:
            return
        
        if self.receivers(SIGNAL("finished(PyQt_PyObject, PyQt_PyObject)")) == 0:
            reply.deleteLater()
            return
        
        self.error.emit(error, errorString)