
from six import text_type
from ems.qt import QtCore, QtGui, QtWidgets
from ems.qt.graphics.tool import GraphicsTool
from ems.qt.richtext.inline_edit_graphicsitem import TextItem

Qt = QtCore.Qt
QPointF = QtCore.QPointF
QAction = QtWidgets.QAction
QTextCharFormat = QtGui.QTextCharFormat
QTextBlockFormat = QtGui.QTextBlockFormat
pyqtSignal = QtCore.pyqtSignal
QIcon = QtGui.QIcon
QSizeF = QtCore.QSizeF

class TextTool(GraphicsTool):

    currentCharFormatChanged = pyqtSignal(QTextCharFormat)

    currentBlockFormatChanged = pyqtSignal(QTextBlockFormat)

    undoAvailable = pyqtSignal(bool)

    redoAvailable = pyqtSignal(bool)

    copyAvailable = pyqtSignal(bool)

    def __init__(self, parent=None, resourcePath=':/ImageEditor/icons'):

        super(TextTool, self).__init__(parent)

        self.resourcePath = resourcePath
        self.addTextItem = QAction(self.icon('frame_text.png'), "Add Text Box", self)
        self.addTextItem.setCheckable(True)
        self.addTextItem.triggered.connect(self.requestViewForTextPosition)
        self._actions.append(self.addTextItem)
        self._currentItem = None


    def requestViewForTextPosition(self):
        self.getPointAnd(self.addItemAt)

    def addItemAt(self, point):
        textItem = TextItem('Neuer Text', point)
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
        self._currentItem.undoAvailable.connect(self.undoAvailable)
        self._currentItem.redoAvailable.connect(self.redoAvailable)
        self._currentItem.hasSelectionChanged.connect(self.copyAvailable)
        self.currentCharFormatChanged.emit(self._currentItem.currentCharFormat())
        self.currentBlockFormatChanged.emit(self._currentItem.currentBlockFormat())
        self.undoAvailable.emit(self._currentItem.isUndoAvailable())
        self.redoAvailable.emit(self._currentItem.isRedoAvailable())
        self.copyAvailable.emit(self._currentItem.cursorHasSelection())

    def resetCurrentItem(self):
        self._disconnectUnselectedItems()
        self._currentItem = None
        self.currentCharFormatChanged.emit(QTextCharFormat())
        self.currentBlockFormatChanged.emit(QTextBlockFormat())
        self.undoAvailable.emit(False)
        self.redoAvailable.emit(False)

    def mergeFormatOnWordOrSelection(self, charFormat):
        if self._currentItem:
            self._currentItem.mergeFormatOnWordOrSelection(charFormat)

    def setBlockFormatOnCurrentBlock(self, blockFormat):
        if self._currentItem:
            self._currentItem.setBlockFormatOnCurrentBlock(blockFormat)

    def undo(self):
        if self._currentItem:
            self._currentItem.undo()

    def redo(self):
        if self._currentItem:
            self._currentItem.redo()

    def copy(self):
        print('copy', self._currentItem)
        if self._currentItem:
            self._currentItem.copy()

    def cut(self):
        if self._currentItem:
            self._currentItem.cut()

    def paste(self):
        print('paste', self._currentItem)
        if self._currentItem:
            self._currentItem.paste()

    def imagePath(self, fileName):
        return "{}/{}".format(self.resourcePath, fileName)

    def icon(self, fileName):
        return QIcon(self.imagePath(fileName))

    def canSerialize(self, item):
        return isinstance(item, TextItem)

    def canDeserialize(self, itemData):
        return (itemData['type'] == 'text-item')

    def serialize(self, item):
        fixedBounds = item.fixedBounds
        fixedBoundsList = {'width':fixedBounds.width(),
                           'height':fixedBounds.height()}
        return {
            'type': 'text-item',
            'position': [item.pos().x(), item.pos().y()],
            'fixedBounds': fixedBoundsList,
            'html': text_type(item.toHtml())
        }

    def deserialize(self, itemData):

        if itemData['type'] != 'text-item':
            return

        pos = QPointF(itemData['position'][0], itemData['position'][1])
        textItem = TextItem('', pos)
        textItem.setHtml(itemData['html'])
        textItem.setFixedBounds(QSizeF(itemData['fixedBounds']['width'],itemData['fixedBounds']['height']))

        return textItem

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