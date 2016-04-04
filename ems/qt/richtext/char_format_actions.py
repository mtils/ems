
from ems.qt import QtWidgets, QtCore, QtGui
from ems.qt.richtext.char_format_proxy import CharFormatProxy

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

class CharFormatActions(QObject):

    documentChanged = pyqtSignal(QTextDocument)
    currentBlockFormatChanged = pyqtSignal(QTextCharFormat)

    def __init__(self, parentWidget, signalProxy=None, resourcePath=':/text-editor'):
        super(CharFormatActions, self).__init__(parentWidget)
        self.resourcePath = resourcePath
        self.actions = []
        self.widgets = []
        self.signals = CharFormatProxy(self) if signalProxy is None else signalProxy
        self._addActions(self.parent())
        self._document = QTextDocument()
        self._lastBlockFormat = None

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

        self.actionTextBold = QAction(
                ThemeIcon('format-text-bold', self._icon('bold.png')),
                "&Bold", parent, priority=QAction.LowPriority,
                shortcut=Qt.CTRL + Qt.Key_B,
                triggered=self.signals.setBold, checkable=True)
        bold = QFont()
        bold.setBold(True)
        self.actionTextBold.setFont(bold)

        self.signals.boldChanged.connect(self.actionTextBold.setChecked)

        self.actions.append(self.actionTextBold)


        self.actionTextItalic = QAction(
                ThemeIcon('format-text-italic', self._icon('italic.png')),
                "&Italic", self, priority=QAction.LowPriority,
                shortcut=Qt.CTRL + Qt.Key_I,
                triggered=self.signals.setItalic, checkable=True)
        italic = QFont()
        italic.setItalic(True)
        self.actionTextItalic.setFont(italic)

        self.signals.italicChanged.connect(self.actionTextItalic.setChecked)

        self.actions.append(self.actionTextItalic)


        self.actionTextUnderline = QAction(
                ThemeIcon('format-text-underline', self._icon('underline.png')),
                "&Underline", self, priority=QAction.LowPriority,
                shortcut=Qt.CTRL + Qt.Key_U,
                triggered=self.signals.setUnderline, checkable=True)
        underline = QFont()
        underline.setUnderline(True)
        self.actionTextUnderline.setFont(underline)

        self.actions.append(self.actionTextUnderline)

        self.signals.underlineChanged.connect(self.actionTextUnderline.setChecked)

        pix = QPixmap(16, 16)
        pix.fill(Qt.black)
        self.actionTextColor = QAction(QIcon(pix), "&Color...",
                self, triggered=self._textColor)

        self.signals.foregroundColorChanged.connect(self._colorChanged)

        self.actions.append(self.actionTextColor)

        self.actionClearFormat = QAction(ThemeIcon('format-text-clear', self._icon('magic.png')),
                                         "&Remove Format", self, priority=QAction.LowPriority,
                                         shortcut=Qt.CTRL + Qt.Key_E,
                                         triggered=self.signals.clearFormat)

        self.actions.append(self.actionClearFormat)

        self.fontCombo = QFontComboBox()
        self.fontCombo.activated[str].connect(self.signals.setFontFamily)

        self.signals.fontFamilyChanged.connect(self.setFontFamily)

        self.widgets.append(self.fontCombo)

        self.sizeCombo = QComboBox()
        self.sizeCombo.setObjectName("sizeCombo")
        self.sizeCombo.setEditable(True)

        self.signals.pointSizeChanged.connect(self.setFontPointSize)

        self.widgets.append(self.sizeCombo)

        db = QFontDatabase()

        for size in db.standardSizes():
            self.sizeCombo.addItem("{}".format(size))

        self.sizeCombo.activated[str].connect(self._textSize)

        self.sizeCombo.setCurrentIndex(
                self.sizeCombo.findText(
                        "{}".format(QApplication.font().pointSize())
                )
        )

    def _textColor(self):
        color = self.signals.getForegroundColor()
        if not color:
            color = QColor(0,0,0)
        col = QColorDialog.getColor(color, self.parent())
        if not col.isValid():
            return

        self.signals.setForegroundColor(col)

    def _colorChanged(self, color):
        pix = QPixmap(16, 16)
        pix.fill(color)
        self.actionTextColor.setIcon(QIcon(pix))

    def _textSize(self, pointSize):
        pointSize = float(pointSize)
        if pointSize < 0:
            return
        self.signals.setPointSize(pointSize)

    def addToToolbar(self, toolbar, addActions=True, addWidgets=True):
        if addActions:
            for action in self.actions:
                toolbar.addAction(action)

        if not addWidgets:
            return
        for widget in self.widgets:
            widget.setParent(toolbar)
            toolbar.addWidget(widget)

    def setFontFamily(self, family):
        self.fontCombo.setCurrentIndex(self.fontCombo.findText(family))

    def setFontPointSize(self, pointSize):
        self.sizeCombo.setCurrentIndex(self.sizeCombo.findText("{}".format(int(pointSize))))

    def iconPath(self, fileName):
        return self.resourcePath + '/' + fileName

    def _icon(self, fileName):
        return QIcon(self.iconPath(fileName))