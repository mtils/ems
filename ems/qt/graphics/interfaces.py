
from six import add_metaclass

from abc import ABCMeta, abstractmethod

@add_metaclass(ABCMeta)
class SceneRepository(object):

    @abstractmethod
    def save(self, scene, tools):
        pass

    @abstractmethod
    def load(self, scene, tools):
        pass