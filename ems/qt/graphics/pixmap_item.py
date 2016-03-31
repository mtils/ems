

from ems.qt import QtCore, QtGui, QtWidgets
from ems.qt.graphics.bounds_editor import BoundsEditor
from ems.qt.event_hook_proxy import SignalEventHookProxy

Qt = QtCore.Qt
pyqtSignal = QtCore.pyqtSignal
pyqtProperty = QtCore.pyqtProperty
QGraphicsItem = QtWidgets.QGraphicsItem
QGraphicsPixmapItem = QtWidgets.QGraphicsPixmapItem
QFont = QtGui.QFont
QTransform = QtGui.QTransform
QTextCursor = QtGui.QTextCursor
QTextCharFormat = QtGui.QTextCharFormat
QTextBlockFormat = QtGui.QTextBlockFormat
QStyle = QtWidgets.QStyle
QStyleOptionGraphicsItem = QtWidgets.QStyleOptionGraphicsItem
QRectF = QtCore.QRectF
QPointF = QtCore.QPointF
QSizeF = QtCore.QSizeF
QPainterPath = QtGui.QPainterPath
QApplication = QtWidgets.QApplication
QKeyEvent = QtGui.QKeyEvent
QEvent = QtCore.QEvent
QPixmap = QtGui.QPixmap

class PixmapItem(QGraphicsPixmapItem):

    def __init__(self, parent=None):
        super(PixmapItem, self).__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable)

        self._boundsEditor = BoundsEditor(self, self.imageBoundingRect)
        self._boundsEditor.itemRectPenWidth = 2.0
        self._positionProxy = SignalEventHookProxy(self._boundsEditor.positionChanged)
        self._sizeProxy = SignalEventHookProxy(self._boundsEditor.sizeChanged)
        self._imageScale = 1.0

        self._positionProxy.triggered += self.setPos
        self._sizeProxy.triggered += self.setSize

        self._pixmapPath = ''
        self._size = QSizeF()
        if hasattr(self, 'setAcceptsHoverEvents'):
            self.setAcceptsHoverEvents(True)
        else:
            self.setAcceptHoverEvents(True)

    def pixmapPath(self):
        return self._pixmapPath

    def setPixmapPath(self, path):
        if self._pixmapPath == path:
            return
        self._pixmapPath = path
        self.setPixmap(QPixmap(self._pixmapPath))

    def setPixmap(self, pixmap):
        super(PixmapItem, self).setPixmap(pixmap)
        if self._size.isEmpty():
            self._size = QSizeF(pixmap.rect().size())

    def size(self):
        return self._size

    def setSize(self, size):
        if self._size == size:
            return

        oldSize = self._size

        self._size = size

        widthDiff = abs(size.width() - oldSize.width())
        heightDiff = abs(size.height() - oldSize.height())

        originalSize = self.pixmap().size()
        originalWidth = float(originalSize.width())
        originalHeight = float(originalSize.height())

        try: 
            if widthDiff == 0.0 and heightDiff > 0.0: # vertical
                scale = 1.0 / (originalHeight / size.height())
            elif widthDiff > 0.0 and heightDiff == 0.0: #horizontal
                scale = 1.0 / (originalWidth / size.width())
            else:
                scale = 1.0 / (originalWidth / size.width())
        except ZeroDivisionError:
            scale = 1.0

        self._size = QSizeF(originalWidth * scale,
                            originalHeight * scale)

        self._imageScale = scale
        self.prepareGeometryChange()


    def imageBoundingRect(self):
        if self._size:
            return QRectF(QPointF(0,0), self._size)
        return super(PixmapItem, self).boundingRect()

    def boundingRect(self):
        imageBoundingRect = self.imageBoundingRect()
        if not self.isSelected():
            return imageBoundingRect
        return self._boundsEditor.boundingRect(imageBoundingRect)

    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def paint(self, painter, option, widget=None):

        originalRect = option.exposedRect
        smallerRect = self.imageBoundingRect()
        option.exposedRect = smallerRect

        originalTransform = painter.transform()
        transform = QTransform()
        transform.scale(self._imageScale, self._imageScale)
        painter.setTransform(transform, True)

        newOption = QStyleOptionGraphicsItem(option)
        newOption.state = newOption.state & ~QStyle.State_Selected & ~QStyle.State_HasFocus

        super(PixmapItem, self).paint(painter, newOption, widget)

        option.exposedRect = originalRect

        painter.setTransform(originalTransform)

        self._boundsEditor.paintSelection(painter, option, widget)

    def hoverEnterEvent(self, event):

        if not self._boundsEditor.hoverEnterEvent(event):
            return super(PixmapItem, self).hoverEnterEvent(event)

    def hoverMoveEvent(self, event):

        if not self._boundsEditor.hoverMoveEvent(event):
            self.setCursor(Qt.DragMoveCursor)
            return super(PixmapItem, self).hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        self._boundsEditor.hoverLeaveEvent(event)
        super(PixmapItem, self).hoverLeaveEvent(event)


    def mousePressEvent(self, event):
        if not self._boundsEditor.mousePressEvent(event):
            return super(PixmapItem, self).mousePressEvent(event)


    def mouseMoveEvent(self, event):
        if not self._boundsEditor.mouseMoveEvent(event):
            return super(PixmapItem, self).mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):

        if not self._boundsEditor.mouseReleaseEvent(event):
            super(PixmapItem, self).mouseReleaseEvent(event)
        self.setSelected(True)
