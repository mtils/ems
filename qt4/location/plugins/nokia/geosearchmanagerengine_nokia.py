'''
Created on 17.11.2011

@author: michi
'''
from PyQt4.QtCore import QUrl, QString, pyqtSlot, SIGNAL, QLocale
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkProxy, \
    QNetworkRequest

from ems.qt4.location.maps.geosearchmanager import GeoSearchManager
from ems.qt4.location.maps.geosearchmanagerengine import GeoSearchManagerEngine #@UnresolvedImport
from ems.qt4.location.geoboundingbox import GeoBoundingBox
from ems.qt4.location.maps.geosearchreply import GeoSearchReply
from ems.qt4.location.plugins.nokia.geosearchreply_nokia import GeoSearchReplyNokia #@UnresolvedImport
from ems.qt4.location.plugins.nokia.marclanguagecodes import marc_language_code_list
from ems.qt4.location.geoboundingarea import GeoBoundingArea
from ems.qt4.location.geoboundingcircle import GeoBoundingCircle

class GeoSearchManagerEngineNokia(GeoSearchManagerEngine):
    
    _m_networkManager = QNetworkAccessManager
    
    _m_host = ""
    
    _m_token = ""
    
    _m_referer = ""
    
    def __init__(self, parameters, error=0, errorString=""):
        '''
        @param parameters: params
        @type parameters: dict
        @param error: Error code (unused)
        @type error: int
        @param errorString: Error msg (unused)
        @type errorString: basestring
        '''
        GeoSearchManagerEngine.__init__(self, parameters)
        self._m_networkManager = QNetworkAccessManager(self)
        self._m_host = "loc.desktop.maps.svc.ovi.com"
        from ems.qt4.location.plugins.nokia.geoserviceproviderfactory_nokia \
            import GeoServiceProviderFactoryNokia #@UnresolvedImport
        self._m_token = GeoServiceProviderFactoryNokia.defaultToken
        self._m_referer = GeoServiceProviderFactoryNokia.defaultReferer
        
        if parameters.has_key("places.proxy"):
            proxy = parameters["places.proxy"]
            if len(proxy.isEmpty):
                proxyUrl = QUrl(proxy)
                if proxyUrl.isValid():
                    self._m_networkManager.setProxy(QNetworkProxy(QNetworkProxy.HttpProxy, 
                                                                  proxyUrl.host(),
                                                                  proxyUrl.port(8080),
                                                                  proxyUrl.userName(),
                                                                  proxyUrl.password()))
        
        if parameters.has_key("places.host"):
            host = parameters["places.host"]
            if len(host):
                self._m_host = host
        
        if parameters.has_key("places.referer"):
            self._m_referer = parameters["places.referer"]
        
    
        if parameters.has_key("places.token"):
            self._m_token = parameters["places.token"]
        
        elif parameters.has_key("token"):
            self._m_token = parameters["token"]
        
        self._setSupportsGeocoding(True)
        self._setSupportsReverseGeocoding(True)
    
        supportedSearchTypes = 0
        supportedSearchTypes |= GeoSearchManager.SearchGeocode
        self._setSupportedSearchTypes(supportedSearchTypes)
    
    def geocode(self, address, bounds):
        '''
        @param address: GeoAddress
        @type address: GeoAddress
        @param bounds: GeoBoundingBox
        @type bounds: GeoBoundingBox
        @rtype: GeoSearchReply
        '''
        
        requestStrings = ["http://"]
        requestStrings.append(self._m_host)
        requestStrings.append("/geocoder/gc/1.0?referer=")
        requestStrings.append(self._m_referer)
    
        if len(self._m_token):
            requestStrings.append("&token=")
            requestStrings.append(self._m_token)
    
        requestStrings.append("&lg=")
        requestStrings.append(self._languageToMarc(self.locale().language()))
    
        requestStrings.append("&country=")
        requestStrings.append(address.country())
        
        if len(address.state()):
            requestStrings.append("&state=")
            requestStrings.append(address.state())
    
        if len(address.city()):
            requestStrings.append("&city=")
            requestStrings.append(address.city())
    
        if len(address.postcode()):
            requestStrings.append("&zip=")
            requestStrings.append(address.postcode())
    
        if len(address.street()):
            requestStrings.append("&street=")
            requestStrings.append(address.street())
        
        return self.search(u"".join(requestStrings), bounds)
    
    def reverseGeoCode(self, coordinate, bounds):
        '''
        @param coordinate: GeoCoordinate
        @type coordinate: GeoCoordinate
        @param bounds: GeoBoundingBox
        @type bounds: GeoBoundingBox
        @rtype: GeoSearchReply
        '''
        
        requestStrings = ["http://"]
        requestStrings.append(self._m_host)
        requestStrings.append("/geocoder/rgc/1.0?referer=")
        requestStrings.append(self._m_referer)
        if len(self._m_token):
            requestStrings.append("&token=")
            requestStrings.append(self._m_token)
        requestStrings.append("&long=")
        requestStrings.append(self._trimDouble(coordinate.longitude()))
        requestStrings.append("&lat=")
        requestStrings.append(self._trimDouble(coordinate.latitude()))
    
        requestStrings.append("&lg=")
        requestStrings.append(self._languageToMarc(self._locale().language()))
    
        return self.search(u"".join(requestStrings), bounds)
    
    def search(self, searchString, searchTypesOrBounds, limit=-1, offset=0,
               bounds=None):
        
        #searchType passed
        if isinstance(searchTypesOrBounds, int):
            searchTypes = searchTypesOrBounds
            # NOTE this will eventually replaced by a much improved implementation
            # which will make use of the additionLandmarkManagers()
            if (searchTypes != GeoSearchManager.SearchAll) \
                    and ((searchTypes & self.supportedSearchTypes()) != searchTypes):
        
                reply = GeoSearchReply(GeoSearchReply.UnsupportedOptionError,
                                       "The selected search type is not supported by this service provider.",
                                       self)
                self.error.emit(reply, reply.error(), reply.errorString())
                return reply
            
            requestStrings = ["http://"]
            requestStrings.append(self._m_host)
            requestStrings.append("/geocoder/gc/1.0?referer=")
            requestStrings.append(self._m_referer)
        
            if len(self._m_token):
                requestStrings.append("&token=")
                requestStrings.append(self._m_token)
        
            requestStrings.append("&lg=")
            requestStrings.append(self._languageToMarc(self._locale().language()))
        
            requestStrings.append("&obloc=")
            requestStrings.append(unicode(searchString))
        
            if limit > 0:
                requestStrings.append("&total=")
                requestStrings.append(unicode(limit))
            
        
            if offset > 0:
                requestStrings.append("&offset=")
                requestStrings.append(unicode(offset))
            
            httpQueryStr ="".join(requestStrings)
            print httpQueryStr
            if bounds is None:
                bounds = GeoBoundingCircle()
            return self.search(httpQueryStr, bounds, limit, offset)
            
        #bounds passed
        elif isinstance(searchTypesOrBounds, GeoBoundingArea):
            bounds = searchTypesOrBounds
            networkReply = self._m_networkManager.get(QNetworkRequest(QUrl(searchString)))
            reply = GeoSearchReplyNokia(networkReply, limit, offset, bounds, self)
            
            reply.finished.connect(self._placesFinished)
            reply.errorOccured.connect(self._placesError)
                
            return reply
    
    @staticmethod
    def _trimDouble(degree, decimalDigits):
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
    def _placesFinished(self):
        reply = self.sender()

        if not reply:
            return
    
#        if self.receivers(SIGNAL('finished(PyQt_PyObject)')) == 0:
#            reply.deleteLater()
#            return;
        
    
        self.finished.emit(reply)
    
    def _placesError(self, error, errorString):
        '''
        @param error: Error code
        @type error: int
        @param errorString: Error msg (dev error)
        @type errorString: str
        '''
        reply = self.sender()
        
        if not reply:
            return
        
        if self.receivers(SIGNAL('error(PyQt_PyObject, int, PyQt_PyObject)')) == 0:
            reply.deleteLater()
            return
        
        self.error.emit(reply, error, errorString)
    
    def _languageToMarc(self, language):
        #offset = 3 * int(language)
        offset = int(language)
        if language == QLocale.C or offset + 3 > len(marc_language_code_list):
            return "eng"
        
        c = marc_language_code_list[offset]
        if c[0] == 0:
            return "eng"
        
        return "".join(c[:3])
        