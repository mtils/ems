

from ems.qt.graphics.interfaces import SceneStorageManager

class SceneStorageManager(SceneStorageManager):

    def __init__(self, parent=None):
        super(SceneStorageManager, self).__init__(parent)
        self._scene = None
        self._tools = None

    def actions(self):
        return []

    def getScene(self):
        return self._scene

    def setScene(self, scene):
        self._scene = scene

    def getTools(self):
        return self._tools

    def setTools(self, tools):
        self._tools = tools