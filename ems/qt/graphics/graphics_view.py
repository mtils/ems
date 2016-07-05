
from ems.qt import QtWidgets, QtGui, QtCore
from ems.qt.graphics.page_item import PageItem

QAction = QtWidgets.QAction
QWidget = QtWidgets.QWidget
pyqtSignal = QtCore.pyqtSignal
Qt = QtCore.Qt
QGraphicsView = QtWidgets.QGraphicsView
QPainter = QtGui.QPainter
QPointF = QtCore.QPointF
QTransform = QtGui.QTransform

class GraphicsView(QGraphicsView):

    emptyAreaClicked = pyqtSignal(QPointF)

    # + 1 on zoom in, -1 on zoom out
    zoomChangeRequested = pyqtSignal(int)

    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)

        self._lastPressedPoint = None
        self._lastReleasedPoint = None
        self._pointCallback = None
        self._pointCancelCallback = None
        self._pointCallbackParams = {}
        self._rectCallback = None
        self._rectCancelCallback = None
        self._rectCallbackParams = {}
        self.setViewport(ViewportWidget())

        self.setDragMode(QGraphicsView.RubberBandDrag)
        #self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)

    def focusOutEvent(self, event):
        #self.discardCurrentRequests()
        super(GraphicsView, self).focusOutEvent(event)

    def mousePressEvent(self, event):

        self._lastPressedPoint = self.mapToScene(event.pos())

        if not self.hasCurrentPointRequest():
            return super(GraphicsView, self).mousePressEvent(event)

        return

        super(GraphicsView, self).mousePressEvent(event)

        clickedItem = self.itemAt(event.pos())

        if clickedItem and not isinstance(clickedItem, PageItem):
            return

        scenePoint = self.mapToScene(event.pos())
        self.emptyAreaClicked.emit(scenePoint)

    def mouseMoveEvent(self, event):
        super(GraphicsView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._lastReleasedPoint = self.mapToScene(event.pos())
        if self.hasCurrentPointRequest():
            self._pointCallback(self.mapToScene(event.pos()), **self._pointCallbackParams)
            self._pointCallback = None
            self._pointCallbackParams.clear()
            return

        super(GraphicsView, self).mouseReleaseEvent(event)

    def wheelEvent(self, event):
        if not int(event.modifiers() & Qt.ControlModifier):
            return super(GraphicsView, self).wheelEvent(event)

        #zoom on ctrl + wheel
        zoomType = 1 if event.delta() > 0 else -1
        self.zoomChangeRequested.emit(zoomType)

    def getPointAnd(self, pointCallback, cancelCallback=None, **params):
        if not callable(pointCallback):
            raise TypeError('pointCallback has to be callable')

        self._pointCallback = pointCallback
        self._pointCallbackParams = params

        if cancelCallback is None:
            return

        if not callable(cancelCallback):
            raise TypeError('cancelCallback has to be callable')

        self._pointCancelCallback = cancelCallback


    def getRectAnd(self, rectCallback, cancelCallback=None, **params):

        if not callable(rectCallback):
            raise TypeError('rectCallback has to be callable')

        self._rectCallback = rectCallback
        self._rectCallbackParams = params

        if not callable(cancelCallback):
            raise TypeError('cancelCallback has to be callable')

        self._rectCancelCallback = cancelCallback

    def hasCurrentRequest(self):
        return self.hasCurrentPointRequest() or self.hasCurrentRectRequest()

    def hasCurrentPointRequest(self):
        return callable(self._pointCallback)

    def hasCurrentRectRequest(self):
        return callable(self._rectCallback)

    def discardCurrentPointRequest(self):
        self._pointCallback = None
        self._pointCallbackParams.clear()
        self._pointCancelCallback = None

    def discardCurrentRectRequest(self):
        self._rectCallback = None
        self._rectCallbackParams.clear()
        self._rectCancelCallback = None

    def discardCurrentRequests(self):
        self.discardCurrentPointRequest()
        self.discardCurrentRectRequest()

    def lastPressedPoint(self):
        return self._lastPressedPoint

    def lastReleasedPoint(self):
        return self._lastReleasedPoint

    def setZoom(self, percent):
        transform = QTransform()
        scale = percent/100.0
        transform.scale(scale, scale)
        self.setTransform(transform)


class ViewportWidget(QWidget):

   EDIT = 1
   PREVIEW = 2
   PRINTING = 3

   def __init__(self, parent=None):
       super(ViewportWidget, self).__init__(parent)
       self.viewMode = self.EDIT