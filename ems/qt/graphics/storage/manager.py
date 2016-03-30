
from ems.typehint import accepts
from ems.event.hook import EventHook
from ems.qt.graphics.storage.interfaces import SceneStorageManager
from ems.qt import QtWidgets, QtCore
from ems.qt.event_hook_proxy import SignalEventHookProxy
from ems.qt.graphics.storage.interfaces import SceneStorage, TargetUriProvider

Qt = QtCore.Qt
QAction = QtWidgets.QAction
QObject = QtCore.QObject
QWidget = QtWidgets.QWidget

class SceneStorageManager(SceneStorageManager):

    @accepts(SceneStorage, TargetUriProvider, QWidget)
    def __init__(self, storage, targetProvider, parentWidget):
        self._storage = storage
        self._targetProvider = targetProvider
        self._parentWidget = parentWidget
        self._scene = None
        self._tools = None
        self._actions = []
        self._setUpActions()

    def load(self, *args):
        uri = self._targetProvider.targetUriForRead()
        return self._storage.load(self._scene, self._tools, uri)

    def save(self, *args):
        uri = self._targetProvider.targetUriForWrite()
        return self._storage.save(self._scene, self._tools, uri)

    def actions(self):
        return self._actions

    def getScene(self):
        return self._scene

    def setScene(self, scene):
        self._scene = scene

    def getTools(self):
        return self._tools

    def setTools(self, tools):
        self._tools = tools

    def _setUpActions(self):

        self.loadAction = QAction('Load', self._parentWidget, shortcut = Qt.CTRL + Qt.Key_O)
        self.saveAction = QAction('Save', self._parentWidget, shortcut = Qt.CTRL + Qt.Key_S)

        self.loadEvent = SignalEventHookProxy(self.loadAction.triggered)
        self.saveEvent = SignalEventHookProxy(self.saveAction.triggered)

        self.loadEvent.triggered += self.load
        self.saveEvent.triggered += self.save

        self._actions.append(self.loadAction)
        self._actions.append(self.saveAction)

