'''
Created on 24.10.2011

@author: michi
'''
class GeoServiceProviderFactory(object):
    '''
    QGeoServiceProviderFactory

    Implementers must provide a unique combination of providerName() and
    providerVersion() per plugin.

    The other functions should be overridden if the plugin supports the
    associated set of functionality.
    
    '''
    def createSearchManagerEngine(self, parameters={}):
        '''
        Returns a new GeoSearchManagerEngine instance, initialized with 
        parameters, which implements as much of the places searching functionality
        as the service provider supports.
    
        If error is not 0 it should be set to GeoServiceProvider::NoError on
        success or an appropriate GeoServiceProvider::Error on failure.
    
        If errorString is not 0 it should be set to a string describing any
        error which occurred.
    
        The default implementation returns 0, which causes a
        GeoServiceProvider.NotSupportedError in QGeoServiceProvider.
        
        @param parameters: Params
        @type parameters: dict
        '''
        raise NotImplementedError('Please implement createSearchManagerEngine')
    
    def createMappingManagerEngine(self, parameters={}):
        '''
        Returns a new QGeoMappingManagerEngine instance, initialized with 
        parameters, which implements as much of the places searching functionality
        as the service provider supports.
    
        If error is not 0 it should be set to GeoServiceProvider.NoError on
        success or an appropriate GeoServiceProvider.Error on failure.
    
        If errorString is not 0 it should be set to a string describing any
        error which occurred.
    
        The default implementation returns 0, which causes a
        QGeoServiceProvider.NotSupportedError in GeoServiceProvider.
        
        @param parameters: Params
        @type parameters: dict
        '''
        raise NotImplementedError("Please implement createMappingManagerEngine")
    
    def createRoutingManagerEngine(self, parameters={}):
        '''
        Returns a new QGeoRoutingManagerEngine instance, initialized with 
        parameters, which implements as much of the places searching functionality
        as the service provider supports.
    
        If error is not 0 it should be set to GeoServiceProvider.NoError on
        success or an appropriate GeoServiceProvider.Error on failure.
    
        If errorString is not 0 it should be set to a string describing any
        error which occurred.
    
        The default implementation returns 0, which causes a
        GeoServiceProvider.NotSupportedError in QGeoServiceProvider.
        
        @param parameters: Params
        @type parameters: dict
        '''
        raise NotImplementedError("Please implement createRoutingManagerEngine")
    
    def providerName(self):
        '''
        Returns the provider name
        @return: Something
        @rtype: string
        '''
        raise NotImplementedError('Please implement providerName()')
    
    def providerVersion(self):
        '''
        Returns the version as int
        
        @return: The verion
        @rtype: int
        '''
        raise NotImplementedError('Please implement providerVersion()')