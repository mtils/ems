
from ems.qt import QtWidgets, QtGui, QtCore

QObject = QtCore.QObject
pyqtSignal = QtCore.pyqtSignal
pyqtProperty = QtCore.pyqtProperty
QGraphicsScene = QtWidgets.QGraphicsScene

class GraphicsTool(QObject):

    itemAdded = pyqtSignal()

    def __init__(self, parent=None):
        super(GraphicsTool, self).__init__(parent)
        self._actions = []
        self._scene = None

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

class GraphicsToolDispatcher(GraphicsTool):

    def __init__(self, parent=None):
        super(GraphicsToolDispatcher, self).__init__(parent)
        self._tools = []
        self.itemAdded.connect(self._deactivateActionsAfterItemAdded)

    def addTool(self, tool):
        tool.setScene(self.getScene())
        tool.itemAdded.connect(self.itemAdded)
        self._tools.append(tool)

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