
import base64
try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

from six import text_type, PY3, PY2
from ems.qt import QtCore, QtGui, QtWidgets
from ems.qt.graphics.tool import GraphicsTool, ToolAction
from ems.qt.richtext.inline_edit_graphicsitem import TextItem
from ems.qt.graphics.pixmap_item import PixmapItem

Qt = QtCore.Qt
QByteArray = QtCore.QByteArray
QBuffer = QtCore.QBuffer
QIODevice = QtCore.QIODevice
QPointF = QtCore.QPointF
QAction = QtWidgets.QAction
QTextCharFormat = QtGui.QTextCharFormat
QTextBlockFormat = QtGui.QTextBlockFormat
pyqtSignal = QtCore.pyqtSignal
QIcon = QtGui.QIcon
QSizeF = QtCore.QSizeF
QFileDialog = QtWidgets.QFileDialog
QPixmap = QtGui.QPixmap

class PixmapTool(GraphicsTool):

    def __init__(self, parent=None, resourcePath=':/ImageEditor/icons'):

        super(PixmapTool, self).__init__(parent)

        self.resourcePath = resourcePath
        self.addPixmapItem = ToolAction(self.icon('frame_image.png'), "Add Image", self)
        self.addPixmapItem.setCheckable(False)
        self.addPixmapItem.triggered.connect(self.requestFileName)
        self._actions.append(self.addPixmapItem)
        self._currentItem = None

    def requestFileName(self):

        fileName = QFileDialog.getOpenFileName(self.view, 'Open Image File', '',
                                               'Image Files (*.jpg *.jpeg *.png)')
        if not fileName:
            return

        if isinstance(fileName, tuple):
            fileName = fileName[0]

        targetPoint = self.view.lastReleasedPoint()

        if not targetPoint:
            targetPoint = QPointF(80.0, 80.0)

        self.addItemAt(targetPoint, fileName)

        #self.getPointAnd(self.addItemAt, fileName=fileName)

    def requestViewForTextPosition(self):
        self.getPointAnd(self.addItemAt)

    def addItemAt(self, point, fileName):

        pixmap = QPixmap(fileName)

        item = PixmapItem()
        item.setPixmapPath(fileName)
        size = item.size()
        item.setPos(point)

        sceneRect = self.scene.sceneRect()

        if size.width() > sceneRect.width() or size.height() > sceneRect.height():
            item.setSize(QSizeF(sceneRect.width()-50, sceneRect.height()-50))

        self.scene.clearSelection()
        self.scene.addItem(item)
        item.setSelected(True)
        return

    def canHandle(self, item):
        return isinstance(item, TextItem)

    def setCurrentItem(self, item):
        self._currentItem = item
        return

    def resetCurrentItem(self):
        self._currentItem = None

    def mergeFormatOnWordOrSelection(self, charFormat):
        if self._currentItem:
            self._currentItem.mergeFormatOnWordOrSelection(charFormat)

    def setBlockFormatOnCurrentBlock(self, blockFormat):
        if self._currentItem:
            self._currentItem.setBlockFormatOnCurrentBlock(blockFormat)

    def imagePath(self, fileName):
        return "{}/{}".format(self.resourcePath, fileName)

    def icon(self, fileName):
        return QIcon(self.imagePath(fileName))

    def canSerialize(self, item):
        return isinstance(item, PixmapItem)

    def canDeserialize(self, itemData):
        return (itemData['type'] == 'pixmap-item')

    def serialize(self, item):
        size = item.size()
        sizeDict = {'width':size.width(),
                    'height':size.height()}

        bArray = QByteArray()
        buffer = QBuffer(bArray)
        buffer.open(QIODevice.WriteOnly)
        item.pixmap().save(buffer, 'PNG')
        if PY2:
            sio = StringIO(bArray)
        else:
            sio = StringIO(bytes(bArray))
        sio.seek(0)
        imgData = sio.getvalue()

        if PY2:
            encoded = base64.b64encode(imgData)
        else:
            encoded = base64.b64encode(imgData).decode('ascii')


        return {
            'type': 'pixmap-item',
            'position': [item.pos().x(), item.pos().y()],
            'size': sizeDict,
            'data': encoded,
            'path': text_type(item.pixmapPath())
        }

    def deserialize(self, itemData):

        if itemData['type'] != 'pixmap-item':
            return

        pos = QPointF(itemData['position'][0], itemData['position'][1])
        item = PixmapItem()
        item.setPos(pos)
        pixmap = QPixmap()
        pixmap.loadFromData(base64.decodestring(itemData['data'].encode('ascii')))
        item.setPixmap(pixmap)
        item.setSize(QSizeF(itemData['size']['width'],itemData['size']['height']))

        return item

    def _disconnectUnselectedItems(self):
        for item in self.scene.items():
            if not isinstance(item, TextItem):
                continue
            try:
                item.currentCharFormatChanged.disconnect(self.currentCharFormatChanged)
            except TypeError:
                pass
            try:
                item.currentBlockFormatChanged.disconnect(self.currentBlockFormatChanged)
            except TypeError:
                pass
            try:
                item.undoAvailable.disconnect(self.undoAvailable)
            except TypeError:
                pass
            try:
                item.redoAvailable.disconnect(self.redoAvailable)
            except TypeError:
                pass
            try:
                item.hasSelectionChanged.disconnect(self.copyAvailable)
            except TypeError:
                pass