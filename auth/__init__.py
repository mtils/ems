'''
Created on 23.09.2011

@author: michi
'''
from ems.pluginemitter import PluginEmitter
from ems.thirdparty.singletonmixin import Singleton

class NotAuthenticatedError(Exception):
    pass

class AuthenticationFailureError(Exception):
    pass

class AlreadyAuthenticatedError(TypeError):
    pass

class AuthenticatedUser(object):
    def __init__(self):
        super(AuthenticatedUser, self).__init__()
    
    def _getSourceObject(self):
        clsName = self.__class__.__name__
        msg = "{0} has to implement _getSourceObject()".format(clsName)
        raise NotImplementedError(msg)
    
    @property
    def sourceObject(self):
        return self._getSourceObject()
    
    def _getId(self):
        clsName = self.__class__.__name__
        msg = "{0} has to implement _getId()".format(clsName)
        raise NotImplementedError(msg)
    
    @property
    def id(self):
        return self._getId()
    
    def _getName(self):
        clsName = self.__class__.__name__
        msg = "{0} has to implement _getName()".format(clsName)
        raise NotImplementedError(msg)
    
    @property
    def name(self):
        return self._getName()
    
    def _getMainGroup(self):
        clsName = self.__class__.__name__
        msg = "{0} has to implement _getMainGroup()".format(clsName)
        raise NotImplementedError(msg)
    
    @property
    def mainGroup(self):
        return self._getMainGroup()
    
    
    def _getGroups(self):
        clsName = self.__class__.__name__
        msg = "{0} has to implement _getGroups()".format(clsName)
        raise NotImplementedError(msg)
    
    @property
    def groups(self):
        return self._getGroups()
    
class AuthGroup(object):
    def __init__(self):
        super(AuthGroup, self).__init__()
    
    def _getSourceObject(self):
        clsName = self.__class__.__name__
        msg = "{0} has to implement _getSourceObject()".format(clsName)
        raise NotImplementedError(msg)
    
    @property
    def sourceObject(self):
        return self._getSourceObject()
    
    def _getId(self):
        clsName = self.__class__.__name__
        msg = "{0} has to implement _getId()".format(clsName)
        raise NotImplementedError(msg)
    
    @property
    def id(self):
        return self._getId()
    
    def _getName(self):
        clsName = self.__class__.__name__
        msg = "{0} has to implement _getName()".format(clsName)
        raise NotImplementedError(msg)
    
    @property
    def name(self):
        return self._getName()

class AuthenticationAdapter(object):
    def __init__(self):
        object.__init__(self)
    
    def checkCredentials(self, **kwargs):
        clsName = self.__class__.__name__
        msg = "{0} has to implement checkCredentials()".format(clsName)
        raise NotImplementedError(msg)
    
    def getAuthenticatedUser(self, **kwargs):
        clsName = self.__class__.__name__
        msg = "{0} has to implement getAuthenticatedObject()".format(clsName)
        raise NotImplementedError(msg)

class Authentication(Singleton):
    def __init__(self):
        super(Authentication, self).__init__()
        self._currentAdapter = None
        self.__isAuthenticated = False
        self.__authenticatedUser = None
        self.pluginEmitter = None
        
#        self.
    
    def isAuthenticated(self):
        return self.__isAuthenticated
    
    def __setIsAuthenticated(self, value):
        if self.__isAuthenticated != value:
            self.__isAuthenticated = value
            if isinstance(self.pluginEmitter, PluginEmitter):
                self.pluginEmitter.notify(self,
                                          "authenticationStateChanged",
                                          value)
            
    
    def getAdapter(self):
        return self._currentAdapter
    
    def login(self, **kwargs):
        if self.__isAuthenticated:
            raise AlreadyAuthenticatedError("Currently another User is authenticated. Logout first")
        res = self.checkCredentials(**kwargs)
        
        if not res:
            raise AuthenticationFailureError()
        
        
        adapter = self._getExistingAdapter()
        authUser = adapter.getAuthenticatedUser(**kwargs)
        
        if not isinstance(authUser, AuthenticatedUser):
            msg = "{0}.getAuthentocatedUser() has to return a AuthenticatedUser Object"
            raise TypeError(msg.format(adapter.__class__.__name__))
        
        self.__authenticatedUser = authUser
        self.__setIsAuthenticated(True)
        
    def logout(self):
        self.__setIsAuthenticated(False)
        self.__authenticatedUser = None
    
    def _getExistingAdapter(self):
        if not isinstance(self._currentAdapter, AuthenticationAdapter):
            raise TypeError("Assign an adapter prior to checkCredentials")
        return self._currentAdapter
    
    def setAdapter(self, adapter):
        if not isinstance(adapter, AuthenticationAdapter):
            raise TypeError("Param adapter has to be AuthenticationAdapter")
        self._currentAdapter = adapter
    
    adapter = property(getAdapter, setAdapter)
    
    def checkCredentials(self, **kwargs):
        return self._getExistingAdapter().checkCredentials(**kwargs)
    
    def getAuthenticatedUser(self):
        if not self.isAuthenticated():
            raise NotAuthenticatedError()
        return self.__authenticatedUser
    