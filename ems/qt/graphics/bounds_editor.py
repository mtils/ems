
from ems.event.hook import EventHook
from ems.qt import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt
QObject = QtCore.QObject
pyqtSignal = QtCore.pyqtSignal
pyqtProperty = QtCore.pyqtProperty
QGraphicsItem = QtWidgets.QGraphicsItem
QRegion = QtGui.QRegion
QColor = QtGui.QColor
QRectF = QtCore.QRectF
QSizeF = QtCore.QSizeF
QPointF = QtCore.QPointF
QPainterPath = QtGui.QPainterPath
QPen = QtGui.QPen

class BoundsEditor(QObject):

    positionChanged = pyqtSignal(QPointF)

    sizeChanged = pyqtSignal(QSizeF)

    MOVE = 'move'

    RESIZE = 'resize'

    RESIZE_HORIZONTAL = 'resize_h'

    RESIZE_VERTICAL = 'resize_v'

    ITEM = 'item'

    def __init__(self, parent=None):
        super(BoundsEditor, self).__init__(parent)
        #self._item = item
        self._margin = 10.0
        self._isMoving = False
        self._currentMouseOperation = ''
        self._isResizing = False
        self._selectionBoundsColor = QColor(187,187,187)
        self._itemBoundsColor = QColor(85, 85, 85)

    def paintSelection(self, painter, itemBoundingRect):

        pen = QPen(Qt.SolidLine)
        pen.setColor(self._itemBoundsColor)
        pen.setWidthF(1.0)

        painter.setPen(pen)

        painter.drawRect(itemBoundingRect)

        boundingRect = self.boundingRect(itemBoundingRect)

        pen = QPen(Qt.SolidLine)
        pen.setColor(self._selectionBoundsColor)
        pen.setWidthF(1.0)

        painter.setPen(pen)

        painter.drawRect(boundingRect)

    def boundingRect(self, itemBoundingRect):
        myRect = QRectF(itemBoundingRect.topLeft(), itemBoundingRect.size())
        myRect.setWidth(itemBoundingRect.width() + self._margin + self._margin)
        myRect.setHeight(itemBoundingRect.height() + self._margin + self._margin)
        myRect.moveTo(itemBoundingRect.x() - self._margin, itemBoundingRect.y() - self._margin)
        return myRect

    def shape(self, boundingRect):
        pass

    def belongsToSelection(self, pos, itemBoundingRect):
        selectionRect = self.boundingRect(itemBoundingRect)
        if not selectionRect.contains(pos):
            return False
        if itemBoundingRect.contains(pos):
            return False
        return True

    def mousePress(self, event, itemBoundingRect):
        self._isMoving = True
        areaType = self.areaType(event.pos(), itemBoundingRect)
        if areaType == self.ITEM:
            self._currentMouseOperation = ''
            return
        self._currentMouseOperation = areaType

    def mouseMove(self, itemPos, event, itemBoundingRect):

        scenePos = event.scenePos()
        lastScenePos = event.lastScenePos()
        relativeX = scenePos.x() - lastScenePos.x()
        relativeY = scenePos.y() - lastScenePos.y()

        if self._currentMouseOperation == self.MOVE:
            newPos = QPointF(itemPos.x()+relativeX, itemPos.y()+relativeY)
            self.positionChanged.emit(newPos)

        if self._currentMouseOperation == self.RESIZE_VERTICAL:
            size = QSizeF(itemBoundingRect.width(), itemBoundingRect.height()+relativeY)
            self.sizeChanged.emit(size)

        if self._currentMouseOperation == self.RESIZE_HORIZONTAL:
            size = QSizeF(itemBoundingRect.width()+relativeX, itemBoundingRect.height())
            self.sizeChanged.emit(size)

        if self._currentMouseOperation == self.RESIZE:
            size = QSizeF(itemBoundingRect.width()+relativeX, itemBoundingRect.height()+relativeY)
            self.sizeChanged.emit(size)

    def mouseRelease(self):
        self._currentMouseOperation = ''
        self._isMoving = False
        self._isResizing = False

    def areaType(self, point, itemBoundingRect):
        selectionRect = self.boundingRect(itemBoundingRect)
        if not selectionRect.contains(point):
            return self.ITEM
        if itemBoundingRect.contains(point):
            return self.ITEM
        if point.x() <= itemBoundingRect.topLeft().x():
            return self.MOVE # left rect
        if point.y() <= itemBoundingRect.topLeft().y():
            return self.MOVE # top rect
        # x > topLeft.x, y > topLeft.y()
        if point.y() > itemBoundingRect.bottomRight().y():
            if point.x() < itemBoundingRect.bottomRight().x():
                return self.RESIZE_VERTICAL
            return self.RESIZE
        if point.x() > itemBoundingRect.bottomRight().x():
            return self.RESIZE_HORIZONTAL
        return self.RESIZE

    def hasCurrentMouseOperation(self):
        return bool(self._currentMouseOperation)

    def getCursorByPosition(self, pos, itemBoundingRect):
        areaType = self.areaType(pos, itemBoundingRect)
        if areaType == BoundsEditor.MOVE:
            return Qt.DragMoveCursor
        if areaType == BoundsEditor.RESIZE:
            return Qt.SizeFDiagCursor
        if areaType == BoundsEditor.RESIZE_HORIZONTAL:
            return Qt.SizeHorCursor
        if areaType == BoundsEditor.RESIZE_VERTICAL:
            return Qt.SizeVerCursor