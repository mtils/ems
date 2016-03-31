
from ems.typehint import accepts
from ems.qt.graphics.storage.interfaces import SceneStorageManager as AbstractSceneStorageManager
from ems.qt import QtWidgets, QtCore
from ems.qt.event_hook_proxy import SignalEventHookProxy
from ems.qt.graphics.storage.interfaces import SceneStorage, TargetUriProvider

Qt = QtCore.Qt
QAction = QtWidgets.QAction
QObject = QtCore.QObject

class SceneStorageManager(AbstractSceneStorageManager):

    @accepts(SceneStorage, TargetUriProvider)
    def __init__(self, storage, targetProvider):
        self._storage = storage
        self._targetProvider = targetProvider
        self._scene = None
        self._tools = None
        self._actions = []

    def load(self, *args):
        uri = self._targetProvider.targetUriForRead()
        if not uri:
            return
        return self._storage.load(self._scene, self._tools, uri)

    def save(self, *args):
        uri = self._targetProvider.targetUriForWrite()
        if not uri:
            return
        return self._storage.save(self._scene, self._tools, uri)

    def getScene(self):
        return self._scene

    def setScene(self, scene):
        self._scene = scene

    def getTools(self):
        return self._tools

    def setTools(self, tools):
        self._tools = tools

