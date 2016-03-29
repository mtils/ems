#coding=utf-8
'''
Created on 27.08.2011

@author: michi
'''
import sys

from ems.qt import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt
QWidget = QtWidgets.QWidget
QHBoxLayout = QtWidgets.QHBoxLayout
QVBoxLayout = QtWidgets.QVBoxLayout
QSpacerItem = QtWidgets.QSpacerItem
QSizePolicy = QtWidgets.QSizePolicy
QIcon = QtGui.QIcon
QApplication = QtWidgets.QApplication
QToolBar = QtWidgets.QToolBar
QAction = QtWidgets.QAction
QActionGroup = QtWidgets.QActionGroup
QKeySequence = QtGui.QKeySequence
QFont = QtGui.QFont
QPixmap = QtGui.QPixmap
QMessageBox = QtWidgets.QMessageBox
QComboBox = QtWidgets.QComboBox
QFontComboBox = QtWidgets.QFontComboBox
QFontDatabase = QtGui.QFontDatabase
QTextListFormat = QtGui.QTextListFormat
QTextBlockFormat = QtGui.QTextBlockFormat
QColorDialog = QtWidgets.QColorDialog
QTextCursor = QtGui.QTextCursor

from ems.qt4.gui.widgets.completiontextedit import CompletionTextEdit
from ems.qt.richtext.block_format_proxy import BlockFormatProxy
from ems.qt.richtext.char_format_proxy import CharFormatProxy
from ems.qt.edit_actions import EditActions
from ems.qt.richtext.char_format_actions import CharFormatActions
from ems.qt.richtext.block_format_actions import BlockFormatActions


class BaseEditor(QWidget):

    def __init__(self, text=None, parent=None):
        super(BaseEditor, self).__init__(parent)
        self.rsrcPath = ':/textedit'
        self.setWindowIcon(QIcon(':/images/logo.png'))
        self.__currentToolbarIndex = 0
        self.setLayout(QVBoxLayout(self))
        self.layout().setSpacing(0)
        self.signalProxy = CharFormatProxy(self)
        self.blockProxy = BlockFormatProxy(self)

        self.toolBarContainers = []

        self.textEdit = CompletionTextEdit(self)
        self.layout().addWidget(self.textEdit)

        self.setupEditActions()

        self.setupTextActions()

        self.textEdit.currentCharFormatChanged.connect(self.signalProxy.updateCharFormatWithoutDiffs)

        self.signalProxy.charFormatDiffChanged.connect(self.mergeFormatOnWordOrSelection)

        self.blockProxy.blockFormatModified.connect(self.setBlockFormat)


        self.textEdit.cursorPositionChanged.connect(self.cursorPositionChanged)
        #self.setCentralWidget(self.textEdit)
        self.textEdit.setFocus()

        self.signalProxy.setCharFormat(self.textEdit.currentCharFormat())
        self.blockProxy.setBlockFormat(self.textEdit.textCursor().blockFormat())

        self.charFormatActions.setDocument(self.textEdit.document())

#        self.textEdit.document().modificationChanged.connect(
#                self.actionSave.setEnabled)
        self.textEdit.document().modificationChanged.connect(
                self.setWindowModified)
        #self.textEdit.document().undoAvailable.connect(
                #self.editActions.actionUndo.setEnabled)
        self.textEdit.document().redoAvailable.connect(
                self.editActions.actionRedo.setEnabled)
        self.setWindowModified(self.textEdit.document().isModified())
        
        self.editActions.actionUndo.setEnabled(self.textEdit.document().isUndoAvailable())
        self.editActions.actionRedo.setEnabled(self.textEdit.document().isRedoAvailable())
        self.editActions.actionUndo.triggered.connect(self.textEdit.undo)
        self.editActions.actionRedo.triggered.connect(self.textEdit.redo)
        self.editActions.actionCut.setEnabled(False)
        self.editActions.actionCopy.setEnabled(False)
        self.editActions.actionCut.triggered.connect(self.textEdit.cut)
        self.editActions.actionCopy.triggered.connect(self.textEdit.copy)
        self.editActions.actionPaste.triggered.connect(self.textEdit.paste)
        self.textEdit.copyAvailable.connect(self.editActions.actionCut.setEnabled)
        self.textEdit.copyAvailable.connect(self.editActions.actionCopy.setEnabled)
        QApplication.clipboard().dataChanged.connect(
                self.clipboardDataChanged)

        if text:
            self.textEdit.setHtml(text)

    def addToolBar(self, toolbar):
        if len(self.toolBarContainers) <= self.__currentToolbarIndex:
            toolBarContainer = QWidget(self)
#            toolbar.setStyleSheet('border: 1px solid black;')
            toolBarContainer.setLayout(QHBoxLayout(toolBarContainer))
            toolBarContainer.layout().setSpacing(0)
            
            toolBarContainer.layout().setContentsMargins(0,0,0,0)
            spacerItem = QSpacerItem(10,5,QSizePolicy.Expanding)
            toolBarContainer.layout().addSpacerItem(spacerItem)
            self.toolBarContainers.append(toolBarContainer)
            self.layout().insertWidget(self.__currentToolbarIndex,
                                       toolBarContainer)
        self.layout().insertWidget(self.layout().count()-1, toolbar)

        layout = self.toolBarContainers[self.__currentToolbarIndex].layout()
        layout.insertWidget(layout.count()-1,toolbar)

    def addToolBarBreak(self, area=None):
        self.__currentToolbarIndex += 1

    def setBlockFormat(self, blockFormat):
        self.textEdit.textCursor().setBlockFormat(blockFormat)

    def setupEditActions(self):
        tb = QToolBar(self)
        tb.setObjectName("editActions")
        tb.setWindowTitle("Edit Actions")

        self.addToolBar(tb)

        self.editActions = EditActions(self)
        self.editActions.addToToolbar(tb)
        return

    def setupTextActions(self):
        tb = QToolBar(self)
        tb.setWindowTitle("Format Actions")
        tb.setObjectName("fontFormatActions")

        self.addToolBar(tb)

        self.charFormatActions = CharFormatActions(self, signalProxy=self.signalProxy)
        self.charFormatActions.addToToolbar(tb, addWidgets=False)

        self.blockFormatActions = BlockFormatActions(self, signalProxy=self.blockProxy)
        self.blockFormatActions.addToToolbar(tb, addWidgets=False)

        tb = QToolBar(self)
        tb.setAllowedAreas(
                Qt.TopToolBarArea | Qt.BottomToolBarArea)
        tb.setWindowTitle("Format Actions")

        self.addToolBarBreak(Qt.TopToolBarArea)

        self.addToolBar(tb)

        comboStyle = QComboBox(tb)
        tb.addWidget(comboStyle)
        comboStyle.addItem(self.trUtf8(u"Standard"))
        comboStyle.addItem(self.trUtf8(u"Ungeordnete Liste (Punkte)"))
        comboStyle.addItem(self.trUtf8(u"Ungeordnete Liste (Kreise)"))
        comboStyle.addItem(self.trUtf8(u"Ungeordnete Liste (Quadrate)"))
        comboStyle.addItem(self.trUtf8(u"Geordnete Liste (Zahlen)"))
        comboStyle.addItem(self.trUtf8(u"Geordnete Liste (Alphabetisch klein)"))
        comboStyle.addItem(self.trUtf8(u"Geordnete Liste (Alphabetisch groß)"))
        comboStyle.addItem(self.trUtf8(u"Geordnete Liste (Römisch klein)"))
        comboStyle.addItem(self.trUtf8(u"Geordnete Liste (Römisch groß)"))
        comboStyle.activated.connect(self.textStyle)

        self.charFormatActions.addToToolbar(tb, addActions=False)

    def maybeSave(self):
        if not self.textEdit.document().isModified():
            return True

        if self.fileName.startswith(':/'):
            return True

        ret = QMessageBox.warning(self, "Application",
                "The document has been modified.\n"
                "Do you want to save your changes?",
                QMessageBox.Save | QMessageBox.Discard |
                        QMessageBox.Cancel)

        if ret == QMessageBox.Save:
            return self.fileSave()

        if ret == QMessageBox.Cancel:
            return False

        return True

    def textSize(self, pointSize):
        pointSize = float(pointSize)
        if pointSize < 0:
            return
        self.signalProxy.setPointSize(pointSize)
        return

    def textStyle(self, styleIndex):
        cursor = self.textEdit.textCursor()
        if styleIndex:
            styleDict = {
                1: QTextListFormat.ListDisc,
                2: QTextListFormat.ListCircle,
                3: QTextListFormat.ListSquare,
                4: QTextListFormat.ListDecimal,
                5: QTextListFormat.ListLowerAlpha,
                6: QTextListFormat.ListUpperAlpha,
                7: QTextListFormat.ListLowerRoman,
                8: QTextListFormat.ListUpperRoman,
            }

            style = styleDict.get(styleIndex, QTextListFormat.ListDisc)
            cursor.beginEditBlock()
            blockFmt = cursor.blockFormat()
            listFmt = QTextListFormat()

            if cursor.currentList():
                listFmt = cursor.currentList().format()
            else:
                listFmt.setIndent(blockFmt.indent() + 1)
                blockFmt.setIndent(0)
                cursor.setBlockFormat(blockFmt)

            listFmt.setStyle(style)
            cursor.createList(listFmt)
            cursor.endEditBlock()
        else:
            bfmt = QTextBlockFormat()
            bfmt.setObjectIndex(-1)
            cursor.mergeBlockFormat(bfmt)

    def textColor(self):
        col = QColorDialog.getColor(self.textEdit.textColor(), self)
        if not col.isValid():
            return

        self.signalProxy.setForegroundColor(col)

    def textAlign(self, action):
        if action == self.actionAlignLeft:
            self.textEdit.setAlignment(
                    Qt.AlignLeft | Qt.AlignAbsolute)
        elif action == self.actionAlignCenter:
            self.textEdit.setAlignment(Qt.AlignHCenter)
        elif action == self.actionAlignRight:
            self.textEdit.setAlignment(
                    Qt.AlignRight | Qt.AlignAbsolute)
        elif action == self.actionAlignJustify:
            self.textEdit.setAlignment(Qt.AlignJustify)

    def cursorPositionChanged(self):
        self.blockProxy.setBlockFormat(self.textEdit.textCursor().blockFormat())

    def clipboardDataChanged(self):
        self.editActions.actionPaste.setEnabled(
                len(QApplication.clipboard().text()) != 0)

    def about(self):
        QMessageBox.about(self, "About", 
                "This example demonstrates Qt's rich text editing facilities "
                "in action, providing an example document for you to "
                "experiment with.")

    def mergeFormatOnWordOrSelection(self, format):
        cursor = self.textEdit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)

        cursor.mergeCharFormat(format)
        self.textEdit.mergeCurrentCharFormat(format)

    def colorChanged(self, color):
        pix = QPixmap(16, 16)
        pix.fill(color)
        self.actionTextColor.setIcon(QIcon(pix))

    def trUtf8(self, sourceText):
        if hasattr(super(BaseEditor, self), 'trUtf8'):
            return super(BaseEditor, self).trUtf8(sourceText)
        return self.tr(sourceText)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindows = []
    for fn in sys.argv[1:] or [None]:
        textEdit = BaseEditor(fn)
        textEdit.resize(700, 800)
        textEdit.show()
        mainWindows.append(textEdit)

    sys.exit(app.exec_())

def testModule(app):
    print('Hallo')
    app.textEdit = BaseEditor()
    textEdit.resize(700, 800)
    textEdit.show()