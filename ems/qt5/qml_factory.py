
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtQml import QQmlEngine

from ems.typehint import accepts
from ems.app import app
from ems.ioc.container import Container

class Factory(QObject):

    def __init__(self, engine, scriptEngine):
        super().__init__()
        self._engine = engine
        self._scriptEngine = scriptEngine

    @pyqtSlot("QString", result=QObject)
    @pyqtSlot("QString", QObject, result=QObject)
    def make(self, abstract, parent=None):
        obj = app(abstract)
        self._engine.setObjectOwnership(obj, self._engine.CppOwnership)
        return obj

    @staticmethod
    def new(engine, scriptEngine):
        factory = Factory(engine, scriptEngine)
        engine.setObjectOwnership(factory, engine.CppOwnership)
        return factory