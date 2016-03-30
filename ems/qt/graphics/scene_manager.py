
from ems.typehint import accepts
from ems.qt.event_hook_proxy import SignalEventHookProxy
from ems.qt import QtWidgets, QtGui, QtCore
from ems.qt.graphics.graphics_scene import GraphicsScene
from ems.qt.graphics.graphics_widget import GraphicsWidget
from ems.qt.graphics.storage.interfaces import SceneStorageManager
from ems.qt.graphics.tool import GraphicsTool
from ems.qt.graphics.tool import GraphicsToolDispatcher
from ems.qt.graphics.text_tool import TextTool

Qt = QtCore.Qt
QObject = QtCore.QObject
pyqtProperty = QtCore.pyqtProperty
pyqtSlot = QtCore.pyqtSlot
QWidget = QtWidgets.QWidget
QVBoxLayout = QtWidgets.QVBoxLayout
QToolBar = QtWidgets.QToolBar
QSlider = QtWidgets.QSlider
QAction = QtWidgets.QAction


class SceneManager(QObject):

    def __init__(self, parent=None, storageManager=None):
        super(SceneManager, self).__init__(parent)
        self._scene = None
        self._widget = None
        self._tools = None
        self._storageManager = None
        self._importStorageManager = None
        self._loadAction = None
        self._saveAction = None
        self._importAction = None
        self._exportAction = None
        self._actions = []
        if storageManager:
            self.setStorageManager(storageManager)

    def actions(self):
        if not self._actions:
            self._populateActions()
        return self._actions

    def getScene(self):
        if not self._scene:
            self._scene = GraphicsScene()
        return self._scene

    scene = pyqtProperty(GraphicsScene, getScene)

    def getWidget(self):
        if not self._widget:
            self._widget = GraphicsWidget(scene=self.scene, tools=self.tools)
            for action in self.actions():
                self._widget.addAction(action)
        return self._widget

    widget = pyqtProperty(GraphicsWidget, getWidget)

    def getTools(self):
        if not self._tools:
            self._tools = self._createTools()
        return self._tools

    tools = pyqtProperty(GraphicsTool, getTools)

    def load(self, *args):
        if self._storageManager:
            return self._storageManager.load()

    def save(self, *args):
        if self._storageManager:
            return self._storageManager.save()

    def importScene(self, *args):
        if self._importStorageManager:
            return self._importStorageManager.load()

    def exportScene(self, *args):
        if self._importStorageManager:
            return self._importStorageManager.save()

    def getStorageManager(self):
        return self._storageManager

    @pyqtSlot(SceneStorageManager)
    def setStorageManager(self, storageManager):
        self._storageManager = storageManager
        self._storageManager.setScene(self.scene)
        self._storageManager.setTools(self.tools)

    storageManager = pyqtProperty(SceneStorageManager, getStorageManager, setStorageManager)

    @property
    def loadAction(self):
        if self._loadAction:
            return self._loadAction

        self._loadAction = QAction('Load', self.getWidget(), shortcut = Qt.CTRL + Qt.Key_O)
        self._loadAction.triggered.connect(self.load)
        return self._loadAction

    @property
    def saveAction(self):
        if self._saveAction:
            return self._saveAction
        self._saveAction = QAction('Save', self.getWidget(), shortcut = Qt.CTRL + Qt.Key_S)
        self._saveAction.triggered.connect(self.save)
        return self._saveAction

    @property
    def importAction(self):
        if self._importAction:
            return self._importAction
        self._importAction = QAction('Import', self.getWidget())
        self._importAction.triggered.connect(self.importScene)
        return self._importAction

    @property
    def exportAction(self):
        if self._exportAction:
            return self._exportAction
        self._exportAction = QAction('Export', self.getWidget())
        self._exportAction.triggered.connect(self.exportScene)
        return self._exportAction

    def _createTools(self):
        tools = GraphicsToolDispatcher(self)
        tools.setScene(self.scene)
        textTool = TextTool()
        tools.addTool(textTool)
        return tools

    def _populateActions(self):
        if self._actions:
            return
        self._actions.append(self.loadAction)
        self._actions.append(self.saveAction)
        self._actions.append(self.importAction)
        self._actions.append(self.exportAction)