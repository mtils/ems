
from ems.qt import QtCore, QtGui, QtWidgets
from ems.qt.graphics.bounds_editor import BoundsEditor

Qt = QtCore.Qt
pyqtSignal = QtCore.pyqtSignal
pyqtProperty = QtCore.pyqtProperty
QGraphicsItem = QtWidgets.QGraphicsItem
QGraphicsTextItem = QtWidgets.QGraphicsTextItem
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

class TextItem(QGraphicsTextItem):

    cursorPositionChanged = pyqtSignal([QTextCursor],[int])

    currentCharFormatChanged = pyqtSignal(QTextCharFormat)

    currentBlockFormatChanged = pyqtSignal(QTextBlockFormat)

    fixedBoundsChanged = pyqtSignal(QSizeF)

    undoAvailable = pyqtSignal(bool)

    redoAvailable = pyqtSignal(bool)

    hasSelectionChanged = pyqtSignal(bool)


    def __init__(self, text, position, font=None, transform=QTransform()):
        font = font if font is not None else QFont("Arial", 12)
        super(TextItem, self).__init__(text)
        self._lastCursorPosition = -1
        self._lastCharFormat = None
        self._lastBlockFormat = None
        self.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable)
        self.setFont(font)
        self.setPos(position)
        self.setTransform(transform)
        self.setTextInteractionFlags(Qt.TextEditable | Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.cursorPositionChanged[QTextCursor].connect(self._updateStyle)
        self._boundsEditor = BoundsEditor()
        self._boundsEditor.positionChanged.connect(self.setPos)
        self._boundsEditor.sizeChanged.connect(self.setFixedBounds)
        self._fixedBounds = QSizeF()
        self._hasSelection = False
        self.document().undoAvailable.connect(self.undoAvailable)
        self.document().redoAvailable.connect(self.redoAvailable)


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

    def undo(self):
        self.document().undo()

    def redo(self):
        self.document().redo()

    def isUndoAvailable(self):
        return self.document().isUndoAvailable()

    def isRedoAvailable(self):
        return self.document().isRedoAvailable()

    def copy(self):
        print("item.copy", self.scene())
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_C, Qt.ControlModifier)
        QApplication.sendEvent(self.scene(), event)

    def cut(self):
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_X, Qt.ControlModifier)
        QApplication.sendEvent(self.scene(), event)

    def paste(self):
        print("item.paste")
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_P, Qt.ControlModifier)
        QApplication.sendEvent(self.scene(), event)

    def _updateSelection(self, selected):
        self.prepareGeometryChange()

    def boundingRect(self):
        textBoundingRect = self.textBoundingRect()
        if not self.isSelected():
            return textBoundingRect

        return self._boundsEditor.boundingRect(textBoundingRect)

    def textBoundingRect(self):
        if self._fixedBounds.isEmpty():
            return super(TextItem, self).boundingRect()
        return QRectF(QPointF(0.0, 0.0), self._fixedBounds)

    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
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

    def mergeFormatOnWordOrSelection(self, format):
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)

        cursor.mergeCharFormat(format)
        #self.textEdit.mergeCurrentCharFormat(format)

    def setBlockFormatOnCurrentBlock(self, blockFormat):
        self.textCursor().setBlockFormat(blockFormat)

    def hoverEnterEvent(self, event):
        if not self._boundsEditor.belongsToSelection(event.pos(), self.textBoundingRect()):
            self.setCursor(Qt.IBeamCursor)
            return

        cursorType = self._boundsEditor.getCursorByPosition(event.pos(), self.textBoundingRect())

        if cursorType:
            self.setCursor(cursorType)

    def hoverMoveEvent(self, event):

        if not self._boundsEditor.belongsToSelection(event.pos(), self.textBoundingRect()):
            self.setCursor(Qt.IBeamCursor)
            return

        cursorType = self._boundsEditor.getCursorByPosition(event.pos(), self.textBoundingRect())

        if cursorType:
            self.setCursor(cursorType)

    def mouseReleaseEvent(self, event):
        self._boundsEditor.mouseRelease()
        if not self._boundsEditor.belongsToSelection(event.pos(), self.textBoundingRect()):
            super(TextItem, self).mouseReleaseEvent(event)
            self._updateCursorPosition(self.textCursor())
            return
        self.setSelected(True)

    def mouseMoveEvent(self, event):
        if not self._boundsEditor.hasCurrentMouseOperation():
            return super(TextItem, self).mouseMoveEvent(event)

        self._boundsEditor.mouseMove(self.pos(), event, self.textBoundingRect())

    def mousePressEvent(self, event):
        if not self._boundsEditor.belongsToSelection(event.pos(), self.textBoundingRect()):
            super(TextItem, self).mousePressEvent(event)
            return
        self._boundsEditor.mousePress(event, self.textBoundingRect())
        super(TextItem, self).mousePressEvent(event)

    def keyReleaseEvent(self, event):
        super(TextItem, self).keyReleaseEvent(event)
        self._updateCursorPosition(self.textCursor())

    def currentCharFormat(self):
        return self.textCursor().charFormat()

    def currentBlockFormat(self):
        return self.textCursor().blockFormat()

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

        self._boundsEditor.paintSelection(painter, self.textBoundingRect())

    def cursorHasSelection(self):
        return self._hasSelection

    def _setCursorHasSelection(self, has):
        if self._hasSelection == has:
            return
        self._hasSelection = has
        self.hasSelectionChanged.emit(has)

    def _updateStyle(self, cursor):
        currentCharFormat = cursor.charFormat()
        currentBlockFormat = cursor.blockFormat()
        if self._lastCharFormat != currentCharFormat:
            self._lastCharFormat = currentCharFormat
            self.currentCharFormatChanged.emit(currentCharFormat)
        if self._lastBlockFormat != currentBlockFormat:
            self._lastBlockFormat = currentBlockFormat
            self.currentBlockFormatChanged.emit(currentBlockFormat)


    def _updateCursorPosition(self, cursor):
        if self._lastCursorPosition == cursor.position():
            return
        self._lastCursorPosition = cursor.position()
        self.cursorPositionChanged[QTextCursor].emit(cursor)
        self.cursorPositionChanged[int].emit(self._lastCursorPosition)
        self._setCursorHasSelection(cursor.hasSelection())