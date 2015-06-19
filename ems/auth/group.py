
from abc import ABCMeta, abstractmethod

class Group(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def groupId(self):
        pass

class GroupHolder(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def getGroups(self):
        pass

    @abstractmethod
    def attachGroup(self, group):
        pass

    @abstractmethod
    def detachGroup(self, group):
        pass

    @abstractmethod
    def isInGroup(self, group):
        pass