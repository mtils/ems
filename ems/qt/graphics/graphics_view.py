
from ems.qt import QtWidgets, QtGui, QtCore
from ems.qt.graphics.page_item import PageItem

QAction = QtWidgets.QAction
pyqtSignal = QtCore.pyqtSignal
QGraphicsView = QtWidgets.QGraphicsView
QPainter = QtGui.QPainter
QPointF = QtCore.QPointF
QTransform = QtGui.QTransform

class GraphicsView(QGraphicsView):

    emptyAreaClicked = pyqtSignal(QPointF)

    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        #self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)

    def mousePressEvent(self, event):
        super(GraphicsView, self).mousePressEvent(event)

        clickedItem = self.itemAt(event.pos())

        if clickedItem and not isinstance(clickedItem, PageItem):
            return

        scenePoint = self.mapToScene(event.pos())
        self.emptyAreaClicked.emit(scenePoint)

    def setZoom(self, percent):
        transform = QTransform()
        scale = percent/100.0
        transform.scale(scale, scale)
        self.setTransform(transform)