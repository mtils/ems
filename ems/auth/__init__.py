'''
Created on 23.09.2011

@author: michi
'''
from abc import ABCMeta, abstractmethod

from ems.singletonmixin import Singleton
from ems.event.hook import EventHook
from ems.typehint import accepts
from ems.event.hook import EventProperty

class NotAuthenticatedError(Exception):
    pass

class AuthenticationFailureError(Exception):
    pass

class AlreadyAuthenticatedError(TypeError):
    pass

class UserNotFoundError(AuthenticationFailureError):
    pass

class User(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def authId(self):
        pass

    @abstractmethod
    def authPassword(self):
        """
        Return the hashed (stored) password
        :returns: str
        """
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

class CredentialsValidator(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, user, **credentials):
        raise NotImplementedError('')

class PlainPasswordValidator(CredentialsValidator):

    def __init__(self):
        self.passwordKey = 'password'

    def validate(self, user, **credentials):
        return (getattr(user, self.passwordKey) == credentials['password'])

class UserContainer(object):

    __metaclass__ = ABCMeta

    user = EventProperty()

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def set(self, user, persist=False):
        pass

    @abstractmethod
    def clear(self):
        pass

class RemeberableUserContainer(UserContainer):

    __metaclass__ = ABCMeta

    @abstractmethod
    def setAndRemember(self, user):
        pass

class TemporaryUserContainer(UserContainer):

    def get(self):
        return self.user

    def set(self, user, persist=False):
        self.user = user

    def clear(self):
        self.user = None

class UserProvider(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def findByCredentials(self, **kwargs):
        raise NotImplementedError('')

class AccessChecker(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def hasAccess(self, user, resource, context='access'):
        pass

class Permission(object):

    def __init__(self, code='', title='', access=1):
        super(Permission, self).__init__()
        self.code = code
        self.title = title
        self.access = access

    def __repr__(self):
        return "<{0} code:{1} access:{2}>".format(self.__class__.__name__,self.code, self.access)

class Authentication(object):


    @accepts(UserProvider, CredentialsValidator, UserContainer)
    def __init__(self, userProvider, credentialsValidator, userContainer):

        super(Authentication, self).__init__()

        self.__userProvider = userProvider
        self.__credentialsValidator = credentialsValidator
        self._userContainer = userContainer

        self._currentAdapter = None
        self.__isAuthenticated = False
        self.__permissions = []

        self.authStateChanged = EventHook()
        self.authenticated = EventHook()
        self.loggedIn = EventHook()
        self.loggedOut = EventHook()

        UserContainer.user.listenOn(userContainer, self._onContainerChanges)

    def isAuthenticated(self):
        return self.__isAuthenticated

    def __setIsAuthenticated(self, value):
        if self.__isAuthenticated != value:
            self.__isAuthenticated = value

            self.authStateChanged.fire(value)

    def login(self, **credentials):

        if self.__isAuthenticated:
            raise AlreadyAuthenticatedError("Currently another User is authenticated. Logout first")

        user = self.__userProvider.findByCredentials(**credentials)

        if not self.__credentialsValidator.validate(user, **credentials):
            raise AuthenticationFailureError()

        self._userContainer.set(user, True)

    def logout(self):
        self._userContainer.clear()

    @property
    def user(self):
        user = self._userContainer.get()
        if not user:
            raise NotAuthenticatedError()
        return user

    @user.setter
    def user(self, user):
        self._userContainer.set(user, False)

    @property
    def permissions(self):
        return self.__permissions

    def _onContainerChanges(self, user):

        if user is None:
            self.loggedOut.fire()
            return

        self.loggedIn.fire(user)

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