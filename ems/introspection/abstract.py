
from abc import ABCMeta, abstractmethod

class TitleIntrospector(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def keyTitle(self, cls, path):
        pass

    @abstractmethod
    def classTitle(self, cls, quantity=1):
        pass

    @abstractmethod
    def enumTitle(self, path, value):
        pass