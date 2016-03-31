
from ems.qt import QtWidgets, QtCore, QtGui
from ems.qt.richtext.char_format_proxy import CharFormatProxy
from ems.qt.richtext.block_format_proxy import BlockFormatProxy

Qt = QtCore.Qt
QObject = QtCore.QObject
QColor = QtGui.QColor
QAction = QtWidgets.QAction
QKeySequence = QtGui.QKeySequence
QFont = QtGui.QFont
QIcon = QtGui.QIcon
QPixmap = QtGui.QPixmap
ThemeIcon = QIcon.fromTheme
QApplication = QtWidgets.QApplication
QColorDialog = QtWidgets.QColorDialog
QFontComboBox = QtWidgets.QFontComboBox
QComboBox = QtWidgets.QComboBox
QFontDatabase = QtGui.QFontDatabase
QTextDocument = QtGui.QTextDocument
QTextCharFormat = QtGui.QTextCharFormat
pyqtSignal = QtCore.pyqtSignal
pyqtSlot = QtCore.pyqtSlot
pyqtProperty = QtCore.pyqtProperty
QActionGroup = QtWidgets.QActionGroup

class BlockFormatActions(QObject):

    documentChanged = pyqtSignal(QTextDocument)
    currentBlockFormatChanged = pyqtSignal(QTextCharFormat)

    def __init__(self, parentWidget, signalProxy=None, resourcePath=':/text-editor'):
        super(BlockFormatActions, self).__init__(parentWidget)
        self.resourcePath = resourcePath
        self.actions = []
        self.widgets = []
        self.signals = BlockFormatProxy(self) if signalProxy is None else signalProxy
        self._addActions(self.parent())
        self._document = QTextDocument()

    def getDocument(self):
        return self._document

    @pyqtSlot(QTextDocument)
    def setDocument(self, document):
        if self._document is document:
            return
        if self._document:
            self._disconnectFromDocument(self._document)
        self._document = document
        self.documentChanged.emit(self._document)

    document = pyqtProperty(QTextDocument, getDocument, setDocument)

    def _disconnectFromDocument(self, document):
        return

    def _addActions(self, parent):

        self.actionAlignLeft = QAction(
                ThemeIcon('format-justify-left', self._icon('align-left.png')),
                "&Left", parent, triggered=self.signals.setAlignLeft)

        self.signals.alignLeftChanged.connect(self.actionAlignLeft.setChecked)

        self.actionAlignCenter = QAction(
                ThemeIcon('format-justify-center',self._icon('align-center.png')),
                "C&enter", parent, triggered=self.signals.setAlignCenter)

        self.signals.alignCenterChanged.connect(self.actionAlignCenter.setChecked)

        self.actionAlignRight = QAction(
                ThemeIcon('format-justify-right', self._icon('align-right.png')),
                "&Right", parent, triggered=self.signals.setAlignRight)

        self.signals.alignRightChanged.connect(self.actionAlignRight.setChecked)

        self.actionAlignJustify = QAction(
                ThemeIcon('format-justify-fill',self._icon('align-justify.png')),
                "&Justify", parent, triggered=self.signals.setAlignJustify)

        self.signals.alignJustifyChanged.connect(self.actionAlignJustify.setChecked)

        grp = QActionGroup(parent)

        if QApplication.isLeftToRight():
            grp.addAction(self.actionAlignLeft)
            grp.addAction(self.actionAlignCenter)
            grp.addAction(self.actionAlignRight)
        else:
            grp.addAction(self.actionAlignRight)
            grp.addAction(self.actionAlignCenter)
            grp.addAction(self.actionAlignLeft)

        grp.addAction(self.actionAlignJustify)

        self.actionAlignLeft.setShortcut(Qt.CTRL + Qt.Key_L)
        self.actionAlignCenter.setShortcut(Qt.CTRL + Qt.Key_E)
        self.actionAlignRight.setShortcut(Qt.CTRL + Qt.Key_R)
        self.actionAlignJustify.setShortcut(Qt.CTRL + Qt.Key_J)

        for action in grp.actions():
            action.setCheckable(True)
            action.setPriority(QAction.LowPriority)
            self.actions.append(action)

    def addToToolbar(self, toolbar, addActions=True, addWidgets=True):
        if addActions:
            for action in self.actions:
                toolbar.addAction(action)

        if not addWidgets:
            return
        for widget in self.widgets:
            widget.setParent(toolbar)
            toolbar.addWidget(widget)

    def iconPath(self, fileName):
        return self.resourcePath + '/' + fileName

    def _icon(self, fileName):
        return QIcon(self.iconPath(fileName))