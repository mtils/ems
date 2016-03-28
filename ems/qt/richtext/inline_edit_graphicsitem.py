
from ems.event.hook import EventHook
from ems.qt import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt
QObject = QtCore.QObject
pyqtSignal = QtCore.pyqtSignal
pyqtProperty = QtCore.pyqtProperty
QGraphicsItem = QtWidgets.QGraphicsItem
QGraphicsTextItem = QtWidgets.QGraphicsTextItem
QFont = QtGui.QFont
QRegion = QtGui.QRegion
QTransform = QtGui.QTransform
QTextCursor = QtGui.QTextCursor
QTextCharFormat = QtGui.QTextCharFormat
QStyle = QtWidgets.QStyle
QBrush = QtGui.QBrush
QColor = QtGui.QColor
QStyleOptionGraphicsItem = QtWidgets.QStyleOptionGraphicsItem
QRectF = QtCore.QRectF
QRect = QtCore.QRect
QSizeF = QtCore.QSizeF
QPointF = QtCore.QPointF
QPainterPath = QtGui.QPainterPath
QPen = QtGui.QPen

class SelectionRenderer(QObject):

    positionChanged = pyqtSignal(QPointF)

    sizeChanged = pyqtSignal(QSizeF)

    MOVE = 'move'

    RESIZE = 'resize'

    RESIZE_HORIZONTAL = 'resize_h'

    RESIZE_VERTICAL = 'resize_v'

    ITEM = 'item'

    def __init__(self, parent=None):
        super(SelectionRenderer, self).__init__(parent)
        #self._item = item
        self._margin = 10.0
        self._isMoving = False
        self._currentMouseOperation = ''
        self._isResizing = False

    def paintSelection(self, painter, boundingRect):

        pen = QPen(Qt.SolidLine)
        pen.setColor(QColor(128,179,255))
        pen.setWidthF(1.0)

        painter.setPen(pen)

        painter.drawRect(boundingRect)

        rect = self.boundingRect(boundingRect)

        painter.drawRect(rect)

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
        if areaType == SelectionRenderer.MOVE:
            return Qt.DragMoveCursor
        if areaType == SelectionRenderer.RESIZE:
            return Qt.SizeFDiagCursor
        if areaType == SelectionRenderer.RESIZE_HORIZONTAL:
            return Qt.SizeHorCursor
        if areaType == SelectionRenderer.RESIZE_VERTICAL:
            return Qt.SizeVerCursor

class TextItem(QGraphicsTextItem):

    cursorPositionChanged = pyqtSignal([QTextCursor],[int])

    currentCharFormatChanged = pyqtSignal(QTextCharFormat)

    fixedBoundsChanged = pyqtSignal(QSizeF)

    def __init__(self, text, position, scene,
                 font=None, transform=QTransform()):
        font = font if font is not None else QFont("Arial", 12)
        super(TextItem, self).__init__(text)
        self._lastCursorPosition = -1
        self._lastCharFormat = None
        self.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable)
        self.setFont(font)
        self.setPos(position)
        self.setTransform(transform)
        self.setTextInteractionFlags(Qt.TextEditable | Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.cursorPositionChanged[QTextCursor].connect(self._updateStyle)
        self.positionChanged = EventHook()
        self._selectionRenderer = SelectionRenderer()
        self._selectionRenderer.positionChanged.connect(self.setPos)
        self._selectionRenderer.sizeChanged.connect(self.setFixedBounds)
        self._fixedBounds = QSizeF()


    def getFixedBounds(self):
        return self._fixedBounds

    def setFixedBounds(self, size):
        if self._fixedBounds == size:
            return
        self._fixedBounds = size
        if not self._fixedBounds.isEmpty():
            self.document().setTextWidth(self._fixedBounds.width())
        self.fixedBoundsChanged.emit(self._fixedBounds)
        self.prepareGeometryChange()

    fixedBounds = pyqtProperty(QSizeF, getFixedBounds, setFixedBounds, notify=fixedBoundsChanged)

    def _updateSelection(self, selected):
        self.prepareGeometryChange()

    def boundingRect(self):
        textBoundingRect = self.textBoundingRect()
        if not self.isSelected():
            return textBoundingRect

        return self._selectionRenderer.boundingRect(textBoundingRect)

    def textBoundingRect(self):
        if self._fixedBounds.isEmpty():
            return super(TextItem, self).boundingRect()
        return QRectF(QPointF(0.0, 0.0), self._fixedBounds)

    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def textClipRegion(self):
        textBoundingRect = self.textBoundingRect()
        return QRegion(textBoundingRect.toRect())

    def itemChange(self, change, variant):

        result = QGraphicsTextItem.itemChange(self, change, variant)

        if change != QGraphicsItem.ItemSelectedChange:
            return result

        if hasattr(variant, 'toBool'):
            selected = variant.toBool()
        else:
            selected = variant

        self._updateSelection(selected)

        return result

    def mergeFormatOnWordOrSelection(self, format):
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)

        cursor.mergeCharFormat(format)
        #self.textEdit.mergeCurrentCharFormat(format)

    def hoverEnterEvent(self, event):
        if not self._selectionRenderer.belongsToSelection(event.pos(), self.textBoundingRect()):
            self.setCursor(Qt.IBeamCursor)
            return

        cursorType = self._selectionRenderer.getCursorByPosition(event.pos(), self.textBoundingRect())

        if cursorType:
            self.setCursor(cursorType)

    def hoverMoveEvent(self, event):

        if not self._selectionRenderer.belongsToSelection(event.pos(), self.textBoundingRect()):
            self.setCursor(Qt.IBeamCursor)
            return

        cursorType = self._selectionRenderer.getCursorByPosition(event.pos(), self.textBoundingRect())

        if cursorType:
            self.setCursor(cursorType)

    def mouseReleaseEvent(self, event):
        self._selectionRenderer.mouseRelease()
        if not self._selectionRenderer.belongsToSelection(event.pos(), self.textBoundingRect()):
            super(TextItem, self).mouseReleaseEvent(event)
            self._updateCursorPosition(self.textCursor())
            return
        self.setSelected(True)

    def mouseMoveEvent(self, event):
        if not self._selectionRenderer.hasCurrentMouseOperation():
            return super(TextItem, self).mouseMoveEvent(event)

        self._selectionRenderer.mouseMove(self.pos(), event, self.textBoundingRect())

    def mousePressEvent(self, event):
        if not self._selectionRenderer.belongsToSelection(event.pos(), self.textBoundingRect()):
            super(TextItem, self).mousePressEvent(event)
            return
        self._selectionRenderer.mousePress(event, self.textBoundingRect())
        super(TextItem, self).mousePressEvent(event)

    def keyReleaseEvent(self, event):
        super(TextItem, self).keyReleaseEvent(event)
        self._updateCursorPosition(self.textCursor())

    def currentCharFormat(self):
        return self.textCursor().charFormat()

    def paint(self, painter, option, widget=None):

        originalRect = option.exposedRect
        smallerRect = self.textBoundingRect()
        option.exposedRect = smallerRect

        newOption = QStyleOptionGraphicsItem(option)
        newOption.state = newOption.state & ~QStyle.State_Selected & ~QStyle.State_HasFocus

        super(TextItem, self).paint(painter, newOption, widget)

        option.exposedRect = originalRect

        if not (option.state & QStyle.State_Selected):
            return

        self._selectionRenderer.paintSelection(painter, self.textBoundingRect())

    def _updateStyle(self, cursor):
        currentCharFormat = cursor.charFormat()
        if self._lastCharFormat == currentCharFormat:
            return
        self._lastCharFormat = currentCharFormat
        self.currentCharFormatChanged.emit(currentCharFormat)


    def _updateCursorPosition(self, cursor):
        if self._lastCursorPosition == cursor.position():
            return
        self._lastCursorPosition = cursor.position()
        self.cursorPositionChanged[QTextCursor].emit(cursor)
        self.cursorPositionChanged[int].emit(self._lastCursorPosition)