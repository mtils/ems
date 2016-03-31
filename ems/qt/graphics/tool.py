
from ems.qt import QtWidgets, QtGui, QtCore

from ems.qt.graphics.graphics_view import GraphicsView

QObject = QtCore.QObject
QEvent = QtCore.QEvent
pyqtSignal = QtCore.pyqtSignal
pyqtProperty = QtCore.pyqtProperty
QGraphicsScene = QtWidgets.QGraphicsScene
QAction = QtWidgets.QAction
QPointF = QtCore.QPointF
QRectF = QtCore.QRectF

class ToolAction(QAction):

    invokedAtPoint = pyqtSignal(QPointF)

    invokedAtRect = pyqtSignal(QRectF)

    DIRECT = 0

    POINT = 1

    RECT = 2

    def __init__(self, *args, **kwargs):
        super(ToolAction, self).__init__(*args, **kwargs)
        self._type = ToolAction.DIRECT


    def invoke(self, view):
        if not self.isCheckable():
            return
        if not self.isChecked():
            return
        if self.type() == ToolAction.POINT:
            print 'getPointAnd', view
            view.getPointAnd(self.invokeAtPoint)
            return
        if self.type() == ToolAction.RECT:
            view.getRectAnd(self.invokeAtRect)
            return

    def invokeAtPoint(self, point):
        self.invokedAtPoint.emit(point)

    def invokeAtRect(self, rect):
        self.invokedAtRect.emit(rect)

    def invokeByType(self, point=None, rect=None):
        if self._type == ToolAction.DIRECT:
            return self.invoke()
        if self._type == ToolAction.POINT:
            return self.invokeAtPoint(point)
        if self._type == ToolAction.RECT:
            return self.invokeAtRect(rect)

    def type(self):
        return self._type


class GraphicsTool(QObject):

    invoked = pyqtSignal()

    cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super(GraphicsTool, self).__init__(parent)
        self._actions = []
        self._scene = None
        self._view = None

    def getActions(self):
        return self._actions

    actions = pyqtProperty(list, getActions)

    def isSelected(self):
        for action in self._actions:
            if action.isChecked():
                return True
        return False

    def canHandle(self, item):
        return False

    def setCurrentItem(self, item):
        return

    def resetCurrentItem(self):
        pass

    def addItemAt(self, point):
        pass

    def canSerialize(self, item):
        return False

    def canDeserialize(self, itemData):
        return False

    def serialize(self, item):
        return

    def deserialize(self, itemData):
        return

    def getScene(self):
        return self._scene

    def setScene(self, scene):
        self._scene = scene

    scene = pyqtProperty(QGraphicsScene, getScene, setScene)

    def getView(self):
        if self._view:
            return self._view

        self._view = self.scene.views()[0]
        if not self._view:
            raise LookupError('No view for scene {0} found'.format(self.scene))
        return self._view

    def setView(self, view):
        self._view = view

    view = pyqtProperty(GraphicsView, getView, setView)

    def mousePressWhenActive(self, event):
        return False

    def mouseMoveWhenActive(self, event):
        return False

    def mouseReleaseWhenActive(self, event):
        return False

    def getPointAnd(self, callback, cancelCallback=None, **params):
        self.view.getPointAnd(callback, cancelCallback, **params)

    def getRectAnd(self, callback, cancelCallback=None, **params):
        self.view.getRectAnd(callback, cancelCallback, **params)

class GraphicsToolDispatcher(GraphicsTool):

    def __init__(self, parent=None):
        super(GraphicsToolDispatcher, self).__init__(parent)
        self._tools = []

    def addTool(self, tool):
        tool.setScene(self.getScene())
        self._tools.append(tool)
        self._connectToolActions(tool)
        self._invokedTool = None

    def tools(self):
        return self._tools

    def getActions(self):
        actions = []
        for tool in self._tools:
            for action in tool.actions:
                actions.append(action)
        return actions

    actions = pyqtProperty(list, getActions)

    def isSelected(self):
        for tool in self._tools:
            if tool.isSelected():
                return True
        return False

    def canHandle(self, item):
        for tool in self._tools:
            if tool.canHandle(item):
                return True
        return False

    def addItemAt(self, point):
        for tool in self._tools:
            if tool.isSelected():
                tool.addItemAt(point)

    def canSerialize(self, item):
        try:
            self._findSerializer(item)
            return True
        except LookupError:
            return False

    def canDeserialize(self, itemData):
        try:
            self._findDeserializer(itemData)
            return True
        except LookupError:
            return False

    def serialize(self, item):
        return self._findSerializer(item).serialize(item)

    def deserialize(self, itemData):
        return self._findDeserializer(itemData).deserialize(itemData)

    def setScene(self, scene):
        super(GraphicsToolDispatcher, self).setScene(scene)
        for tool in self._tools:
            tool.setScene(scene)

    def updateFocusItem(self):
        focusItem = self.scene.focusItem()

        for tool in self._tools:
            tool.resetCurrentItem()

        if focusItem is None:
            return

        for tool in self._tools:
            if tool.canHandle(focusItem):
                tool.setCurrentItem(focusItem)

    def _findSerializer(self, item):
        for tool in self._tools:
            if tool.canSerialize(item):
                return tool
        raise LookupError('No tool found to serialize {}'.format(item))

    def _findDeserializer(self, itemData):
        for tool in self._tools:
            if tool.canDeserialize(itemData):
                return tool
        raise LookupError('No tool found to deserialize {}'.format(itemData))

    def _deactivateActionsAfterItemAdded(self):
        for action in self.actions:
            action.setChecked(False)

    def _connectToolActions(self, tool):
        for action in tool.actions:
            if action.isCheckable():
               action.toggled.connect(self._onToolActionToggled)
               continue
            action.triggered.connect(self._onToolActionTriggered)

    def _onToolActionToggled(self, toggled):
        if not toggled:
            return self._uninstallMouseFilterIfNoActionChecked()
        action = self.sender()
        self._uncheckActionsExcept(action)

        self._invokedTool = self._findToolOfAction(action)

        if not self._invokedTool:
            return

        #action.invoke(self.view)
        self._installMouseFilter()

    def _onToolActionTriggered(self):
        self._uncheckActionsExcept(self.sender())

    def _uncheckActionsExcept(self, exceptAction=None):
        for action in self.actions:
            if action.isCheckable() and action is not exceptAction:
                action.setChecked(False)

    def _installMouseFilter(self):
        self.scene.installEventFilter(self)

    def _uninstallMouseFilterIfNoActionChecked(self):
        for action in self.actions:
            if action.isCheckable() and action.isChecked():
                return
        self.scene.removeEventFilter(self)
        self._invokedTool = None

    def eventFilter(self, view, event):

        if not self._invokedTool:
            return False

        if event.type() == QEvent.GraphicsSceneMousePress:
            return self._invokedTool.mousePressWhenActive(event)
        if event.type() == QEvent.GraphicsSceneMouseMove:
            return self._invokedTool.mouseMoveWhenActive(event)
        if event.type() == QEvent.GraphicsSceneMouseRelease:
            result = self._invokedTool.mouseReleaseWhenActive(event)
            self._uncheckActionsExcept()
            return result

        return False

    def _findToolOfAction(self, action):
        for tool in self.tools():
            if action in tool.actions:
                return tool