
from abc import ABCMeta, abstractmethod

from six import add_metaclass

@add_metaclass(ABCMeta)
class SceneStorageManager(object):

    def __init__(self, parent=None):
        super(SceneStorageManager, self).__init__(parent)
        self._scene = None
        self._tools = None

    @abstractmethod
    def load(self, *args):
        pass

    @abstractmethod
    def save(self, *args):
        pass

    @abstractmethod
    def setScene(self, scene):
        self._scene = scene

    @abstractmethod
    def setTools(self, tools):
        self._tools = tools


@add_metaclass(ABCMeta)
class SceneSerializer(object):

    @abstractmethod
    def serialize(self, scene, tools):
        pass

    @abstractmethod
    def deserialize(self, sceneData, scene, tools):
        pass

@add_metaclass(ABCMeta)
class TargetUriProvider(object):

    @abstractmethod
    def targetUriForRead(self):
        pass

    @abstractmethod
    def targetUriForWrite(self):
        pass

@add_metaclass(ABCMeta)
class SceneStorage(object):

    @abstractmethod
    def load(self, scene, tools, uri):
        pass

    @abstractmethod
    def save(self, scene, tools, uri):
        pass


