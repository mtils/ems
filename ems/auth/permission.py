
from abc import ABCMeta, abstractmethod

from ems.auth import AccessChecker as AbstractChecker

class Permission(object):

    def __init__(self, code='', title='', access=1):
        super(Permission, self).__init__()
        self.code = code
        self.title = title
        self.access = access

    def __repr__(self):
        return "<{0} code:{1} access:{2}>".format(self.__class__.__name__,self.code, self.access)

class PermissionHolder(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def getPermissionAccess(self, code):
        pass

    @abstractmethod
    def setPermissionAccess(self, code, access):
        pass

    @abstractmethod
    def permissionCodes(self):
        pass

class NestedPermissionHolder(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def getSubHolders(self):
        pass

class AccessChecker(AbstractChecker):

    def hasAccess(self, user, resource, context='access'):
        pass