
from PyQt4.QtCore import pyqtSignal, QString, QDir
from PyQt4.QtGui import QWidget, QLineEdit, QPushButton, QHBoxLayout
from PyQt4.QtGui import QFileDialog, QFileSystemModel, QCompleter

class FileSelect(QWidget):

    def __init__(self, parent=None):

        super(FileSelect, self).__init__(parent)

        self._forceExisting = True
        self._fileDialog = None

        self.setupUi()
        self.setupSignals()

    def isExistanceForced(self):
        return self._forceExisting

    def forceExisting(self, force=True):
        self._forceExisting = force

    def setupUi(self):

        self.setLayout(QHBoxLayout())

        self.dirModel = QFileSystemModel(self)
        self.dirModel.setRootPath(QDir.currentPath())

        self.lineEdit = QLineEdit(self)
        self.layout().addWidget(self.lineEdit)
        self.completer = QCompleter(self.lineEdit)
        self.completer.setModel(self.dirModel)
        self.lineEdit.setCompleter(self.completer)
        self.button = QPushButton(self)
        self.layout().addWidget(self.button)
        self.button.setText('...')
        self.button.setMaximumWidth(40)

    def setupSignals(self):
        self.button.clicked.connect(self.showFileDialog)

    def showFileDialog(self):
        if self._forceExisting:
            self.fileDialog.setFileMode(QFileDialog.ExistingFile)
        else:
            self.fileDialog.setFileMode(QFileDialog.AnyFile)
        self.fileDialog.show()

    @property
    def fileDialog(self):
        if not self._fileDialog:
            self._fileDialog = self._createFileDialog()
        return self._fileDialog

    def _createFileDialog(self):
        fileDialog= QFileDialog()
        fileDialog.fileSelected.connect(self._onFileSelected)
        return fileDialog

    def _onFileSelected(self, fileName):
        self.lineEdit.setText(fileName)







if __name__ == '__main__':

    import sys

    from PyQt4.QtGui import QApplication, QVBoxLayout

    app = QApplication(sys.argv)

    container = QWidget()
    container.setLayout(QVBoxLayout())
    
    fileSelect = FileSelect(container)
    container.layout().addWidget(fileSelect)
    
    container.show()

    sys.exit(app.exec_())