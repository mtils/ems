
import os.path

from ems.qt import QtCore

QObject = QtCore.QObject
pyqtProperty = QtCore.pyqtProperty

def qmlImportPath(compiled=False):
    if not compiled:
        return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),'..','qt5','assets','qml'
            )
        )

class QError(QObject):

    FATAL = 'FATAL'

    ERROR = 'ERROR'

    WARNING = 'WARNING'

    NOTICE = 'NOTICE'

    def __init__(self, exception=None, code=None, message='', level='ERROR'):
        super().__init__()
        self._code = code
        self._message = message
        self._exception = None
        self._level = level
        if exception is not None:
            self.setException(exception)

    def getCode(self):
        return self._code

    def setCode(self, code):
        self._code = code
        return self

    code = pyqtProperty(int, getCode, setCode)

    def getMessage(self):
        return self._message

    def setMessage(self, message):
        self._message = message
        return self

    message = pyqtProperty("QString", getMessage, setMessage)

    def getLevel(self):
        return self._level

    def setLevel(self, level):
        self._level = level
        return self

    level = pyqtProperty("QString", getLevel, setLevel)

    def getException(self):
        return self._exception

    def setException(self, exception):
        self._exception = exception
        msgFound = False
        for arg in exception.args:
            if isinstance(arg, str):
                if not msgFound:
                    self.setMessage("{0}: {1}".format(exception.__class__.__name__, arg))
                    msgFound = False
            elif isinstance(arg, int):
                self.setCode(arg)

        self.setLevel(QError.ERROR)

        return self

    def __str__(self):
        return self._message