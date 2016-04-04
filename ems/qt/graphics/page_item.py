
from ems.qt import QtCore, QtGui, QtWidgets, QtPrintSupport
from ems.qt.graphics.interfaces import Finalizer

Qt = QtCore.Qt
QGraphicsObject = QtWidgets.QGraphicsObject
pyqtSignal = QtCore.pyqtSignal
pyqtProperty = QtCore.pyqtProperty
QRectF = QtCore.QRectF
QPointF = QtCore.QPointF
QMargins = QtCore.QMargins
QPrinter = QtPrintSupport.QPrinter
QColor = QtGui.QColor
QPen = QtGui.QPen
QBrush = QtGui.QBrush

class PageItemHider(Finalizer):

    def toFinalized(self, scene):
        for item in scene.items():
            if isinstance(item, PageItem):
                item.setVisible(False)


    def toEditable(self, scene):
        for item in scene.items():
            if isinstance(item, PageItem):
                item.setVisible(True)

class Margins(object):

    def __init__(self, left=0.0, top=0.0, right=0.0, bottom=0.0):
        self._left = left
        self._top = top
        self._right = right
        self._bottom = bottom

    def left(self):
        return self._left

    def setLeft(self, left):
        self._left = left

    def top(self):
        return self._top

    def setTop(self, top):
        self._top = top

    def right(self):
        return self._right

    def setRight(self, right):
        self._right = right

    def bottom(self):
        return self._bottom

    def setBottom(self, bottom):
        self._bottom = bottom

    def isNull(self):
        return (self._left == 0.0
            and self._top == 0.0
            and self._right == 0.0
            and self._bottom == 0.0)

    def toMargins(self):
        return QMargins(int(self._left), int(self._top), int(self._right), int(self._bottom))

    def __eq__(self, other):
        if other.left() != self._left:
            return False
        if other.top() != self._top:
            return False
        if other.right() != self._right:
            return False
        if other.bottom() != self._bottom:
            return False
        return True

class PageItem(QGraphicsObject):

    paperRectChanged = pyqtSignal(QRectF)

    printerRectChanged = pyqtSignal(QRectF)

    pageRectChanged = pyqtSignal(QRectF)

    marginsChanged = pyqtSignal(Margins)

    paperFormatChanged = pyqtSignal(int)

    def __init__(self):
        super(PageItem, self).__init__()
        self._paperRect = QRectF(0.0, 0.0, 594.75, 842.25) #A4
        self._pageRect = QRectF()
        self._printerRect = QRectF(24.0, 24.0, 546.75, 794.25)
        self._margins = Margins()
        self._paperFormat = QPrinter.A4
        self._printer = None
        self._printerRectColor = QColor(187, 187, 187)
        self._printerRectPenStyle = Qt.DotLine
        self._pageRectColor = self._printerRectColor
        self._pageRectPenStyle = Qt.SolidLine
        self._marginRectColor = self._pageRectColor
        self._pageColor = QColor(255, 255, 255)
        self.setMargins(Margins(2.0, 2.0, 2.0, 2.0))

    def boundingRect(self):
        return self._pageRect

    def getPaperRect(self):
        return self._paperRect

    paperRect = pyqtProperty(QRectF, getPaperRect, notify=paperRectChanged)

    def getPrinterRect(self):
        return self._printerRect

    printerRect = pyqtProperty(QRectF, getPrinterRect, notify=printerRectChanged)

    def setPrinterRect(self, printerRect):
        if self._printerRect == printerRect:
            return
        self._printerRect = printerRect
        self.printerRectChanged.emit(self._printerRect)
        self._setPageRect(self._calculatePageRect(self._printerRect, self._margins))

    def getPageRect(self):
        return self._pageRect

    pageRect = pyqtProperty(QRectF, getPageRect, notify=pageRectChanged)

    def _setPageRect(self, pageRect):
        if self._pageRect == pageRect:
            return
        self._pageRect = pageRect
        self.pageRectChanged.emit(self._pageRect)

    def getMargins(self):
        return self._margins

    def setMargins(self, margins):
        if self._margins == margins:
            return
        self._margins = margins
        self.marginsChanged.emit(self._margins)
        self._setPageRect(self._calculatePageRect(self._printerRect, self._margins))

    margins = pyqtProperty(Margins, getMargins, setMargins)

    def getPaperFormat(self):
        return self._paperFormat

    def setPaperFormat(self, paperFormat):
        if self._paperFormat == paperFormat:
            return
        self._paperFormat = paperFormat
        self.paperFormatChanged.emit(self._paperFormat)

    paperFormat = pyqtProperty(int, getPaperFormat, setPaperFormat, notify=paperFormatChanged)

    def getPrinter(self):
        return self._printer

    def setPrinter(self, printer):
        self._printer = printer

    def paint(self, painter, option, widget=None):

        oldBrush = painter.brush()
        brush = QBrush(self._pageColor, Qt.SolidPattern)
        painter.setBrush(brush)

        painter.drawRect(self.paperRect)

        painter.setBrush(oldBrush)

        pen = QPen(self._printerRectPenStyle)
        pen.setColor(self._printerRectColor)
        pen.setWidthF(1.0)
        painter.setPen(pen)

        painter.drawRect(self.printerRect)

        pen = QPen(self._pageRectPenStyle)
        pen.setColor(self._pageRectColor)
        pen.setWidthF(1.0)

        painter.setPen(pen)

        painter.drawRect(self.pageRect)

    def _calculatePageRect(self, paperRect, margins):
        paperTopLeft = paperRect.topLeft()
        paperBottomRight = paperRect.bottomRight()

        pageTopLeft = QPointF(paperTopLeft.x()+margins.left(),
                              paperTopLeft.y()+margins.top())
        pageBottomRight = QPointF(paperBottomRight.x()-margins.right(),
                                  paperBottomRight.y()-margins.bottom())

        return QRectF(pageTopLeft, pageBottomRight)