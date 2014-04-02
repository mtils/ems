import os

from PyQt4.QtGui import QWidget, QHBoxLayout, QGroupBox, QTextEdit, QVBoxLayout,\
    QFont, QApplication, QStackedWidget, QComboBox, QPushButton, QGridLayout, \
    QToolButton, QRadioButton, QCheckBox, QCommandLinkButton, QStyleFactory, \
    QStyle, QTabWidget, QLineEdit, QSpinBox, QDateTimeEdit, QFrame, QFormLayout,\
    QLabel, QAction, QSlider, QScrollBar,QProgressBar, QDial, QTableWidget, \
    QListWidget, QTreeWidget, QColumnView, QScrollArea, QTableWidgetItem,\
    QTreeWidgetItem, QSplitter, QToolBar, QKeySequence, QFileDialog, \
    QFontMetrics, QTextDocumentWriter

from PyQt4.QtCore import Qt, pyqtSignal, QString, QDir, QFile, QTextStream,\
    QTextCodec

from ems.qt4.gui.syntaxhighlighter.csshighlighter import CssHighlighter

class QStyleEditor(QWidget):

    styleChangeRequested = pyqtSignal(QString,QString)

    currentFileNameChanged = pyqtSignal(QString)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self._styles = {}
        self._currentFileName = ''

        self.setupActions()
        self.setupUi()
        self.addPreviewPages()
        self.editor.setText(QApplication.instance().styleSheet())
        self.setStyleByIndex(0)

    def setupActions(self):
        app = QApplication.instance()
        openIcon = app.style().standardIcon(QStyle.SP_DialogOpenButton)
        self.openAction = QAction(openIcon, app.tr('Open'), self)
        self.openAction.setShortcut(QKeySequence.Open)
        self.openAction.setToolTip(app.tr('Open') + u' ' + str(self.openAction.shortcut().toString()))
        self.openAction.triggered.connect(self.openCssFile)
        self.addAction(self.openAction)

        saveIcon = app.style().standardIcon(QStyle.SP_DialogSaveButton)
        self.saveAction = QAction(saveIcon, app.tr('Save'), self)
        self.saveAction.setShortcut(QKeySequence.Save)
        self.saveAction.setToolTip(app.tr('Save') + u' ' + str(self.saveAction.shortcut().toString()))
        self.saveAction.triggered.connect(self.saveCssFile)
        self.addAction(self.saveAction)

        applyIcon = app.style().standardIcon(QStyle.SP_DialogApplyButton)
        self.applyAction = QAction(applyIcon, 'Apply',self)
        self.applyAction.setShortcut(Qt.CTRL + Qt.Key_Return)
        self.applyAction.setToolTip(self.tr('Apply to Application') + ' ' + str(self.applyAction.shortcut().toString()))
        self.applyAction.triggered.connect(self.emitCurrentStyles)
        self.addAction(self.applyAction)

        previewIcon = app.style().standardIcon(QStyle.SP_ArrowRight)
        self.refreshAction = QAction(previewIcon, self.tr('Refresh Preview'),self)
        self.refreshAction.setShortcut(Qt.CTRL + Qt.Key_R)
        self.refreshAction.setToolTip(self.tr('Apply to Preview') + u' ' + str(self.refreshAction.shortcut().toString()))
        self.refreshAction.triggered.connect(self.applyToPreview)

        self.addAction(self.refreshAction)

    def setupUi(self):
        self.splitter = QSplitter(self)
        self.setLayout(QHBoxLayout(self))
        self.layout().addWidget(self.splitter)

        self.editorGroup = QGroupBox(self)
        self.editorGroup.setTitle(self.tr('Stylesheet'))
        self.editorGroup.setLayout(QVBoxLayout(self.editorGroup))

        self.editorToolBar = QToolBar(self.editorGroup)
        self.editorGroup.layout().addWidget(self.editorToolBar)
        self.editorToolBar.addActions(self.actions())

        self.previewGroup = QGroupBox(self)
        self.previewGroup.setTitle(self.tr('Preview'))
        self.previewGroup.setLayout(QVBoxLayout(self.previewGroup))

        self.styleSelect = QComboBox(self.previewGroup)
        for s in QStyleFactory.keys():
            self.styleSelect.addItem(s)
        self.previewGroup.layout().addWidget(self.styleSelect)
        self.styleSelect.currentIndexChanged.connect(self.setStyleByIndex)

        self.previewView = QTabWidget(self.previewGroup)
        self.previewGroup.layout().addWidget(self.previewView)

        self.editor = QTextEdit(self)
        self.editor.setAcceptRichText(False)

        self.editorGroup.layout().addWidget(self.editor)

        font = QFont('Monospace')
        font.setStyleHint(QFont.TypeWriter)
        font.setPointSize(10)
        self.editor.setFont(font)

        fm = QFontMetrics(font)
        self.editor.setTabStopWidth(fm.width('XXXX'))

        self.highlighter = CssHighlighter(self.editor.document())
        self.splitter.addWidget(self.editorGroup)
        self.splitter.addWidget(self.previewGroup)

    def openCssFile(self):
        if self._currentFileName:
            dirName = os.path.dirname(self._currentFileName)
        else:
            dirName = QDir.homePath()

        fileName = QFileDialog.getOpenFileName(self, QApplication.instance().tr('Open'),
                                               dirName,
                                               self.tr('Css Files (*.css)'))
        if not fileName:
            return

        file = QFile(fileName)
        file.open(QFile.ReadOnly)
        stream = QTextStream(file)
        stream.setCodec('UTF-8')
        fileContent = stream.readAll()
        self.editor.setText(fileContent)
        self.setCurrentFileName(fileName)

        file.close()
    
    def emitCurrentStyles(self):
        styleName = self.styleSelect.itemText(self.styleSelect.currentIndex())
        styleSheet = self.editor.document().toPlainText()
        self.styleChangeRequested.emit(styleName, styleSheet)

    def saveCssFile(self):
        if self._currentFileName:
            dirName = os.path.dirname(self._currentFileName)
        else:
            dirName = QDir.homePath()

        fileName = QFileDialog.getSaveFileName(self, QApplication.instance().tr('Save'),
                                               dirName,
                                               self.tr('Css Files (*.css)'))

        writer = QTextDocumentWriter(fileName)
        writer.setFormat('plaintext')
        writer.setCodec(QTextCodec.codecForName('UTF-8'))
        success = writer.write(self.editor.document())
        if success:
            self.editor.document().setModified(False)

        self.setCurrentFileName(fileName)


    def currentFileName(self):
        return self._currentFileName

    def setCurrentFileName(self, fileName):
        fileName = unicode(fileName)
        if self._currentFileName == fileName:
            return
        self._currentFileName = fileName
        self.currentFileNameChanged.emit(QString.fromUtf8(self._currentFileName))

    def applyToPreview(self):
        self.previewView.setStyleSheet(self.editor.document().toPlainText())
        #self.previewView.style().polish()

    def addPreviewPages(self):
        self.previewView.addTab(self.formPage(), self.formPage().windowTitle())
        self.previewView.addTab(self.sliderPage(), self.sliderPage().windowTitle())
        self.previewView.addTab(self.itemViewPage(), self.itemViewPage().windowTitle())

    def formPage(self):
        if not hasattr(self, '_formPage'):
            mainPage = QWidget()
            mainPage.setWindowTitle(self.tr('Input Widgets'))
            mainPage.setLayout(QGridLayout(mainPage))

            sampleButton = QPushButton('QPushButton',mainPage)
            mainPage.layout().addWidget(sampleButton,0, 0)

            sampleToolButton = QToolButton(mainPage)
            sampleToolButton.setText('QToolButton')
            mainPage.layout().addWidget(sampleToolButton,0, 1)

            line = QFrame(mainPage)
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            mainPage.layout().addWidget(line,1,0,1,2)

            sampleRadioButton = QRadioButton('QRadioButton', mainPage)
            mainPage.layout().addWidget(sampleRadioButton, 2, 0)

            sampleRadioButton2 = QRadioButton('QRadioButton', mainPage)
            mainPage.layout().addWidget(sampleRadioButton2, 3, 0)

            checkBox = QCheckBox(mainPage)
            checkBox.setText(self.tr('QCheckBox'))
            checkBox.setTristate(True)
            checkBox.setChecked(True)
            mainPage.layout().addWidget(checkBox, 2, 1)

            checkBox2 = QCheckBox(mainPage)
            checkBox2.setText(self.tr('QCheckBox'))
            checkBox2.setTristate(True)
            checkBox2.setChecked(False)
            mainPage.layout().addWidget(checkBox2, 3, 1)

            inputGroup = QGroupBox(mainPage)
            inputGroup.setTitle(self.tr('QGroupBox'))
            inputGroup.setLayout(QVBoxLayout(inputGroup))

            combo = QComboBox(inputGroup)
            combo.addItem(self.tr('QComboBox'))
            inputGroup.layout().addWidget(combo)

            lineEdit = QLineEdit(inputGroup)
            lineEdit.setText(self.tr('QLineEdit'))
            inputGroup.layout().addWidget(lineEdit)

            textEdit = QTextEdit(inputGroup)
            textEdit.setText(self.tr('QTextEdit'))
            inputGroup.layout().addWidget(textEdit)

            spinboxFrame = QFrame(inputGroup)
            spinboxFrame.setFrameStyle(spinboxFrame.StyledPanel)
            spinboxFrame.setLayout(QFormLayout(spinboxFrame))

            spinBox = QSpinBox(spinboxFrame)
            #spinBox.setSpecialValueText(self.tr('QSpinBox'))
            spinboxFrame.layout().addRow(QLabel(self.tr('QSpinBox:')), spinBox)

            dateTimeEdit = QDateTimeEdit(spinboxFrame)
            spinboxFrame.layout().addRow(QLabel(self.tr('QDateTimeEdit:')), dateTimeEdit)
            inputGroup.layout().addWidget(spinboxFrame)

            mainPage.layout().addWidget(inputGroup,4,0,1,2)
            self._formPage = mainPage

        return self._formPage

    def sliderPage(self):
        if not hasattr(self,'_sliderPage'):
            sliderPage = QWidget()
            sliderPage.setWindowTitle(self.tr('Slider'))
            sliderPage.setLayout(QGridLayout(sliderPage))

            hSlider = QSlider(Qt.Horizontal, sliderPage)
            sliderPage.layout().addWidget(QLabel(self.tr('QSlider')),0,0)
            sliderPage.layout().addWidget(hSlider,0,1)

            hScrollbar = QScrollBar(Qt.Horizontal, sliderPage)
            sliderPage.layout().addWidget(QLabel(self.tr('QScrollBar')),1,0)
            sliderPage.layout().addWidget(hScrollbar,1,1)

            progressBar = QProgressBar(sliderPage)
            progressBar.setValue(50)
            sliderPage.layout().addWidget(QLabel(self.tr('QProgressBar')),2,0)
            sliderPage.layout().addWidget(progressBar,2,1)
            
            dial = QDial(sliderPage)
            dial.setValue(50)
            dial.setMaximumHeight(150)
            sliderPage.layout().addWidget(QLabel(self.tr('QDial')),3,0)
            sliderPage.layout().addWidget(dial,3,1)
            self._sliderPage = sliderPage
        return self._sliderPage
    
    def itemViewPage(self):
        if not hasattr(self,'_itemViewPage'):
            itemViewPage = QWidget()
            itemViewPage.setWindowTitle(self.tr('Item-Views'))
            itemViewPage.setLayout(QVBoxLayout(itemViewPage))

            listWidget = QListWidget(itemViewPage)
            listWidget.addItem('QListWidget 1')
            listWidget.addItem('QListWidget 2')
            itemViewPage.layout().addWidget(listWidget)

            tableWidget = QTableWidget(itemViewPage)
            tableWidget.setColumnCount(3)
            tableWidget.setRowCount(3)
            tableWidget.setHorizontalHeaderLabels(('QTableWidget 1','QTableWidget 2','QTableWidget 3'))
            for i in range(4):
                for j in range(4):
                    item = QTableWidgetItem('Cell ' + str(i) + '-' + str(j))
                    tableWidget.setItem(i,j,item)
            tableWidget.horizontalHeader().setResizeMode(tableWidget.horizontalHeader().Stretch)
            itemViewPage.layout().addWidget(tableWidget)

            treeWidget = QTreeWidget(itemViewPage)
            treeWidget.setHeaderLabels(('QTreeWidget 1','QTreeWidget 2'))
            treeWidget.setColumnCount(2)
            items = []
            for i in range(3):
                item = QTreeWidgetItem(['col 1','col 2'])

                for j in range(2):
                    childItem = QTreeWidgetItem(item, ['child col 1','child col 2'])
                items.append(item)

            treeWidget.addTopLevelItems(items)
            itemViewPage.layout().addWidget(treeWidget)
            
            
            
            self._itemViewPage = itemViewPage
        return self._itemViewPage
    
    def specialsPage(self):
        raise NotImplementedError()
        '''QCommandLinkButton
           QToolBox
           QGraphicsView
           QCalendar
           QLCDNumber
           QSplitter
           QMenu
           QToolBar'''

    def setStyleByIndex(self, index):
        styleName = str(self.styleSelect.itemText(index))
        if not self._styles.has_key(styleName):
            self._styles[styleName] = QStyleFactory.create(styleName)

        self.previewView.setStyle(self._styles[styleName])
        for widget in self.previewView.findChildren(QWidget):
            widget.setStyle(self._styles[styleName])


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    
    editor = QStyleEditor()
    editor.setMinimumWidth(800)
    editor.setMinimumHeight(600)
    editor.show()
    
    sys,exit(app.exec_())