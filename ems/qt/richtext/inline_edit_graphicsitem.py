
from ems.qt import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt
pyqtSignal = QtCore.pyqtSignal
QGraphicsItem = QtWidgets.QGraphicsItem
QGraphicsTextItem = QtWidgets.QGraphicsTextItem
QFont = QtGui.QFont
QTransform = QtGui.QTransform
QTextCursor = QtGui.QTextCursor
QTextCharFormat = QtGui.QTextCharFormat
QStyle = QtWidgets.QStyle
QBrush = QtGui.QBrush
QColor = QtGui.QColor

class TextItem(QGraphicsTextItem):

    cursorPositionChanged = pyqtSignal([QTextCursor],[int])

    currentCharFormatChanged = pyqtSignal(QTextCharFormat)

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
        #scene.clearSelection()
        #scene.addItem(self)
        #self.setSelected(True)
        self.setTextInteractionFlags(Qt.TextEditable | Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.cursorPositionChanged[QTextCursor].connect(self._updateStyle)


    def parentWidget(self):
        return self.scene().views()[0]


    def itemChange(self, change, variant):
        if change != QGraphicsItem.ItemSelectedChange:
            Dirty = True
        return QGraphicsTextItem.itemChange(self, change, variant)

    def mergeFormatOnWordOrSelection(self, format):
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)

        cursor.mergeCharFormat(format)
        #self.textEdit.mergeCurrentCharFormat(format)

    def mouseDoubleClickEvent_(self, event):
        dialog = TextItemDlg(self, self.parentWidget())
        dialog.exec_()

    def hoverEnterEvent(self, event):
        #print "HoverEnter"
        #print event.pos()
        #print self.boundingRect()
        self.setCursor(Qt.IBeamCursor)
        QGraphicsTextItem.hoverEnterEvent(self, event)

    def hoverLeaveEvent(self, event):
        #print "HoverLeave"
        QGraphicsTextItem.hoverLeaveEvent(self, event)

    def mouseReleaseEvent(self, event):
        super(TextItem, self).mouseReleaseEvent(event)
        self._updateCursorPosition(self.textCursor())
        self.setSelected(True)

    def keyReleaseEvent(self, event):
        super(TextItem, self).keyReleaseEvent(event)
        self._updateCursorPosition(self.textCursor())

    def currentCharFormat(self):
        return self.textCursor().charFormat()

    def paint(self, painter, option, widget=None):
        super(TextItem, self).paint(painter, option, widget)

        if not (option.state & QStyle.State_Selected):
            return

        rect = self.boundingRect()

        w = rect.width()
        h = rect.height()
        s = 4
        brush = QBrush(QColor(128,179,255))
        painter.fillRect(0, 0, s,  s, brush);
        painter.fillRect(0, 0 + h - s, s, s, brush);
        painter.fillRect(0 + w - s, 0, s, s, brush);

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