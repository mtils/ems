
from ems.event.hook import EventHook
from ems.qt import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt
QObject = QtCore.QObject
pyqtSignal = QtCore.pyqtSignal
pyqtProperty = QtCore.pyqtProperty
QGraphicsItem = QtWidgets.QGraphicsItem
QGraphicsTextItem = QtWidgets.QGraphicsTextItem
QFont = QtGui.QFont
QTransform = QtGui.QTransform
QTextCursor = QtGui.QTextCursor
QTextCharFormat = QtGui.QTextCharFormat
QStyle = QtWidgets.QStyle
QBrush = QtGui.QBrush
QColor = QtGui.QColor
QStyleOptionGraphicsItem = QtWidgets.QStyleOptionGraphicsItem
QRectF = QtCore.QRectF
QSizeF = QtCore.QSizeF
QPointF = QtCore.QPointF
QPainterPath = QtGui.QPainterPath
QPen = QtGui.QPen

class SelectionRenderer(QObject):

    positionChanged = pyqtSignal(QPointF)

    def __init__(self, parent=None):
        super(SelectionRenderer, self).__init__(parent)
        #self._item = item
        self._margin = 10.0
        self._isMoving = False
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

    def mousePress(self, event):
        self._isMoving = True

    def mouseMove(self, itemPos, event):

        scenePos = event.scenePos()
        lastScenePos = event.lastScenePos()
        relativeX = scenePos.x() - lastScenePos.x()
        relativeY = scenePos.y() - lastScenePos.y()

        newPos = QPointF(itemPos.x()+relativeX, itemPos.y()+relativeY)
        self.positionChanged.emit(newPos)

    def mouseRelease(self):
        self._isMoving = False
        self._isResizing = False

    def isMoving(self):
        return self._isMoving

    def isInMoveArea(self, point):
        if not self.belongsToSelection(point):
            return False

    def hasCurrentMouseOperation(self):
        return self._isMoving

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
        return QRectF(self.pos(), self._fixedBounds)

    def shape(self):
        if not self.isSelected():
            return super(TextItem, self).shape()
        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

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

        print('itemChange', change)
        if change != QGraphicsItem.ItemSelectedChange:
            Dirty = True
        result = QGraphicsTextItem.itemChange(self, change, variant)

        if change == QGraphicsItem.ItemPositionChange:
            print('ItemPositionChange', self.pos())

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
        self.setCursor(Qt.DragMoveCursor)

        #print "HoverEnter"
        #print event.pos()
        #print self.boundingRect()
        self.setCursor(Qt.IBeamCursor)
        QGraphicsTextItem.hoverEnterEvent(self, event)

    def hoverMoveEvent(self, event):

        if not self._selectionRenderer.belongsToSelection(event.pos(), self.textBoundingRect()):
            self.setCursor(Qt.IBeamCursor)
            return

        self.setCursor(Qt.DragMoveCursor)
        #print 'HoverMove'
        #print self.boundingRect()
        
        QGraphicsTextItem.hoverMoveEvent(self, event)

    def hoverLeaveEvent(self, event):
        print "HoverLeave"
        QGraphicsTextItem.hoverLeaveEvent(self, event)

    def mouseReleaseEvent(self, event):
        self._selectionRenderer.mouseRelease()
        if not self._selectionRenderer.belongsToSelection(event.pos(), self.textBoundingRect()):
            super(TextItem, self).mouseReleaseEvent(event)
            self._updateCursorPosition(self.textCursor())
            return
        self.setSelected(True)

    def mouseMoveEvent(self, event):
        #if not self._selectionRenderer.belongsToSelection(event.pos(), self.textBoundingRect()):
            #super(TextItem, self).mouseMoveEvent(event)
            #return

        if not self._selectionRenderer.hasCurrentMouseOperation():
            return super(TextItem, self).mouseMoveEvent(event)

        self._selectionRenderer.mouseMove(self.pos(), event)

        #scenePos = event.scenePos()
        #lastScenePos = event.lastScenePos()
        #relativeX = scenePos.x() - lastScenePos.x()
        #relativeY = scenePos.y() - lastScenePos.y()
        #currentPos = self.pos()

        #newPos = QPointF(currentPos.x()+relativeX, currentPos.y()+relativeY)
        #self.setPos(newPos)
        #print('mouseMoveEvent', event.scenePos(), event.lastScenePos(), self.pos())
        #self.positionChanged.fire(self.pos())

    def mousePressEvent(self, event):
        if not self._selectionRenderer.belongsToSelection(event.pos(), self.textBoundingRect()):
            super(TextItem, self).mousePressEvent(event)
            return
        self._selectionRenderer.mousePress(event)
        super(TextItem, self).mousePressEvent(event)
        print('mousePressEvent', event.pos())

    def keyReleaseEvent(self, event):
        super(TextItem, self).keyReleaseEvent(event)
        self._updateCursorPosition(self.textCursor())

    def currentCharFormat(self):
        return self.textCursor().charFormat()

    def paint(self, painter, option, widget=None):

        newOption = QStyleOptionGraphicsItem(option)
        newOption.state = newOption.state & ~QStyle.State_Selected & ~QStyle.State_HasFocus

        super(TextItem, self).paint(painter, newOption, widget)

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