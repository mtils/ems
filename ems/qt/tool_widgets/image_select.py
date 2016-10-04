
from six import text_type

from ems.qt import QtWidgets, QtCore, QtGui
from ems.qt.tool_widgets.filesystem_inputs import FileInput
#from ems.qt5.util import QError


pyqtSignal = QtCore.pyqtSignal
pyqtProperty = QtCore.pyqtProperty
Qt = QtCore.Qt
QPainter = QtGui.QPainter
QWidget = QtWidgets.QWidget
QPushButton = QtWidgets.QPushButton
QColorDialog = QtWidgets.QColorDialog
QColor = QtGui.QColor
QMargins = QtCore.QMargins
QRect = QtCore.QRect
QRectF = QtCore.QRectF
QHBoxLayout = QtWidgets.QHBoxLayout
QVBoxLayout = QtWidgets.QVBoxLayout
QLineEdit = QtWidgets.QLineEdit
QLabel = QtWidgets.QLabel
QFrame = QtWidgets.QFrame
QPixmap = QtGui.QPixmap
QFileDialog = QtWidgets.QFileDialog
QImageReader = QtGui.QImageReader


class _ImageLabel(QFrame):

    clicked = pyqtSignal()

    def __init__(self, parent):
        super(_ImageLabel, self).__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        #self.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.setFrameShape(QLabel.StyledPanel)
        self.setFrameShadow(QLabel.Sunken)
        self.setLineWidth(2)
        self.setMidLineWidth(1)
        self._pixmap = None

    def getPixmap(self):
        return self._pixmap

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self.repaint()

    def resizeEvent(self, event):
        super(_ImageLabel, self).resizeEvent(event)

    def paintEvent(self, event):

        super(_ImageLabel, self).paintEvent(event)
        painter = QPainter(self)
        if not self._pixmap or self._pixmap.isNull():
            return

        rect = self.contentsRect()

        pixmap = self._pixmap.scaled(rect.size(), Qt.KeepAspectRatio)
        pixmapSize = pixmap.size()
        targetRect = QRectF(
            float(rect.center().x()) - float(pixmapSize.width()/2) + 1.0,
            float(rect.center().y()) - float(pixmapSize.height()/2)+ 1.0,
            float(pixmapSize.width()),
            float(pixmapSize.height())
        )

        painter.drawPixmap(targetRect, pixmap, QRectF(pixmap.rect()))

    def mouseReleaseEvent(self, event):
        super(_ImageLabel, self).mouseReleaseEvent(event)
        self.clicked.emit()

    def enterEvent(self, event):
        super(_ImageLabel, self).enterEvent(event)
        self.setFrameShadow(QLabel.Raised)

    def leaveEvent(self, event):
        super(_ImageLabel, self).leaveEvent(event)
        self.setFrameShadow(QLabel.Sunken)

class ImageSelect(QFrame):

    pathChanged = pyqtSignal(text_type)

    pixmapChanged = pyqtSignal(QPixmap)

    def __init__(self, parent=None, color=None):
        super(ImageSelect, self).__init__(parent)
        color = QColor(0,0,0) if color is None else color
        self._color = color
        self._margins = QMargins(15,10,15,10)
        self._fileDialog = None
        self._setupUi()
        self._noImagePixmap = QPixmap()
        self._imageFormats = None
        self._pixmap = None
        self._path = None
        self.pathChanged.connect(self._updatePixmap)


    def getPath(self):
        return self.pathInput.getPath()

    def setPath(self, path):
        return self.pathInput.setPath(path)

    path = pyqtProperty(text_type, getPath, setPath, notify=pathChanged)

    def pickFile(self):
        self._configureFileDialog(self.fileDialog)
        self.fileDialog.show()

    @property
    def fileDialog(self):
        if not self._fileDialog:
            self._fileDialog = self._createFileDialog()
        return self._fileDialog

    def getImageFormats(self):
        if self._imageFormats is not None:
            return self._imageFormats
        self._imageFormats = [text_type(t) for t in QImageReader.supportedImageFormats()]
        return self._imageFormats

    def setImageFormats(self, formats):
        self._imageFormats = formats

    imageFormats = pyqtProperty(list, getImageFormats, setImageFormats)

    def _createFileDialog(self):
        fileDialog= QFileDialog(parent=self.window())
        fileDialog.fileSelected.connect(self.setPath)
        return fileDialog

    def _configureFileDialog(self, fileDialog):
        fileDialog.setFileMode(QFileDialog.ExistingFile)
        filterString = ' '.join(["*.{0}".format(f) for f in self.imageFormats])
        fileDialog.setNameFilter(u"{0} ({1})".format(self.tr('Image Files'), filterString))

    def _setupUi(self):
        self.setLayout(QVBoxLayout())
        self.imageLabel = _ImageLabel(self)
        self.imageLabel.setFixedHeight(150)
        self.pixmapChanged.connect(self.imageLabel.setPixmap)
        self.pathInput = FileInput(self)
        self.pathInput.pathChanged.connect(self.pathChanged)
        self.layout().addWidget(self.imageLabel)
        self.layout().addWidget(self.pathInput)

        self.imageLabel.clicked.connect(self.pickFile)

    def _updatePixmap(self, *args):
        self._pixmap = QPixmap(self.getPath())
        self.pixmapChanged.emit(self._pixmap)
