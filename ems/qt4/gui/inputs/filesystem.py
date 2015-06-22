
from __future__ import print_function

import os.path

from PyQt4.QtCore import pyqtSignal, QString, QDir
from PyQt4.QtGui import QWidget, QLineEdit, QPushButton, QHBoxLayout
from PyQt4.QtGui import QFileDialog, QFileSystemModel, QCompleter

class FileSelect(QWidget):

    pathChanged = pyqtSignal(QString)

    errorOccured = pyqtSignal([int],[QString])

    PATH_DOES_NOT_EXIST = 1

    PATH_EXISTS = 2

    PATH_IS_DIR = 3

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

    def isExistanceForced(self):
        return self._forceExisting

    def forceExisting(self, force=True):
        self._forceExisting = force

    def getLineEdit(self):
        return self._lineEdit

    def setLineEdit(self, lineEdit):

        self.delLineEdit()
        self._lineEdit = lineEdit
        self._lineEdit.textChanged.connect(self._setPathIfExists)
        self.layout().insertWidget(0, self._lineEdit)
        self._lineEdit.setCompleter(self.completer)

    def delLineEdit(self):
        if not self._lineEdit:
            return
        self._lineEdit.textChanged.disconnect(self._setPathIfExists)
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

        self.lineEdit = QLineEdit(self)

        self.button = QPushButton(self)

        self.button.setText('...')
        self.button.setMaximumWidth(40)

    def _setupSignals(self):
        self.errorOccured[int].connect(self._emitErrorMsg)

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
        self.lineEdit.setText(fileName)

    def _setPathIfExists(self, path):

        if path == self._path:
            return

        try:
            self._checkPath(path)
            self._path = path
            self.pathChanged.emit(path)
        except IOError as e:
            self.errorOccured[int].emit(e.args[0])


    def _checkPath(self, path):
        self._checkExistance(path)
        self._checkType(path)


    def _checkExistance(self, path):

        exists = os.path.exists(unicode(path))

        if self._forceExisting and not exists:
            raise IOError(self.PATH_DOES_NOT_EXIST)

        if not self._forceExisting and exists:
            raise IOError(self.PATH_EXISTS)

        return exists

    def _checkType(self, path):
        if os.path.isdir(path):
            raise IOError(self.PATH_IS_DIR)

    def _emitErrorMsg(self, errorNum):
        self.errorOccured[QString].emit(self.getErrorMsg(errorNum))

    def getErrorMsg(self, errorNum):
        if errorNum == self.PATH_DOES_NOT_EXIST:
            return self.trUtf8(u"Path does not exist")
        elif errorNum == self.PATH_EXISTS:
            return self.trUtf8(u"Path does exist")
        elif errorNum == self.PATH_IS_DIR:
            return self.trUtf8(u"Path is a directory")

        return QString()

class DirectorySelect(FileSelect):

    PATH_IS_FILE = 4

    def _createFsModel(self):
        model = super(DirectorySelect, self)._createFsModel()
        model.setFilter(QDir.AllDirs)
        return model

    def _configureFileDialog(self, fileDialog):
        fileDialog.setFileMode(QFileDialog.Directory)
        fileDialog.setOptions(QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)

        #super(DirectorySelect, self)._configureFileDialog(fileDialog)


    def _checkType(self, path):
        if os.path.isfile(path):
            raise IOError(self.PATH_IS_FILE)

    def getErrorMsg(self, errorNum):
        if errorNum == self.PATH_IS_FILE:
            return self.trUtf8(u"Path is a file")
        return super(DirectorySelect, self).getErrorMsg(errorNum)

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
    fileSelect.errorOccured[int].connect(container.printErrorNum)
    fileSelect.errorOccured[QString].connect(container.printErrorMessage)

    newFileSelect = FileSelect(container)
    newFileSelect.forceExisting(False)
    container.layout().addWidget(newFileSelect)

    newFileSelect.pathChanged.connect(container.printPathChange)
    newFileSelect.errorOccured[int].connect(container.printErrorNum)
    newFileSelect.errorOccured[QString].connect(container.printErrorMessage)

    dirSelect = DirectorySelect(container)
    container.layout().addWidget(dirSelect)

    dirSelect.pathChanged.connect(container.printPathChange)
    dirSelect.errorOccured[int].connect(container.printErrorNum)
    dirSelect.errorOccured[QString].connect(container.printErrorMessage)

    newDirSelect = DirectorySelect(container)
    newDirSelect.forceExisting(False)
    container.layout().addWidget(newDirSelect)

    newDirSelect.pathChanged.connect(container.printPathChange)
    newDirSelect.errorOccured[int].connect(container.printErrorNum)
    newDirSelect.errorOccured[QString].connect(container.printErrorMessage)

    container.show()

    sys.exit(app.exec_())