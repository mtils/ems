'''
Created on 16.11.2011

@author: michi
'''
from PyQt4.QtCore import QString, QSize, QUrl, QDir
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkDiskCache, \
    QNetworkProxy, QNetworkRequest

from ems.qt4.location.maps.tiled.geotiledmappingmanagerengine import GeoTiledMappingManagerEngine #@UnusedImport
from ems.qt4.location.maps.graphicsgeomap import GraphicsGeoMap
from ems.qt4.location.plugins.nokia.geotiledmapdata_nokia import GeoTiledMapDataNokia #@UnresolvedImport
from ems.qt4.location.plugins.nokia.geomapreply_nokia import GeoMapReplyNokia #@UnresolvedImport
#from ems.qt4.location.plugins.nokia.

LARGE_TILE_DIMENSION = 256

class GeoMappingManagerEngineNokia(GeoTiledMappingManagerEngine):
    
    _m_networkmanager = QNetworkAccessManager
    
    _m_cache = QNetworkDiskCache
    
    _m_host = ""
    
    _m_token = ""
    
    _m_referer = ""
    
    def __init__(self, parameters, error=0, errorString=""):
        GeoTiledMappingManagerEngine.__init__(self, parameters)
        self._m_cache = None
        self._m_host = "maptile.maps.svc.ovi.com"
        from ems.qt4.location.plugins.nokia.geoserviceproviderfactory_nokia \
            import GeoServiceProviderFactoryNokia #@UnresolvedImport
        self._m_token = GeoServiceProviderFactoryNokia.defaultToken
        self._m_referer = GeoServiceProviderFactoryNokia.defaultReferer
        self._lastRequestString = ""
        
        self.setTileSize(QSize(256,256))
        self._setMinimumZoomLevel(0.0)
        self._setMaximumZoomLevel(18.0)
        
        types = []
        types.append(GraphicsGeoMap.StreetMap)
        types.append(GraphicsGeoMap.SatelliteMapDay)
        types.append(GraphicsGeoMap.TerrainMap)
        self._setSupportedMapTypes(types)
        
        modes = []
        modes.append(GraphicsGeoMap.OnlineMode)
        self._setSupportedConnectivityModes(modes)
        
        self._m_networkmanager = QNetworkAccessManager(self)
        
        if parameters.has_key("mapping.proxy"):
            proxy = parameters["mapping.proxy"]
            if len(proxy):
                proxyUrl = QUrl(proxy)
                if proxyUrl.isValid():
                    self._m_networkManager.setProxy(QNetworkProxy(QNetworkProxy.HttpProxy,
                        proxyUrl.host(),
                        proxyUrl.port(8080),
                        proxyUrl.userName(),
                        proxyUrl.password()))
        
        if parameters.has_key("mapping.host"):
            host = parameters["mapping.host"]
            if len(host):
                self._m_host = host
        
        if parameters.has_key("mapping.referer"):
            self._m_referer = parameters["mapping.referer"]
        
        if parameters.has_key("mapping.token"):
            self._m_token = parameters["mapping.token"]
        elif parameters.has_key('token'):
            self._m_token = parameters["token"]
        
        cacheDir = u""
        if parameters.has_key("mapping.cache.directory"):
            cacheDir = parameters["mapping.cache.directory"]
        else:
            cacheDir = QDir.temp().path() + "/maptiles"
        
             
        if len(cacheDir):
            self._m_cache = QNetworkDiskCache(self)
            dir_ = QDir()
            dir_.mkpath(cacheDir)
            dir_.setPath(cacheDir)
            
            self._m_cache.setCacheDirectory(dir_.path())
            
            if parameters.has_key('mapping.cache.size'):
                cacheSize = int(parameters['mapping.cache.size'])
                self._m_cache.setMaximumCacheSize(cacheSize)
            
            self._m_networkmanager.setCache(self._m_cache)
    
    def createMapData(self):
        '''
        @rtype: GeoTiledMapDataNokia
        '''
        data = GeoTiledMapDataNokia(self)
        if not data:
            return None
        
        data.setConnectivityMode(GraphicsGeoMap.OnlineMode)
        return data
    
    def getTileImage(self, request):
        '''
        @param request: The request for the tile image
        @type request: GeoTiledMapRequest
        '''
        # TODO add error detection for if request.connectivityMode() != QGraphicsGeoMap::OnlineMode
        rawRequest = self._getRequestString(request)
#        if rawRequest != self._lastRequestString:
#            print rawRequest
#        print rawRequest
        self._lastRequestString = rawRequest
        
        # The extra pair of parens disambiguates this from a function declaration
        netRequest = QNetworkRequest(QUrl(rawRequest))
        netRequest.setAttribute(QNetworkRequest.HttpPipeliningAllowedAttribute,
                                True)
        
        if isinstance(self._m_cache, QNetworkDiskCache):
            netRequest.setAttribute(QNetworkRequest.CacheLoadControlAttribute,
                                    QNetworkRequest.PreferCache)
        
        netReply = self._m_networkmanager.get(netRequest)
        
        mapReply = GeoMapReplyNokia(netReply, request)
        
        return mapReply
    
    def _getRequestString(self, request):
        '''
        @param request: GeoTiledMapRequest
        @type request: GeoTiledMapRequest
        '''
        maxDomains = 11; # TODO: hmmm....
        subdomainKey = (request.row() + request.column()) % maxDomains
        subdomain = 'a{0}'.format(subdomainKey) # a...k
        
        http = "http://"
        path = "/maptiler/maptile/newest/"
        dot = '.'
        slash = '/'
        
        requestParams = [http]
        #requestParams.append(subdomain)
        #requestParams.append(dot)
        requestParams.append(self._m_host)
        requestParams.append(path)
        requestParams.append(GeoMappingManagerEngineNokia._mapTypeToStr(request.mapType()))
        requestParams.append(slash)
        requestParams.append(unicode(int(request.zoomLevel())))
        requestParams.append(slash)
        requestParams.append(unicode(request.column()))
        requestParams.append(slash)
        requestParams.append(unicode(request.row()))
        requestParams.append(slash)
        requestParams.append(GeoMappingManagerEngineNokia._sizeToStr(self.tileSize()))
        
        requestParams.append('/png')
        
        if len(self._m_token):
            requestParams.append("?token={0}".format(self._m_token))
            
            if len(self._m_referer):
                requestParams.append("&referer={0}".format(self._m_referer))
        elif len(self._m_referer):
            requestParams.append('?referer={0}'.format(self._m_referer))
        
        return u"".join(requestParams)
    
    @staticmethod
    def _sizeToStr(size):
        '''
        @param size: The translateble size
        @type size: QSize
        '''
        s256 = "256"
        s128 = "128"
        
        if size.height() >= LARGE_TILE_DIMENSION or \
            size.width() >= LARGE_TILE_DIMENSION:
            return s256
        return s128
    
    @staticmethod
    def _mapTypeToStr(type_):
        '''
        @param type_: int
        @type type_: int
        '''
        if type_ == GraphicsGeoMap.StreetMap:
            return "normal.day"
        elif type_ in (GraphicsGeoMap.SatelliteMapDay,
                       GraphicsGeoMap.SatelliteMapNight):
            return "satellite.day"
        elif type_ == GraphicsGeoMap.TerrainMap:
            return "terrain.day"
        
        return "normal.day"
        
        
        
        