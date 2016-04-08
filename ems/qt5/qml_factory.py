
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt5.QtQml import QQmlEngine

from ems.typehint import accepts
from ems.app import app
from ems.ioc.container import Container
from ems.qt5.util import QError

class Factory(QObject):

    error = pyqtSignal(QError)

    def __init__(self, engine, scriptEngine):
        super().__init__()
        self._engine = engine
        self._scriptEngine = scriptEngine
        self._events = app('events')

    @pyqtSlot("QString", result=QObject)
    @pyqtSlot("QString", QObject, result=QObject)
    def make(self, abstract, parent=None):
        try:
            obj = app(abstract)
            self._engine.setObjectOwnership(obj, self._engine.CppOwnership)
            return obj
        except Exception as e:
            self.error.emit(QError(e))
            return QObject()

    @pyqtSlot("QString", result=float)
    @pyqtSlot("QString", "QJSValue", result=float)
    @pyqtSlot("QString", "QJSValue", "QJSValue", result=float)
    @pyqtSlot("QString", "QJSValue", "QJSValue", "QJSValue", result=float)
    def getFloat(self, abstractMethod, arg1=None, arg2=None, arg3=None):

        try:
            abstract, method = self._splitAbstractMethod(abstractMethod)

            obj = app(abstract)
            result = getattr(obj, method)(*self._argsToPython(abstractMethod, *(arg1, arg2, arg3)))

            if isinstance(result, float):
                return result
            if isinstance(result, int):
                return float(result)
            return 0.0
        except Exception as e:
            self.error.emit(QError(e))
            return 0.0

    @pyqtSlot("QString", result=int)
    @pyqtSlot("QString", "QJSValue", result=int)
    @pyqtSlot("QString", "QJSValue", "QJSValue", result=int)
    @pyqtSlot("QString", "QJSValue", "QJSValue", "QJSValue", result=int)
    def getInt(self, abstractMethod, arg1=None, arg2=None, arg3=None):

        try:
            abstract, method = self._splitAbstractMethod(abstractMethod)

            obj = app(abstract)
            result = getattr(obj, method)(*self._argsToPython(abstractMethod,*(arg1, arg2, arg3)))

            if isinstance(result, float):
                return int(result)
            if isinstance(result, int):
                return result
            return 0
        except Exception as e:
            self.error.emit(QError(e))
            return 0

    @pyqtSlot("QString", result='QString')
    @pyqtSlot("QString", "QJSValue", result='QString')
    @pyqtSlot("QString", "QJSValue", "QJSValue", result='QString')
    @pyqtSlot("QString", "QJSValue", "QJSValue", "QJSValue", result='QString')
    def getString(self, abstractMethod, arg1=None, arg2=None, arg3=None):

        try:
            abstract, method = self._splitAbstractMethod(abstractMethod)

            obj = app(abstract)
            result = getattr(obj, method)(*self._argsToPython(abstractMethod,*(arg1, arg2, arg3)))

            if isinstance(result, str):
                return result

            return str(result)
        except Exception as e:
            self.error.emit(QError(e))
            return ''

    @pyqtSlot("QString", result=bool)
    @pyqtSlot("QString", "QJSValue", result=bool)
    @pyqtSlot("QString", "QJSValue", "QJSValue", result=bool)
    @pyqtSlot("QString", "QJSValue", "QJSValue", "QJSValue", result=bool)
    def getBool(self, abstractMethod, arg1=None, arg2=None, arg3=None):

        try:
            abstract, method = self._splitAbstractMethod(abstractMethod)

            obj = app(abstract)
            result = getattr(obj, method)(*self._argsToPython(abstractMethod,*(arg1, arg2, arg3)))

            if isinstance(result, bool):
                return result

            return bool(result)
        except Exception as e:
            self.error.emit(QError(e))
            return False

    @pyqtSlot("QString", result="QVariantMap")
    @pyqtSlot("QString", "QJSValue", result="QVariantMap")
    @pyqtSlot("QString", "QJSValue", "QJSValue", result="QVariantMap")
    @pyqtSlot("QString", "QJSValue", "QJSValue", "QJSValue", result="QVariantMap")
    def getDict(self, abstractMethod, arg1=None, arg2=None, arg3=None):

        try:
            abstract, method = self._splitAbstractMethod(abstractMethod)

            obj = app(abstract)
            result = getattr(obj, method)(*self._argsToPython(abstractMethod,*(arg1, arg2, arg3)))

            if result is None:
                return None

            if self._isInstanceOfClass(result):
                return self._instanceToDict(result)

            for key in result:
                result[key] = self._toQml(result[key])

            return result
        except Exception as e:
            self.error.emit(QError(e))
            return {}

    @pyqtSlot("QString", result='QVariantList')
    @pyqtSlot("QString", "QJSValue", result='QVariantList')
    @pyqtSlot("QString", "QJSValue", "QJSValue", result='QVariantList')
    @pyqtSlot("QString", "QJSValue", "QJSValue", "QJSValue", result='QVariantList')
    def getList(self, abstractMethod, arg1=None, arg2=None, arg3=None):

        try:
            abstract, method = self._splitAbstractMethod(abstractMethod)

            obj = app(abstract)
            result = getattr(obj, method)(*self._argsToPython(abstractMethod,*(arg1, arg2, arg3)))

            if result is None:
                return None

            items = []
            for item in result:
                items.append(self._toQml(item))

            return items
        except Exception as e:
            self.error.emit(QError(e))
            return []

    @pyqtSlot("QString", result='QVariant')
    @pyqtSlot("QString", "QJSValue", result='QVariant')
    @pyqtSlot("QString", "QJSValue", "QJSValue", result='QVariant')
    @pyqtSlot("QString", "QJSValue", "QJSValue", "QJSValue", result='QVariant')
    def getNativeObject(self, abstractMethod, arg1=None, arg2=None, arg3=None):

        try:
            try:
                abstract, method = self._splitAbstractMethod(abstractMethod)
            except ValueError:
                return app(abstractMethod)

            obj = app(abstract)
            return getattr(obj, method)(*self._argsToPython(abstractMethod,*(arg1, arg2, arg3)))
        except Exception as e:
            self.error.emit(QError(e))
            return None

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
        elif qJsValue.isObject():
            #print("Returning variant from object")
            return qJsValue.toVariant()
        raise TypeError("Nothing matching type found")

    def _toQml(self, pyValue):

        if isinstance(pyValue, dict):
            return pyValue
        if self._isInstanceOfClass(pyValue):
            return self._instanceToDict(pyValue)

        return pyValue

    def _isInstanceOfClass(self, value):
        return hasattr(value, '__dict__')

    def _instanceToDict(self, value):
        result = {}
        for key in value.__dict__:
            if not key[0] == '_':
                result[key] = value.__dict__[key]

        result['__class'] = str(value.__module__) + '.' + (value.__class__.__name__)
        return result