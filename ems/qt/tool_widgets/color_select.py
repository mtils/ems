
from six import text_type

from ems.qt import QtWidgets, QtCore, QtGui
from ems.qt5.util import QError


pyqtSignal = QtCore.pyqtSignal
pyqtProperty = QtCore.pyqtProperty
QPainter = QtGui.QPainter
QPushButton = QtWidgets.QPushButton
QColorDialog = QtWidgets.QColorDialog
QColor = QtGui.QColor
QMargins = QtCore.QMargins
QRect = QtCore.QRect

class ColorSelect(QPushButton):

    colorChanged = pyqtSignal(QColor)

    colorStringChanged = pyqtSignal(text_type)

    def __init__(self, parent=None, color=None):
        super(ColorSelect, self).__init__(parent)
        color = QColor(0,0,0) if color is None else color
        self._color = color
        self._margins = QMargins(15,10,15,10)
        self._colorDialog = None
        self.clicked.connect(self.pickColor)

    def getColor(self):
        return self._color

    def setColor(self, color):
        if self._color == color:
            return
        self._color = color
        self.colorChanged.emit(self._color)
        self.colorStringChanged.emit(self._color.name())
        self.repaint()

    color = pyqtProperty(QColor, getColor, setColor, notify=colorChanged)

    def getColorString(self):
        return self._color.name()

    def setColorString(self, colorString):
        if colorString == self.getColorString():
            return
        self.setColor(QColor(colorString))

    colorString = pyqtProperty(text_type, getColorString, setColorString, notify=colorStringChanged)

    def paintEvent(self, event):
        super(ColorSelect, self).paintEvent(event)
        painter = QPainter(self)

        rect = event.rect()
        coloredRect = QRect(
            rect.topLeft().x() + self._margins.left(),
            rect.topLeft().y() + self._margins.top(),
            rect.width() - self._margins.left() - self._margins.right(),
            rect.height() - self._margins.top() - self._margins.bottom()
        )

        painter.fillRect(coloredRect, self._color)

    def pickColor(self):
        if self._colorDialog is None:
            self._colorDialog = self._createColorDialog()

        self._colorDialog.show()

    def _createColorDialog(self):
        dialog = QColorDialog(self.window())
        dialog.setCurrentColor(self._color)
        dialog.currentColorChanged.connect(self.setColor)
        self.colorChanged.connect(dialog.setCurrentColor)
        return dialog