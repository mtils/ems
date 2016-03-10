
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
        self._events = app('events')

    @pyqtSlot("QString", result=QObject)
    @pyqtSlot("QString", QObject, result=QObject)
    def make(self, abstract, parent=None):
        obj = app(abstract)
        self._engine.setObjectOwnership(obj, self._engine.CppOwnership)
        return obj

    @pyqtSlot("QString", result=float)
    @pyqtSlot("QString", "QJSValue", result=float)
    @pyqtSlot("QString", "QJSValue", "QJSValue", result=float)
    @pyqtSlot("QString", "QJSValue", "QJSValue", "QJSValue", result=float)
    def getFloat(self, abstractMethod, arg1=None, arg2=None, arg3=None):

        abstract, method = self._splitAbstractMethod(abstractMethod)

        obj = app(abstract)
        result = getattr(obj, method)(*self._argsToPython(abstractMethod, *(arg1, arg2, arg3)))

        if isinstance(result, float):
            return result
        if isinstance(result, int):
            return float(result)
        return 0.0

    @pyqtSlot("QString", result=int)
    @pyqtSlot("QString", "QJSValue", result=int)
    @pyqtSlot("QString", "QJSValue", "QJSValue", result=int)
    @pyqtSlot("QString", "QJSValue", "QJSValue", "QJSValue", result=int)
    def getInt(self, abstractMethod, arg1=None, arg2=None, arg3=None):

        abstract, method = self._splitAbstractMethod(abstractMethod)

        obj = app(abstract)
        result = getattr(obj, method)(*self._argsToPython(abstractMethod,*(arg1, arg2, arg3)))

        if isinstance(result, float):
            return int(result)
        if isinstance(result, int):
            return result
        return 0

    @pyqtSlot("QString", result='QString')
    @pyqtSlot("QString", "QJSValue", result='QString')
    @pyqtSlot("QString", "QJSValue", "QJSValue", result='QString')
    @pyqtSlot("QString", "QJSValue", "QJSValue", "QJSValue", result='QString')
    def getString(self, abstractMethod, arg1=None, arg2=None, arg3=None):

        abstract, method = self._splitAbstractMethod(abstractMethod)

        obj = app(abstract)
        result = getattr(obj, method)(*self._argsToPython(abstractMethod,*(arg1, arg2, arg3)))

        if isinstance(result, str):
            return result

        return str(result)

    @pyqtSlot("QString", result=bool)
    @pyqtSlot("QString", "QJSValue", result=bool)
    @pyqtSlot("QString", "QJSValue", "QJSValue", result=bool)
    @pyqtSlot("QString", "QJSValue", "QJSValue", "QJSValue", result=bool)
    def getBool(self, abstractMethod, arg1=None, arg2=None, arg3=None):

        abstract, method = self._splitAbstractMethod(abstractMethod)

        obj = app(abstract)
        result = getattr(obj, method)(*self._argsToPython(abstractMethod,*(arg1, arg2, arg3)))

        if isinstance(result, bool):
            return result

        return bool(result)

    @pyqtSlot("QString", result="QVariantMap")
    @pyqtSlot("QString", "QJSValue", result="QVariantMap")
    @pyqtSlot("QString", "QJSValue", "QJSValue", result="QVariantMap")
    @pyqtSlot("QString", "QJSValue", "QJSValue", "QJSValue", result="QVariantMap")
    def getDict(self, abstractMethod, arg1=None, arg2=None, arg3=None):

        abstract, method = self._splitAbstractMethod(abstractMethod)

        obj = app(abstract)
        result = getattr(obj, method)(*self._argsToPython(abstractMethod,*(arg1, arg2, arg3)))

        if isinstance(result, dict) or result is None:
            return result

        return dict(result)

    @pyqtSlot("QString", result='QVariantList')
    @pyqtSlot("QString", "QJSValue", result='QVariantList')
    @pyqtSlot("QString", "QJSValue", "QJSValue", result='QVariantList')
    @pyqtSlot("QString", "QJSValue", "QJSValue", "QJSValue", result='QVariantList')
    def getList(self, abstractMethod, arg1=None, arg2=None, arg3=None):

        abstract, method = self._splitAbstractMethod(abstractMethod)

        obj = app(abstract)
        result = getattr(obj, method)(*self._argsToPython(abstractMethod,*(arg1, arg2, arg3)))

        if isinstance(result, list) or result is None:
            return result

        return list(result)

    def _splitAbstractMethod(self, abstractMethod):
        return abstractMethod.split('.', 1)

    @staticmethod
    def new(engine, scriptEngine):
        factory = Factory(engine, scriptEngine)
        engine.setObjectOwnership(factory, engine.CppOwnership)
        return factory

    def _argsToPython(self, abstractMethod, *args):
        parsed = []
        for arg in args:
            # A passed arg would be a QJSValue
            if arg is not None:
                parsed.append(self._toPython(arg))

        event = "qml-factory.calling:{}".format(abstractMethod)

        self._events.fire(event, parsed)

        return parsed

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