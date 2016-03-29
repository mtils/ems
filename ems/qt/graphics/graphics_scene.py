

from ems.qt import QtWidgets, QtGui, QtCore

pyqtSignal = QtCore.pyqtSignal
Qt = QtCore.Qt
QGraphicsScene = QtWidgets.QGraphicsScene
QColor = QtGui.QColor

class GraphicsScene(QGraphicsScene):

    focusItemChanged = pyqtSignal()

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
