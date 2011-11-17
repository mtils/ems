'''
Created on 17.11.2011

@author: michi
'''
from PyQt4.QtCore import QUrl
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkProxy

from ems.qt4.location.maps.geosearchmanager import GeoSearchManager
from ems.qt4.location.maps.geosearchmanagerengine import GeoSearchManagerEngine #@UnresolvedImport
from ems.qt4.location.plugins.nokia.geoserviceproviderfactory_nokia import GeoServiceProviderFactoryNokia #@UnresolvedImport


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
        self._m_networkManager = QNetworkAccessManager(self)
        self._m_host = "loc.desktop.maps.svc.ovi.com"
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
    
    def search(self, searchString, searchTypes):
        pass