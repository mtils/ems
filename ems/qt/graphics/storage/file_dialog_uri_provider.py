
import os, tempfile

from ems.typehint import accepts
from ems.qt.graphics.storage.interfaces import TargetUriProvider
from ems.gui.interfaces.dialogs import AbstractFileDialog
from ems.app import app

class FileDialogUriProvider(TargetUriProvider):

    @accepts(AbstractFileDialog)
    def __init__(self, fileDialog):
        self._fileDialog = fileDialog
        self.openWindowTitle = 'Open File'
        self.fileFilter = 'Graphics Editor Files (*.gson)'
        self.saveWindowTitle = 'Save File'

    def targetUriForRead(self):

        fileName = self._fileDialog.openFileName(
            self._findTopLevelWindow(),
            self.openWindowTitle,
            self.fileFilter
        )


        return fileName

    def targetUriForWrite(self):

        fileName = self._fileDialog.saveFileName(
            self._findTopLevelWindow(),
            self.saveWindowTitle,
            self.fileFilter
        )

        return fileName

    def _findTopLevelWindow(self):
        qapp = app()
        for widget in qapp.topLevelWidgets():
            if widget.isVisible() and widget.isWindow():
                return widget