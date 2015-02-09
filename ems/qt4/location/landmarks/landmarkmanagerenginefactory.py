'''
Created on 26.10.2011

@author: michi
'''

class LandmarkManagerEngineFactory(object):
    '''
    The QLandmarkManagerEngineFactory class provides the interface for
    plugins that implement QLandmarkManagerEngine functionality.

    This class provides a simple interface for the creation of
    landmark manager engine instances.  Each factory has a specific id
    associated with it, which forms the \c managerName parameter
    when creating \l QLandmarkManager objects.
    '''
    
    def supportedImplementationVersions(self):
        '''
        This function returns a list of versions of the engine which this factory can instantiate.
        
        @rtype: list
        '''
        return []
    
    def managerName(self):
        '''
        This function returns a unique string that identifies
        the engine provided by this factory.
        
        Typically this would be of the form "com.nokia.qt.landmarks.engines.sqlite", with
        the appropriate domain and engine name substituted.
        
        @rtype: str
        '''
        return ""
    
    def engine(self, parameters, error=0, errorString=""):
        '''
        This function is called by the QLandmarkManager implementation to
        create an instance of the engine provided by this factory.
    
        The \a parameters supplied can be ignored or interpreted as desired.
    
        If a supplied parameter results in an unfulfillable request, or some other error
        occurs, this function may return a null pointer, and the client developer will get an
        invalid QLandmarkManager in return.  Errors are stored in \a error and \a errorString.
        
        @param parameters: The parameters for the engine
        @type parameters: dict
        @param error: Unused, instead raises Exceptions
        @type error: int
        @param errorString: Unused, instead raises Exceptions
        @type errorString: str
        '''
        raise NotImplementedError('Please implement engine()')
    