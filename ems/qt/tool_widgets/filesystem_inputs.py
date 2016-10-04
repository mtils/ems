
from __future__ import print_function

import os.path

from six import text_type

from ems.qt import QtWidgets, QtCore, QtGui

pyqtSignal = QtCore.pyqtSignal
pyqtProperty = QtCore.pyqtProperty
QDir = QtCore.QDir
Qt = QtCore.Qt
QWidget = QtWidgets.QWidget
QLineEdit = QtWidgets.QLineEdit
QPushButton = QtWidgets.QPushButton
QHBoxLayout = QtWidgets.QHBoxLayout
QFileDialog = QtWidgets.QFileDialog
QFileSystemModel = QtWidgets.QFileSystemModel
QCompleter = QtWidgets.QCompleter
QFrame = QtWidgets.QFrame

utf8 = QtCore.QString.fromUtf8 if hasattr(QtCore, 'QString') else text_type

class FileInput(QLineEdit):

    pathChanged = pyqtSignal(text_type)

    def __init__(self, parent=None):
        super(FileInput, self).__init__(parent)
        self._forceExisting = True
        self._fileDialog = None
        self._path = ''
        self._fsModel = None
        self._setUp()

    def getPath(self):
        return self._path

    def setPath(self, path):
        path = utf8(path)

        if path == self._path:
            return

        self._path = path
        self.setText(path)
        self.pathChanged.emit(self._path)

    path = pyqtProperty(text_type, getPath, setPath, notify=pathChanged)

    def isExistanceForced(self):
        return self._forceExisting

    def forceExisting(self, force=True):
        self._forceExisting = force

    def setCompleter(self, completer):
        raise RuntimeError("setCompleter of this widget is protected")

    def getFileSystemModel(self):
        if not self._fsModel:
            self._fsModel = self._createFileSystemModel()
        return self._fsModel

    def setFileSystemModel(self, model):
        if self._fsModel is model:
            return
        self._fsModel = model
        self.completer().setModel(self._fsModel)

    fileSystemModel = pyqtProperty(QFileSystemModel, getFileSystemModel, setFileSystemModel)

    def _setUp(self):
        self.editingFinished.connect(self._updatePath)
        completer = self._createCompleter()
        completer.setModel(self.fileSystemModel)
        super(FileInput, self).setCompleter(completer)
        #self._fsModel = 

    def _updatePath(self, *args, **kwargs):
        self.setPath(self.text())

    def _createCompleter(self):
        return QCompleter()

    def _createFileSystemModel(self):
        model = QFileSystemModel(self)
        model.setRootPath(QDir.currentPath())
        return model

class FileSelect(QFrame):

    pathChanged = pyqtSignal(text_type)

    def __init__(self, parent=None):

        super(FileSelect, self).__init__(parent)

        self._forceExisting = True
        self._fileDialog = None
        self._lineEdit = None
        self._button = None
        self._path = ''
        self._fsModel = None
        self._completer = None

        self._setupUi()

        self._setupSignals()
        self.setFrameStyle(QFrame.Plain)
        self.setFrameShape(QFrame.NoFrame)

    def getPath(self):
        return self._path

    def setPath(self, path):
        path = path if isinstance(path, QString) else QString.fromUtf8(path)

        if path == self._path:
            return

        self._path = path
        self._lineEdit.setText(path)
        self.pathChanged.emit(self._path)

    path = property(getPath, setPath)

    def isExistanceForced(self):
        return self._forceExisting

    def forceExisting(self, force=True):
        self._forceExisting = force

    def getLineEdit(self):
        return self._lineEdit

    def setLineEdit(self, lineEdit):

        self.delLineEdit()
        self._lineEdit = lineEdit
        self._lineEdit.editingFinished.connect(self._updatePath)
        self.layout().insertWidget(0, self._lineEdit)
        self._lineEdit.setCompleter(self.completer)

    def delLineEdit(self):
        if not self._lineEdit:
            return

        self._lineEdit.editingFinished.disconnect(self._updatePath)
        self.layout().removeWidget(self._lineEdit)

        self._lineEdit = None

    lineEdit = property(getLineEdit, setLineEdit, delLineEdit)

    def getButton(self):
        return self._button

    def setButton(self, button):
        self.delButton()
        self._button = button
        self.button.clicked.connect(self.showFileDialog)
        self.layout().addWidget(self._button)

    def delButton(self):

        if not self._button:
            return

        self._button.clicked.disconnect(self.showFileDialog)
        self.layout().removeWidget(self._button)
        self._button = None

    button = property(getButton, setButton, delButton)

    def getFileSystemModel(self):
        if self._fsModel is None:
            self._fsModel = self._createFsModel()
        return self._fsModel

    def setFileSystemModel(self, model):
        self._fsModel = model

    fileSystemModel = property(getFileSystemModel, setFileSystemModel)

    def getCompleter(self):
        if not self._completer:
            self.setCompleter(self._createCompleter())
        return self._completer

    def setCompleter(self, completer):
        self._completer = completer
        self._completer.setModel(self.fileSystemModel)
        self.lineEdit.setCompleter(self._completer)

    completer = property(getCompleter, setCompleter)

    def _setupUi(self):

        self.setLayout(QHBoxLayout())
        self.layout().setStretch(0,1)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.lineEdit = QLineEdit(self)

        self.button = QPushButton(self)

        self.button.setText('...')
        self.button.setMaximumWidth(40)

    def _setupSignals(self):
        pass

    def showFileDialog(self):
        self._configureFileDialog(self.fileDialog)
        self.fileDialog.show()

    @property
    def fileDialog(self):
        if not self._fileDialog:
            self._fileDialog = self._createFileDialog()
        return self._fileDialog

    def _createFsModel(self):
        model = QFileSystemModel(self)
        model.setRootPath(QDir.currentPath())
        return model

    def _createFileDialog(self):
        fileDialog= QFileDialog(parent=self.window())
        fileDialog.fileSelected.connect(self._onFileSelected)
        return fileDialog

    def _createCompleter(self):
        return QCompleter()

    def _configureFileDialog(self, fileDialog):
        if self._forceExisting:
            fileDialog.setFileMode(QFileDialog.ExistingFile)
        else:
            fileDialog.setFileMode(QFileDialog.AnyFile)

    def _onFileSelected(self, fileName):
        self.setPath(fileName)

    def _updatePath(self, *args, **kwargs):
        self.setPath(self.lineEdit.text())

class DirectorySelect(FileSelect):

    def _createFsModel(self):
        model = super(DirectorySelect, self)._createFsModel()
        model.setFilter(QDir.AllDirs)
        return model

    def _configureFileDialog(self, fileDialog):
        fileDialog.setFileMode(QFileDialog.Directory)
        fileDialog.setOptions(QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)

if __name__ == '__main__':

    import sys

    from PyQt4.QtGui import QApplication, QVBoxLayout

    app = QApplication(sys.argv)

    class FileInputContainer(QWidget):

        def printPathChange(self, path):
            print('path changed to:', path)

        def printErrorNum(self, num):
            print('Error num:', num, 'occured')

        def printErrorMessage(self, msg):
            print('Error msg:', msg)

    container = FileInputContainer()
    container.setLayout(QVBoxLayout(container))

    fileSelect = FileSelect(container)
    container.layout().addWidget(fileSelect)

    fileSelect.pathChanged.connect(container.printPathChange)

    newFileSelect = FileSelect(container)
    newFileSelect.forceExisting(False)
    container.layout().addWidget(newFileSelect)

    newFileSelect.pathChanged.connect(container.printPathChange)

    dirSelect = DirectorySelect(container)
    container.layout().addWidget(dirSelect)

    dirSelect.pathChanged.connect(container.printPathChange)

    newDirSelect = DirectorySelect(container)
    newDirSelect.forceExisting(False)
    container.layout().addWidget(newDirSelect)

    newDirSelect.pathChanged.connect(container.printPathChange)

    container.show()

    sys.exit(app.exec_())