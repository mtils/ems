
from ems.qt import QtCore, QtGui, QtWidgets
from ems.qt.graphics.tool import GraphicsTool
from ems.qt.richtext.inline_edit_graphicsitem import TextItem

Qt = QtCore.Qt
QAction = QtWidgets.QAction
QTextCharFormat = QtGui.QTextCharFormat
QTextBlockFormat = QtGui.QTextBlockFormat
pyqtSignal = QtCore.pyqtSignal
QResource = QtCore.QResource
QIcon = QtGui.QIcon
QSizeF = QtCore.QSizeF

class TextTool(GraphicsTool):

    currentCharFormatChanged = pyqtSignal(QTextCharFormat)
    currentBlockFormatChanged = pyqtSignal(QTextBlockFormat)

    def __init__(self, parent=None, resourcePath=':/ImageEditor/icons'):

        super(TextTool, self).__init__(parent)

        self.resourcePath = resourcePath
        self.addTextItem = QAction(self.icon('frame_text.png'), "Add Text Box", self)
        self.addTextItem.setCheckable(True)
        self._actions.append(self.addTextItem)
        self._currentItem = None


    def addItemAt(self, point):
        textItem = TextItem('Neuer Text', point, self.scene )
        textItem.setFixedBounds(QSizeF(300,100))
        self.scene.clearSelection()
        self.scene.addItem(textItem)
        textItem.setSelected(True)
        self.itemAdded.emit()

    def canHandle(self, item):
        return isinstance(item, TextItem)

    def setCurrentItem(self, item):
        self._currentItem = item
        self._currentItem.currentCharFormatChanged.connect(self.currentCharFormatChanged)
        self._currentItem.currentBlockFormatChanged.connect(self.currentBlockFormatChanged)
        self.currentCharFormatChanged.emit(self._currentItem.currentCharFormat())
        self.currentBlockFormatChanged.emit(self._currentItem.currentBlockFormat())

    def resetCurrentItem(self):
        self._disconnectUnselectedItems()
        self._currentItem = None
        self.currentCharFormatChanged.emit(QTextCharFormat())
        self.currentBlockFormatChanged.emit(QTextBlockFormat())

    def mergeFormatOnWordOrSelection(self, charFormat):
        if not self._currentItem:
            return
        self._currentItem.mergeFormatOnWordOrSelection(charFormat)

    def setBlockFormatOnCurrentBlock(self, blockFormat):
        if not self._currentItem:
            return
        self._currentItem.setBlockFormatOnCurrentBlock(blockFormat)

    def imagePath(self, fileName):
        return "{}/{}".format(self.resourcePath, fileName)

    def icon(self, fileName):
        return QIcon(self.imagePath(fileName))

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