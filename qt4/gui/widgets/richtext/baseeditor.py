#coding=utf-8
'''
Created on 27.08.2011

@author: michi
'''
import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QWidget, QHBoxLayout, QSpacerItem, QSizePolicy

from ems.qt4.gui.widgets.dialogable import DialogableWidget
from ems.qt4.gui.widgets.completiontextedit import CompletionTextEdit

class BaseEditor(DialogableWidget):
    def __init__(self, text=None, parent=None):
        super(BaseEditor, self).__init__(parent)
        self.rsrcPath = ':/textedit'
        self.setWindowIcon(QtGui.QIcon(':/images/logo.png'))
        #self.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.__currentToolbarIndex = 0
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().setSpacing(0)
        #self.layout().setMargin(0)
        #l = QtGui.QVBoxLayout(self)
        
        self.toolBarContainers = []
        
        self.textEdit = CompletionTextEdit(self)
        self.layout().addWidget(self.textEdit)
        
        self.setupEditActions()
        
        self.setupTextActions()
        
        self.textEdit.currentCharFormatChanged.connect(
                self.currentCharFormatChanged)
        self.textEdit.cursorPositionChanged.connect(self.cursorPositionChanged)
        #self.setCentralWidget(self.textEdit)
        self.textEdit.setFocus()
        
        self.fontChanged(self.textEdit.font())
        self.colorChanged(self.textEdit.textColor())
        self.alignmentChanged(self.textEdit.alignment())
#        self.textEdit.document().modificationChanged.connect(
#                self.actionSave.setEnabled)
        self.textEdit.document().modificationChanged.connect(
                self.setWindowModified)
        self.textEdit.document().undoAvailable.connect(
                self.actionUndo.setEnabled)
        self.textEdit.document().redoAvailable.connect(
                self.actionRedo.setEnabled)
        self.setWindowModified(self.textEdit.document().isModified())
        
        self.actionUndo.setEnabled(self.textEdit.document().isUndoAvailable())
        self.actionRedo.setEnabled(self.textEdit.document().isRedoAvailable())
        self.actionUndo.triggered.connect(self.textEdit.undo)
        self.actionRedo.triggered.connect(self.textEdit.redo)
        self.actionCut.setEnabled(False)
        self.actionCopy.setEnabled(False)
        self.actionCut.triggered.connect(self.textEdit.cut)
        self.actionCopy.triggered.connect(self.textEdit.copy)
        self.actionPaste.triggered.connect(self.textEdit.paste)
        self.textEdit.copyAvailable.connect(self.actionCut.setEnabled)
        self.textEdit.copyAvailable.connect(self.actionCopy.setEnabled)
        QtGui.QApplication.clipboard().dataChanged.connect(
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
        
#        for i in range(self.layout().count()): 
#            if self.layout().itemAt(i).widget() is self.textEdit:
#                self.layout().setStretch(i, 1)
#            else:
#                self.layout().setStretch(i, 0)
        #self.layout().setStretch(self.layout().count(), 1)
        
        layout = self.toolBarContainers[self.__currentToolbarIndex].layout()
        layout.insertWidget(layout.count()-1,toolbar)
    
    def addToolBarBreak(self, area=None):
        self.__currentToolbarIndex += 1
    
    
    def setupEditActions(self):
        tb = QtGui.QToolBar(self)
        tb.setObjectName("editActions")
        tb.setWindowTitle("Edit Actions")
        self.addToolBar(tb)

        self.actionUndo = QtGui.QAction(
                QtGui.QIcon.fromTheme('edit-undo',
                        QtGui.QIcon(self.rsrcPath + '/editundo.png')),
                "&Undo", self, shortcut=QtGui.QKeySequence.Undo)
        tb.addAction(self.actionUndo)
        
        self.actionRedo = QtGui.QAction(
                QtGui.QIcon.fromTheme('edit-redo',
                        QtGui.QIcon(self.rsrcPath + '/editredo.png')),
                "&Redo", self, priority=QtGui.QAction.LowPriority,
                shortcut=QtGui.QKeySequence.Redo)
        tb.addAction(self.actionRedo)
        
        self.actionCut = QtGui.QAction(
                QtGui.QIcon.fromTheme('edit-cut',
                        QtGui.QIcon(self.rsrcPath + '/editcut.png')),
                "Cu&t", self, priority=QtGui.QAction.LowPriority,
                shortcut=QtGui.QKeySequence.Cut)
        tb.addAction(self.actionCut)
        

        self.actionCopy = QtGui.QAction(
                QtGui.QIcon.fromTheme('edit-copy',
                        QtGui.QIcon(self.rsrcPath + '/editcopy.png')),
                "&Copy", self, priority=QtGui.QAction.LowPriority,
                shortcut=QtGui.QKeySequence.Copy)
        tb.addAction(self.actionCopy)
        

        self.actionPaste = QtGui.QAction(
                QtGui.QIcon.fromTheme('edit-paste',
                        QtGui.QIcon(self.rsrcPath + '/editpaste.png')),
                "&Paste", self, priority=QtGui.QAction.LowPriority,
                shortcut=QtGui.QKeySequence.Paste,
                enabled=(len(QtGui.QApplication.clipboard().text()) != 0))
        tb.addAction(self.actionPaste)
        

    def setupTextActions(self):
        tb = QtGui.QToolBar(self)
        tb.setWindowTitle("Format Actions")
        tb.setObjectName("fontFormatActions")
        
        self.addToolBar(tb)

        

        self.actionTextBold = QtGui.QAction(
                QtGui.QIcon.fromTheme('format-text-bold',
                        QtGui.QIcon(self.rsrcPath + '/textbold.png')),
                "&Bold", self, priority=QtGui.QAction.LowPriority,
                shortcut=QtCore.Qt.CTRL + QtCore.Qt.Key_B,
                triggered=self.textBold, checkable=True)
        bold = QtGui.QFont()
        bold.setBold(True)
        self.actionTextBold.setFont(bold)
        tb.addAction(self.actionTextBold)
        

        self.actionTextItalic = QtGui.QAction(
                QtGui.QIcon.fromTheme('format-text-italic',
                        QtGui.QIcon(self.rsrcPath + '/textitalic.png')),
                "&Italic", self, priority=QtGui.QAction.LowPriority,
                shortcut=QtCore.Qt.CTRL + QtCore.Qt.Key_I,
                triggered=self.textItalic, checkable=True)
        italic = QtGui.QFont()
        italic.setItalic(True)
        self.actionTextItalic.setFont(italic)
        tb.addAction(self.actionTextItalic)
        

        self.actionTextUnderline = QtGui.QAction(
                QtGui.QIcon.fromTheme('format-text-underline',
                        QtGui.QIcon(self.rsrcPath + '/textunder.png')),
                "&Underline", self, priority=QtGui.QAction.LowPriority,
                shortcut=QtCore.Qt.CTRL + QtCore.Qt.Key_U,
                triggered=self.textUnderline, checkable=True)
        underline = QtGui.QFont()
        underline.setUnderline(True)
        self.actionTextUnderline.setFont(underline)
        tb.addAction(self.actionTextUnderline)
        
        grp = QtGui.QActionGroup(self, triggered=self.textAlign)

        # Make sure the alignLeft is always left of the alignRight.
        if QtGui.QApplication.isLeftToRight():
            self.actionAlignLeft = QtGui.QAction(
                    QtGui.QIcon.fromTheme('format-justify-left',
                            QtGui.QIcon(self.rsrcPath + '/textleft.png')),
                    "&Left", grp)
            self.actionAlignCenter = QtGui.QAction(
                    QtGui.QIcon.fromTheme('format-justify-center',
                            QtGui.QIcon(self.rsrcPath + '/textcenter.png')),
                    "C&enter", grp)
            self.actionAlignRight = QtGui.QAction(
                    QtGui.QIcon.fromTheme('format-justify-right',
                            QtGui.QIcon(self.rsrcPath + '/textright.png')),
                    "&Right", grp)
        else:
            self.actionAlignRight = QtGui.QAction(
                    QtGui.QIcon.fromTheme('format-justify-right',
                            QtGui.QIcon(self.rsrcPath + '/textright.png')),
                    "&Right", grp)
            self.actionAlignCenter = QtGui.QAction(
                    QtGui.QIcon.fromTheme('format-justify-center',
                            QtGui.QIcon(self.rsrcPath + '/textcenter.png')),
                    "C&enter", grp)
            self.actionAlignLeft = QtGui.QAction(
                    QtGui.QIcon.fromTheme('format-justify-left',
                            QtGui.QIcon(self.rsrcPath + '/textleft.png')),
                    "&Left", grp)
 
        self.actionAlignJustify = QtGui.QAction(
                QtGui.QIcon.fromTheme('format-justify-fill',
                        QtGui.QIcon(self.rsrcPath + '/textjustify.png')),
                "&Justify", grp)

        self.actionAlignLeft.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_L)
        self.actionAlignLeft.setCheckable(True)
        self.actionAlignLeft.setPriority(QtGui.QAction.LowPriority)

        self.actionAlignCenter.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_E)
        self.actionAlignCenter.setCheckable(True)
        self.actionAlignCenter.setPriority(QtGui.QAction.LowPriority)

        self.actionAlignRight.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_R)
        self.actionAlignRight.setCheckable(True)
        self.actionAlignRight.setPriority(QtGui.QAction.LowPriority)

        self.actionAlignJustify.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_J)
        self.actionAlignJustify.setCheckable(True)
        self.actionAlignJustify.setPriority(QtGui.QAction.LowPriority)

        tb.addActions(grp.actions())
        
        pix = QtGui.QPixmap(16, 16)
        pix.fill(QtCore.Qt.black)
        self.actionTextColor = QtGui.QAction(QtGui.QIcon(pix), "&Color...",
                self, triggered=self.textColor)
        tb.addAction(self.actionTextColor)
        
        tb = QtGui.QToolBar(self)
        tb.setAllowedAreas(
                QtCore.Qt.TopToolBarArea | QtCore.Qt.BottomToolBarArea)
        tb.setWindowTitle("Format Actions")
        
        self.addToolBarBreak(QtCore.Qt.TopToolBarArea)
        
        self.addToolBar(tb)

        comboStyle = QtGui.QComboBox(tb)
        tb.addWidget(comboStyle)
        comboStyle.addItem(self.trUtf8("Standard"))
        comboStyle.addItem(self.trUtf8("Ungeordnete Liste (Punkte)"))
        comboStyle.addItem(self.trUtf8("Ungeordnete Liste (Kreise)"))
        comboStyle.addItem(self.trUtf8("Ungeordnete Liste (Quadrate)"))
        comboStyle.addItem(self.trUtf8("Geordnete Liste (Zahlen)"))
        comboStyle.addItem(self.trUtf8("Geordnete Liste (Alphabetisch klein)"))
        comboStyle.addItem(self.trUtf8("Geordnete Liste (Alphabetisch groß)"))
        comboStyle.addItem(self.trUtf8("Geordnete Liste (Römisch klein)"))
        comboStyle.addItem(self.trUtf8("Geordnete Liste (Römisch groß)"))
        comboStyle.activated.connect(self.textStyle)

        self.comboFont = QtGui.QFontComboBox(tb)
        tb.addWidget(self.comboFont)
        self.comboFont.activated[str].connect(self.textFamily)

        self.comboSize = QtGui.QComboBox(tb)
        self.comboSize.setObjectName("comboSize")
        tb.addWidget(self.comboSize)
        self.comboSize.setEditable(True)

        db = QtGui.QFontDatabase()
        for size in db.standardSizes():
            self.comboSize.addItem("%s" % (size))

        self.comboSize.activated[str].connect(self.textSize)
        self.comboSize.setCurrentIndex(
                self.comboSize.findText(
                        "%s" % (QtGui.QApplication.font().pointSize())))


    def maybeSave(self):
        if not self.textEdit.document().isModified():
            return True

        if self.fileName.startswith(':/'):
            return True

        ret = QtGui.QMessageBox.warning(self, "Application",
                "The document has been modified.\n"
                "Do you want to save your changes?",
                QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard |
                        QtGui.QMessageBox.Cancel)

        if ret == QtGui.QMessageBox.Save:
            return self.fileSave()

        if ret == QtGui.QMessageBox.Cancel:
            return False

        return True

    
    def textBold(self):
        fmt = QtGui.QTextCharFormat()
        fmt.setFontWeight(self.actionTextBold.isChecked() and QtGui.QFont.Bold or QtGui.QFont.Normal)
        self.mergeFormatOnWordOrSelection(fmt)

    def textUnderline(self):
        fmt = QtGui.QTextCharFormat()
        fmt.setFontUnderline(self.actionTextUnderline.isChecked())
        self.mergeFormatOnWordOrSelection(fmt)

    def textItalic(self):
        fmt = QtGui.QTextCharFormat()
        fmt.setFontItalic(self.actionTextItalic.isChecked())
        self.mergeFormatOnWordOrSelection(fmt)

    def textFamily(self, family):
        fmt = QtGui.QTextCharFormat()
        fmt.setFontFamily(family)
        self.mergeFormatOnWordOrSelection(fmt)

    def textSize(self, pointSize):
        pointSize = float(pointSize)
        if pointSize > 0:
            fmt = QtGui.QTextCharFormat()
            fmt.setFontPointSize(pointSize)
            self.mergeFormatOnWordOrSelection(fmt)

    def textStyle(self, styleIndex):
        cursor = self.textEdit.textCursor()
        if styleIndex:
            styleDict = {
                1: QtGui.QTextListFormat.ListDisc,
                2: QtGui.QTextListFormat.ListCircle,
                3: QtGui.QTextListFormat.ListSquare,
                4: QtGui.QTextListFormat.ListDecimal,
                5: QtGui.QTextListFormat.ListLowerAlpha,
                6: QtGui.QTextListFormat.ListUpperAlpha,
                7: QtGui.QTextListFormat.ListLowerRoman,
                8: QtGui.QTextListFormat.ListUpperRoman,
            }

            style = styleDict.get(styleIndex, QtGui.QTextListFormat.ListDisc)
            cursor.beginEditBlock()
            blockFmt = cursor.blockFormat()
            listFmt = QtGui.QTextListFormat()

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
            bfmt = QtGui.QTextBlockFormat()
            bfmt.setObjectIndex(-1)
            cursor.mergeBlockFormat(bfmt)

    def textColor(self):
        col = QtGui.QColorDialog.getColor(self.textEdit.textColor(), self)
        if not col.isValid():
            return

        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(col)
        self.mergeFormatOnWordOrSelection(fmt)
        self.colorChanged(col)

    def textAlign(self, action):
        if action == self.actionAlignLeft:
            self.textEdit.setAlignment(
                    QtCore.Qt.AlignLeft | QtCore.Qt.AlignAbsolute)
        elif action == self.actionAlignCenter:
            self.textEdit.setAlignment(QtCore.Qt.AlignHCenter)
        elif action == self.actionAlignRight:
            self.textEdit.setAlignment(
                    QtCore.Qt.AlignRight | QtCore.Qt.AlignAbsolute)
        elif action == self.actionAlignJustify:
            self.textEdit.setAlignment(QtCore.Qt.AlignJustify)

    def currentCharFormatChanged(self, format):
        self.fontChanged(format.font())
        self.colorChanged(format.foreground().color())

    def cursorPositionChanged(self):
        self.alignmentChanged(self.textEdit.alignment())

    def clipboardDataChanged(self):
        self.actionPaste.setEnabled(
                len(QtGui.QApplication.clipboard().text()) != 0)

    def about(self):
        QtGui.QMessageBox.about(self, "About", 
                "This example demonstrates Qt's rich text editing facilities "
                "in action, providing an example document for you to "
                "experiment with.")

    def mergeFormatOnWordOrSelection(self, format):
        cursor = self.textEdit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QtGui.QTextCursor.WordUnderCursor)

        cursor.mergeCharFormat(format)
        self.textEdit.mergeCurrentCharFormat(format)

    def fontChanged(self, font):
        self.comboFont.setCurrentIndex(
                self.comboFont.findText(QtGui.QFontInfo(font).family()))
        self.comboSize.setCurrentIndex(
                self.comboSize.findText("%s" % font.pointSize()))
        self.actionTextBold.setChecked(font.bold())
        self.actionTextItalic.setChecked(font.italic())
        self.actionTextUnderline.setChecked(font.underline())

    def colorChanged(self, color):
        pix = QtGui.QPixmap(16, 16)
        pix.fill(color)
        self.actionTextColor.setIcon(QtGui.QIcon(pix))

    def alignmentChanged(self, alignment):
        if alignment & QtCore.Qt.AlignLeft:
            self.actionAlignLeft.setChecked(True)
        elif alignment & QtCore.Qt.AlignHCenter:
            self.actionAlignCenter.setChecked(True)
        elif alignment & QtCore.Qt.AlignRight:
            self.actionAlignRight.setChecked(True)
        elif alignment & QtCore.Qt.AlignJustify:
            self.actionAlignJustify.setChecked(True)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    mainWindows = []
    for fn in sys.argv[1:] or [None]:
        textEdit = BaseEditor(fn)
        textEdit.resize(700, 800)
        textEdit.show()
        mainWindows.append(textEdit)

    sys.exit(app.exec_())
