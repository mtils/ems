

from ems.qt import QtWidgets, QtGui, QtCore
from ems.qt.graphics.interfaces import Finalizer

pyqtSignal = QtCore.pyqtSignal
Qt = QtCore.Qt
QGraphicsScene = QtWidgets.QGraphicsScene
QColor = QtGui.QColor
QRectF = QtCore.QRectF
QBrush = QtGui.QBrush

class GraphicsScene(QGraphicsScene):

    focusItemChanged = pyqtSignal()

    deleteRequested = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(GraphicsScene, self).__init__(*args, **kwargs)
        self._currentFocusItem = None
        self.setBackgroundBrush(QColor(187,187,187))

    def setFocusItem(self, item, reason=Qt.OtherFocusReason):
        super(GraphicsScene, self).setFocusItem(item, reason)

    def mouseReleaseEvent(self, event):
        super(GraphicsScene, self).mouseReleaseEvent(event)
        focusItem = self.focusItem()
        if self._currentFocusItem is focusItem:
            return
        self._currentFocusItem = focusItem
        self.focusItemChanged.emit()

    def keyReleaseEvent(self, keyEvent):

        if keyEvent.key() != Qt.Key_Delete:
            return super(GraphicsScene, self).keyReleaseEvent(keyEvent)

        if self.focusItem():
            return super(GraphicsScene, self).keyReleaseEvent(keyEvent)

        self.deleteRequested.emit()

class BackgroundCorrector(Finalizer):

    def __init__(self):
        self.originalBrush = QColor()

    def toFinalized(self, scene):
        self.originalBrush = scene.backgroundBrush()
        scene.setBackgroundBrush(QBrush(Qt.NoBrush))

    def toEditable(self, scene):
        scene.setBackgroundBrush(self.originalBrush)