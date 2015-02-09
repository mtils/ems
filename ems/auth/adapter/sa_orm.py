'''
Created on 23.09.2011

@author: michi
'''
from ems.auth import AuthenticationAdapter, AuthenticatedUser,AuthGroup, Permission

class SAOrmAuthGroup(AuthGroup):
    
    def __init__(self, sourceObject, adapter):
        self.__sourceObject = sourceObject
        self._adapter = adapter
    
    def _getSourceObject(self):
        return self.__sourceObject
    
    def _getId(self):
        propName = self._adapter.getPropertyName(SAOrmAuthAdapter.GROUP_ID)
        return self.__sourceObject.__getattribute__(propName)
    
    def _getName(self):
        propName = self._adapter.getPropertyName(SAOrmAuthAdapter.GROUP_NAME)
        return self.__sourceObject.__getattribute__(propName)

    def _getPermissions(self):
        propName = self._adapter.getPropertyName(SAOrmAuthAdapter.GROUP_PERMISSIONS)
        codeProp = self._adapter.getPropertyName(SAOrmAuthAdapter.PERMISSION_CODE)
        accessProp = self._adapter.getPropertyName(SAOrmAuthAdapter.PERMISSION_ACCESS)
        titleProp = self._adapter.getPropertyName(SAOrmAuthAdapter.PERMISSION_TITLE)

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
        propName = self._adapter.getPropertyName(SAOrmAuthAdapter.USER_ID)
        return self.__sourceObject.__getattribute__(propName)
    
    def _getName(self):
        propName = self._adapter.getPropertyName(SAOrmAuthAdapter.USER_NAME)
        return self.__sourceObject.__getattribute__(propName)
    
    def _getMainGroup(self):
        if self._mainGroup is None:
            propName = self._adapter.getPropertyName(SAOrmAuthAdapter.USER_GROUP)
            group = self.__sourceObject.__getattribute__(propName)
            self._mainGroup = SAOrmAuthGroup(group, self._adapter)
        return self._mainGroup
    
    def _getGroups(self):
        return [self._getMainGroup()]
        


class SAOrmAuthAdapter(AuthenticationAdapter):
    
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
        if not self._propertyMap.has_key(name):
            raise KeyError("PropertyMap does not contain key {0}".format(name))
        return self._propertyMap[name]
        
    def __getUserFromDB(self, **kwargs):
        if kwargs.has_key('skipPasswordCheck') and kwargs['skipPasswordCheck'] == True:
            filterByArgs = {self.getPropertyName(self.USER_NAME):kwargs['username']}
        else:
            if not kwargs.has_key('username') or not kwargs.has_key('password'):
                raise TypeError('SAOrmAuthAdapter needs username and password param')
            
            filterByArgs = {self.getPropertyName(self.USER_NAME):kwargs['username'],
                            self.getPropertyName(self.USER_PASSWORD):kwargs['password']}
            
        return self.session.query(self.userClass).\
               filter_by(**filterByArgs).first()
    
    def checkCredentials(self, **kwargs):
        res = self.__getUserFromDB(**kwargs)
        
        if isinstance(res, self.userClass):
            return True
        else:
            return False
    
    def getAuthenticatedUser(self, **kwargs):
        saUser = self.__getUserFromDB(**kwargs)
        return SAOrmAuthenticatedUser(saUser, self)
    
    def getUserName(self):
        return self.currentAuthenticatedObject.__getattribute__(self.accountPropertyName)
    
    def getGroupName(self):
        pass