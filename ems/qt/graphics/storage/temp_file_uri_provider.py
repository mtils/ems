
import os, tempfile

from ems.qt.graphics.storage.interfaces import TargetUriProvider

class TempFileTargetUriProvider(TargetUriProvider):

    def __init__(self, fileName='graphics-editor.gson'):
        self._fileName = fileName

    def targetUriForRead(self):
        return os.path.join(tempfile.gettempdir(), self._fileName)

    def targetUriForWrite(self):
        return self.targetUriForRead()