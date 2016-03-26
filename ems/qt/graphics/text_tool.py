
from ems.qt import QtCore, QtGui, QtWidgets
from ems.qt.graphics.tool import GraphicsTool
from ems.qt.richtext.inline_edit_graphicsitem import TextItem

QAction = QtWidgets.QAction
QTextCharFormat = QtGui.QTextCharFormat
pyqtSignal = QtCore.pyqtSignal
QResource = QtCore.QResource
QIcon = QtGui.QIcon

class TextTool(GraphicsTool):

    currentCharFormatChanged = pyqtSignal(QTextCharFormat)

    def __init__(self, parent=None, resourcePath=':/ImageEditor/icons'):

        super(TextTool, self).__init__(parent)

        self.resourcePath = resourcePath
        self.addTextItem = QAction(self.icon('frame_text.png'), "Add Text Box", self)
        self.addTextItem.setCheckable(True)
        self._actions.append(self.addTextItem)
        self._currentItem = None


    def addItemAt(self, point):
        textItem = TextItem('Neuer Text', point, self.scene )
        self.scene.clearSelection()
        self.scene.addItem(textItem)
        textItem.setSelected(True)
        self.itemAdded.emit()
        #print("emptyAreaClicked", point, self.scene)

    def canHandle(self, item):
        return isinstance(item, TextItem)

    def setCurrentItem(self, item):
        self._currentItem = item
        self._currentItem.currentCharFormatChanged.connect(self.currentCharFormatChanged)
        self.currentCharFormatChanged.emit(self._currentItem.currentCharFormat())

    def resetCurrentItem(self):
        self._disconnectUnselectedItems()
        self._currentItem = None
        self.currentCharFormatChanged.emit(QTextCharFormat())

    def mergeFormatOnWordOrSelection(self, charFormat):
        if not self._currentItem:
            return
        self._currentItem.mergeFormatOnWordOrSelection(charFormat)

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