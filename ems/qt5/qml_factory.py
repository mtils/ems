
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

    @pyqtSlot("QString", "QString", result=float)
    @pyqtSlot("QString", "QString", "QJSValue", result=float)
    @pyqtSlot("QString", "QString", "QJSValue", "QJSValue", result=float)
    @pyqtSlot("QString", "QString", "QJSValue", "QJSValue", "QJSValue", result=float)
    def getFloat(self, abstract, method, arg1=None, arg2=None, arg3=None):

        obj = app(abstract)
        args = []
        for arg in (arg1, arg2, arg3):
            # A passed arg would be a QJSValue
            if arg is not None:
                args.append(self._toPython(arg))

        result = getattr(obj, method)(*args)
        return 0.0 if not isinstance(result, float) else result

    @staticmethod
    def new(engine, scriptEngine):
        factory = Factory(engine, scriptEngine)
        engine.setObjectOwnership(factory, engine.CppOwnership)
        return factory

    def _toPython(self, qJsValue):

        if qJsValue is None:
            return None

        if qJsValue.isArray():
            #print("Returning QObject from array")
            return qJsValue.toQObject()
        elif qJsValue.isBool():
            #print("Returning bool")
            return qJsValue.toBool()
        elif qJsValue.isDate():
            #print("Returning QDateTime")
            return qJsValue.toDateTime()
        elif qJsValue.isNull():
            #print("Returning None from null")
            return None
        elif qJsValue.isNumber():
            #print("Returning number")
            return qJsValue.toNumber()
        elif qJsValue.isQObject():
            #print("Returning QObject")
            return qJsValue.toQObject()
        elif qJsValue.isString():
            #print("Returning string")
            return qJsValue.toString()
        elif qJsValue.isUndefined():
            #print("Returning undefined")
            return None
        elif qJsValue.isVariant():
            #print("Returning variant")
            return qJsValue.toVariant()
        #print("Nothing matching found")