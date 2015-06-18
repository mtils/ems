'''
Created on 23.09.2011

@author: michi
'''
from abc import ABCMeta, abstractmethod

from ems.pluginemitter import PluginEmitter
from ems.singletonmixin import Singleton
from ems.eventhook import EventHook
from ems.typehint import accepts

class NotAuthenticatedError(Exception):
    pass

class AuthenticationFailureError(Exception):
    pass

class AlreadyAuthenticatedError(TypeError):
    pass

class UserNotFoundError(AuthenticationFailureError):
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
    
    @property
    def password(self):
        return self.sourceObject.password
    
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

    def _getPermissions(self):
        clsName = self.__class__.__name__
        msg = "{0} has to implement getPermissions(permissionCode)".format(clsName)
        raise NotImplementedError(msg)

    @property
    def permissions(self):
        return self._getPermissions()

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

    def _getPermissions(self):
        clsName = self.__class__.__name__
        msg = "{0} has to implement getPermissions(permissionCode)".format(clsName)
        raise NotImplementedError(msg)

    @property
    def permissions(self):
        return self._getPermissions()

    def can(self, permissionCode):
        if self.id == 1:
            return True
        for perm in self.permissions:
            if perm.code == permissionCode:
                return True
        return False

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

class CredentialsBroker(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, user, **credentials):
        raise NotImplementedError('')

    def translate(self, **credentials):
        return credentials

class UserProvider(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def findByCredentials(self, **kwargs):
        raise NotImplementedError('')

class Permission(object):

    def __init__(self, code='', title='', access=1):
        super(Permission, self).__init__()
        self.code = code
        self.title = title
        self.access = access

    def __repr__(self):
        return "<{0} code:{1} access:{2}>".format(self.__class__.__name__,self.code, self.access)

class Authentication(object):


    @accepts(UserProvider, CredentialsBroker)
    def __init__(self, userProvider, credentialsBroker):

        super(Authentication, self).__init__()

        self.__userProvider = userProvider
        self.__credentialsBroker = credentialsBroker

        self._currentAdapter = None
        self.__isAuthenticated = False
        self.__authenticatedUser = None
        self.__permissions = []
        self.pluginEmitter = None

        self.authStateChanged = EventHook()
        self.authenticated = EventHook()
        self.loggedOut = EventHook()

    def isAuthenticated(self):
        return self.__isAuthenticated

    def __setIsAuthenticated(self, value):
        if self.__isAuthenticated != value:
            self.__isAuthenticated = value

            self.authStateChanged.fire(value)

            if isinstance(self.pluginEmitter, PluginEmitter):
                self.pluginEmitter.notify(self,
                                          "authenticationStateChanged",
                                          value)

    def login(self, **kwargs):

        if self.__isAuthenticated:
            raise AlreadyAuthenticatedError("Currently another User is authenticated. Logout first")

        credentials = self.__credentialsBroker.translate(**kwargs)

        try:
            user = self.__userProvider.findByCredentials(**credentials)
        except UserNotFoundError:
            raise AuthenticationFailureError()

        if not self.__credentialsBroker.validate(user, **credentials):
            raise AuthenticationFailureError()

        self.__authenticatedUser = user
        self.__setIsAuthenticated(True)

    def logout(self):
        self.__setIsAuthenticated(False)
        self.__authenticatedUser = None

    @property
    def user(self):
        return self.getAuthenticatedUser()

    def getAuthenticatedUser(self):
        if not self.isAuthenticated():
            self.login()
        return self.__authenticatedUser

    @property
    def permissions(self):
        return self.__permissions

    def registerPermission(self, permission):
        for perm in self.__permissions:
            if perm.code == permission.code:
                raise ValueError("A Permission with code {0} is already registered".format(permission.code))
        self.__permissions.append(permission)

    def unregisterPermission(self, permission):
        i = 0
        found = -1
        for perm in self.__permissions:
            if perm.code == permission.code:
                found = i
                break
            i += 1
        self.__permissions.pop(found)