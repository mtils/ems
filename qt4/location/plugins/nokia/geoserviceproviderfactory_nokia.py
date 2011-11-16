'''
Created on 16.11.2011

@author: michi
'''
from ems.qt4.location.maps.geoserviceproviderfactory import GeoServiceProviderFactory

class GeoServiceProviderFactoryNokia(GeoServiceProviderFactory):
    
    defaultToken = '152022572f0e44e07489c35cd46fa246'
    defaultReferer = 'qtlocationapi'