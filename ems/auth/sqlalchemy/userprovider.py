'''
Created on 23.09.2011

@author: michi
'''
from ems.auth import AuthenticatedUser, AuthGroup, Permission
from ems.auth import UserProvider as BaseProvider
from ems.auth import UserNotFoundError

class SAOrmAuthGroup(AuthGroup):
    
    def __init__(self, sourceObject, adapter):
        self.__sourceObject = sourceObject
        self._adapter = adapter
    
    def _getSourceObject(self):
        return self.__sourceObject
    
    def _getId(self):
        propName = self._adapter.getPropertyName(UserProvider.GROUP_ID)
        return self.__sourceObject.__getattribute__(propName)
    
    def _getName(self):
        propName = self._adapter.getPropertyName(UserProvider.GROUP_NAME)
        return self.__sourceObject.__getattribute__(propName)

    def _getPermissions(self):
        propName = self._adapter.getPropertyName(UserProvider.GROUP_PERMISSIONS)
        codeProp = self._adapter.getPropertyName(UserProvider.PERMISSION_CODE)
        accessProp = self._adapter.getPropertyName(UserProvider.PERMISSION_ACCESS)
        titleProp = self._adapter.getPropertyName(UserProvider.PERMISSION_TITLE)

        perms = set()
        for ormPerm in self.__sourceObject.__getattribute__(propName):
            code = ormPerm.__getattribute__(codeProp)
            access = ormPerm.__getattribute__(accessProp)
            title = ''
            perms.add(Permission(code, title, access))
        return perms

class SAOrmAuthenticatedUser(AuthenticatedUser):
    
    def __init__(self, sourceObject, adapter):
        self.__sourceObject = sourceObject
        self._adapter = adapter
        self._mainGroup = None
    
    def _getSourceObject(self):
        return self.__sourceObject
    
    def _getId(self):
        propName = self._adapter.getPropertyName(UserProvider.USER_ID)
        return self.__sourceObject.__getattribute__(propName)
    
    def _getName(self):
        propName = self._adapter.getPropertyName(UserProvider.USER_NAME)
        return self.__sourceObject.__getattribute__(propName)
    
    def _getMainGroup(self):
        if self._mainGroup is None:
            propName = self._adapter.getPropertyName(UserProvider.USER_GROUP)
            group = self.__sourceObject.__getattribute__(propName)
            self._mainGroup = SAOrmAuthGroup(group, self._adapter)
        return self._mainGroup
    
    def _getGroups(self):
        return [self._getMainGroup()]
        


class UserProvider(BaseProvider):

    USER_ID = 'user_id'
    USER_NAME = 'user_name'
    USER_PASSWORD = 'user_password'
    USER_GROUP = 'user_group'

    GROUP_ID = 'group_id'
    GROUP_NAME = 'group_name'

    GROUP_PERMISSIONS = 'group_permissions'
    PERMISSION_CODE = 'permission'
    PERMISSION_ACCESS = 'access'
    PERMISSION_TITLE = 'title'

    def __init__(self, sessionGetter, userClass=None, propertyMap=None,
                  groupClass=None):
        self._sessionGetter = sessionGetter
        self._session = None
        self.userClass = userClass
        self.groupClass = groupClass
        self._propertyMap = {}

        if propertyMap is not None:
            self.propertyMap = propertyMap

    @property
    def session(self):
        if self._session is None:
            if callable(self._sessionGetter):
                self._session = self._sessionGetter()
            else:
                self._session = self._sessionGetter
        return self._session

    def getPropertyMap(self):
        return self._propertyMap

    def setPropertyMap(self, map):
        self._propertyMap = map

    propertyMap = property(getPropertyMap, setPropertyMap)

    def getPropertyName(self, name):
        if name not in self._propertyMap:
            raise KeyError("PropertyMap does not contain key {0}".format(name))
        return self._propertyMap[name]

    def findByCredentials(self, **kwargs):

        if 'username' not in kwargs:
            raise UserNotFoundError()

        filterByArgs = {self.getPropertyName(self.USER_NAME):kwargs['username']}

        user = self._getUserFromDB(filterByArgs)

        if not isinstance(user, self.userClass):
            raise UserNotFoundError()

        return SAOrmAuthenticatedUser(user, self)

    def _getUserFromDB(self, filterArgs):
        return self.session.query(self.userClass).filter_by(**filterArgs).first()

    def getUserName(self):
        return self.currentAuthenticatedObject.__getattribute__(self.accountPropertyName)

    def getGroupName(self):
        pass