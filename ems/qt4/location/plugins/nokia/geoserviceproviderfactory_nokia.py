'''
Created on 16.11.2011

@author: michi
'''
from ems.qt4.location.maps.geoserviceproviderfactory import GeoServiceProviderFactory
from ems.qt4.location.plugins.nokia.geosearchmanagerengine_nokia import GeoSearchManagerEngineNokia
from ems.qt4.location.plugins.nokia.geomappingmanagerengine_nokia import GeoMappingManagerEngineNokia
from ems.qt4.location.plugins.nokia.georoutingmanagerengine_nokia import GeoRoutingManagerEngineNokia

class GeoServiceProviderFactoryNokia(GeoServiceProviderFactory):
    
    defaultToken = '152022572f0e44e07489c35cd46fa246'
    defaultReferer = 'qtlocationapi'
    
    def providerName(self):
        return "nokia"
    
    def providerVersion(self):
        return 1
    
    def createSearchManagerEngine(self, parameters, error=0, errorString=""):
        return GeoSearchManagerEngineNokia(parameters, error, errorString)
    
    def createMappingManagerEngine(self, parameters, error=0, errorString=""):
        return GeoMappingManagerEngineNokia(parameters, error, errorString)
    
    def createRoutingManagerEngine(self, parameters, error=0, errorString=""):
        return GeoRoutingManagerEngineNokia(parameters, error, errorString)
    