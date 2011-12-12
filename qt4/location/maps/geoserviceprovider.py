'''
Created on 21.10.2011

@author: michi
'''
from geosearchmanager import GeoSearchManager #@UnresolvedImport
from geomappingmanager import GeoMappingManager #@UnresolvedImport
from georoutingmanager import GeoRoutingManager #@UnresolvedImport

class NotSupportedError(Exception):
    def __init__(self, *args, **kwargs):
        self.code = GeoServiceProvider.NotSupportedError
        Exception.__init__(self, *args, **kwargs)

class UnknownParameterError(Exception):
    pass

class MissingRequiredParameterError(Exception):
    pass

class GeoServiceProvider(object):
    '''
    The QGeoServiceProvider class aggregates access to services which provide
    geographical information.


    The Maps and Navigation API allows people to access various kinds of
    geographical information, including functionality to perform geocoding,
    routing and the display of maps.  The QGeoServiceProvider aggregates the
    access to a set of these services that are provided by a single vendor.

    It is possible to mix and match service providers for the various domains,
    so that a geocoding manager from one service provider can be used with
    a geographic routing manager from another service provider.

    This is not recommended unless the client is able to verify that the
    data provided by the different services are compatible, as differences
    in the underlying data sets could cause serious incongruences between
    the services.

    Subclasses of QGeoServiceProvider guarantee that the different services
    that they provide are interoperable.

    At this point only the Nokia Services plugin is pacakged with Qt Mobility,
    which is accessible using the provider name "nokia".
    '''
    
    'Error Enum'
    NoError = 0
    'No error has occurred'
    
    NotSupportedError = 1
    'The plugin does not support this functionality.'
    
    UnknownParameterError = 2
    'The plugin did not recognise one of the parameters it was given.'
    
    MissingRequiredParameterError = 3
    'The plugin did not find one of the parameters it was expecting.'
    
    
    _plugins = {}
    
    _alreadyDiscovered = False
    
    
    
    @staticmethod
    def availableServiceProviders():
        '''
        Returns a list of names of the available service providers, for use with
        the QGeoServiceProvider constructors.
        
        @return list
        '''
        return GeoServiceProvider._plugins.keys()
    
    def __init__(self, providerName, parameters={}):
        '''
        Constructs a QGeoServiceProvider whose backend has the name 
        providerName, using the provided parameters.
    
        If multiple plugins have the same providerName, the plugin with the
        highest reported providerVersion() will be used.
    
        If no plugin matching providerName was able to be loaded then error()
        and errorString() will provide details about why this is the case.
        
        @param providerName: The name of the provider
        @type providerName: str
        @param parameters: The params
        @type parameters: dict
        '''
        self.__factory = None
        self.__loadPlugin(providerName, parameters)
        self.__parameterMap = parameters
        
        self.__searchManager = None
        self.__searchError = self.NoError
        self.__searchErrorString = ""
        
        self.__mappingError = self.NoError
        self.__mappingManager = None
        self.__mappingErrorString = ""
        
        self.__routingManager = None
        self.__routingError = self.NoError
        self.__routingErrorString = ""
        
        
        self.__error = self.NoError
        self.__errorString = ""
        
        
    
    def searchManager(self):
        '''
        Returns the QGeoSearchManager made available by the service
        provider.
    
        This function will return 0 if the service provider does not provide
        any geocoding services.
    
        This function will attempt to construct a QGeoSearchManager instance
        when it is called for the first time.  If the attempt is successful the
        QGeoSearchManager will be cached, otherwise each call of this function
        will attempt to construct a QGeoSearchManager instance until the
        construction is successful.
    
        After this function has been called, error() and errorString() will
        report any errors which occurred during the construction of the
        QGeoSearchManager.
        
        @return: GeoSearchManager
        '''
        if not self.__factory or (self.__searchError != GeoServiceProvider.NoError):
            return None
        
        if not self.__searchManager:
            engine = self.__factory.createSearchManagerEngine(self.__parameterMap,
                                                              self.__searchError,
                                                              self.__searchErrorString)
            if engine:
                engine._setManagerName(self.__factory.providerName())
                engine._setManagerVersion(self.__factory.providerVersion())
                self.__searchManager = GeoSearchManager(engine)
            else:
                self.__searchError = self.NotSupportedError
                self.__searchErrorString = "The service provider does not support searchManager()"
            
            if self.__searchError != self.NoError:
                if self.__searchManager:
                    del self.__searchManager
                self.__searchManager = None
                self.__error = self.__searchError
                self.__errorString = self.__searchErrorString
        return self.__searchManager
    
    def mappingManager(self):
        '''
        Returns the QGeoMappingManager made available by the service provider.

        This function will return 0 if the service provider does not provide
        any mapping services.
    
        This function will attempt to construct a QGeoMappingManager instance
        when it is called for the first time.  If the attempt is successful the
        QGeoMappingManager will be cached, otherwise each call of this function
        will attempt to construct a QGeoMappingManager instance until the
        construction is successful.
    
        After this function has been called, error() and errorString() will
        report any errors which occurred during the construction of the
        QGeoMappingManager.
        
        @return: GeoMappingManager
        '''
        
        if not self.__factory or (self.__mappingError != GeoServiceProvider.NoError):
            return 0

        if not self.__mappingManager:
            engine = self.__factory.createMappingManagerEngine(self.__parameterMap,
                                               self.__mappingError,
                                               self.__mappingErrorString)
            
            if engine:
                engine._setManagerName(self.__factory.providerName())
                engine._setManagerVersion(self.__factory.providerVersion())
                self.__mappingManager = GeoMappingManager(engine)
            else:
                self.__mappingError = GeoServiceProvider.NotSupportedError;
                self.__mappingErrorString = "The service provider does not support mappingManager()."
            
    
            if self.__mappingError != GeoServiceProvider.NoError:
                if self.__mappingManager:
                    del self.__mappingManager
                self.__mappingManager = None
                self.__error = self.__mappingError
                self.__errorString = self.__mappingErrorString;
            
    
        return self.__mappingManager
    
    def routingManager(self):
        '''
        Returns the QGeoRoutingManager made available by the service provider.

        This function will return 0 if the service provider does not provide
        any geographic routing services.
    
        This function will attempt to construct a QGeoRoutingManager instance
        when it is called for the first time.  If the attempt is successful the
        QGeoRoutingManager will be cached, otherwise each call of this function
        will attempt to construct a QGeoRoutingManager instance until the
        construction is successful.
    
        After this function has been called, error() and errorString() will
        report any errors which occurred during the construction of the
        QGeoRoutingManager.
        
        @return GeoRoutingManager
        '''
        
        if not self.__factory or (self.__routingError != GeoServiceProvider.NoError):
            return None;

        if not self.__routingManager:
            engine = self.__factory.createRoutingManagerEngine(self.__parameterMap,
                                               self.__routingError,
                                               self.__routingErrorString)
    
            if engine:
                engine._setManagerName(self.__factory.providerName())
                engine._setManagerVersion(self.__factory.providerVersion())
                self.__routingManager = GeoRoutingManager(engine)
            else:
                self.__routingError = GeoServiceProvider.NotSupportedError
                self.__routingErrorString = "The service provider does not support routingManager()."
    
            if self.__routingError != GeoServiceProvider.NoError:
                if (self.__routingManager):
                    del self.__routingManager
                self.__routingManager = None
                self.__error = self.__routingError
                self.__errorString = self.__routingErrorString
    
        return self.__routingManager;
    
    def error(self):
        '''
        Returns an error code describing the error which occurred during the
        last operation that was performed by this class.
        
        @return: int
        '''
        return self.__error
    
    def errorString(self):
        '''
        Returns a string describing the error which occurred during the
        last operation that was performed by this class.
        
        @return: string
        '''
        return self.__errorString
    
    def __del__(self):
        del self.__searchManager
        del self.__mappingManager
        del self.__routingManager
    
    def __loadPlugin(self, providerName, parameters={}):
        '''
        Loads a plugin
        
        @param providerName: The name of the provider
        @type providerName: string
        @param parameters: Params for the plugin
        @type parameters: dict
        '''
        
        if not providerName in self.plugins().keys():
            self.__error = GeoServiceProvider.NotSupportedError
            self.__errorString = "The geoservices provider %1 is not supported.".format(providerName)
            self.__factory = None
            return
        
        self.__factory = None
        self.__error = GeoServiceProvider.NoError
        self.__errorString = ""
        
        canditates = GeoServiceProvider._plugins
        
        versionFound = -1
        
        for candidateName in canditates:
            candidate = GeoServiceProvider._plugins[candidateName]
            if (candidate.providerName() == providerName) and\
               (candidate.providerVersion() > versionFound):
                self.__factory = candidate
        
    @staticmethod
    def plugins(reload_=False):
        if reload_:
            GeoServiceProvider._alreadyDiscovered = False
        
        if not GeoServiceProvider._alreadyDiscovered:
            staticPlugins = GeoServiceProvider.loadStaticPlugins()
            #dynamicPlugins = GeoServiceProvider.loadDynamicPlugins()
            #staticPlugins.update(dynamicPlugins)
            GeoServiceProvider._alreadyDiscovered = True
        
        return GeoServiceProvider._plugins
    
    @staticmethod
    def loadStaticPlugins():
        plugins = {}
    
    @staticmethod
    def addPlugin(plugin):
        GeoServiceProvider._plugins[plugin.providerName()] = plugin
        
            
        
        

if __name__ == '__main__':
    print GeoServiceProvider.availableServiceProviders()
    print NotSupportedError
    print GeoServiceProvider.NotSupportedError