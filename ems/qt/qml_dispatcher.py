
import inspect

import os.path
from ems.event.hook import EventHook

class configures(object):

    handlers = {}

    def __init__(self, routeName):
        self.routeName = routeName

    def __call__(self, func):
        configures.handlers[self.routeName] = func
        return func

class QmlController(object):

    def bootItem(self, routeName, item):

        methodName = routeName.split('.')[-1:][0]
        bootMethod = "{0}{1}".format('boot', methodName.capitalize())
        if hasattr(self, bootMethod):
            getattr(self, bootMethod)(item)

class _FakeHandler(object):

    def __init__(self, handler):
        self.handler = handler

    def invoke(self, *args, **kwargs):
        self.handler(*args, **kwargs)

class QmlFileLoader(object):

    def __init__(self, qmlPath):
        self.qmlPath = qmlPath

    def fileName(self, routeName):
        pathSplit = routeName.split('.')
        return "{0}.qml".format(os.path.join(self.qmlPath, 'resources', *pathSplit))

class QmlDispatcher(object):

    def __init__(self, componentCreator, componentAdder, fileLoader):
        self._componentCreator = componentCreator
        self.dispatching = EventHook()
        self.handlerCreated = EventHook()
        self._fileLoader = fileLoader
        #self.requested += self._dispatchToHandler
        self.itemAdded = EventHook()
        self.itemBooted = EventHook()
        self.componentAdder = componentAdder
        self.handlerCreator = lambda c: c()

    def show(self, component, routeName):
        return self.componentAdder(component, routeName)

    def dispatch(self, routeName):

        qmlFile = self._fileLoader.fileName(routeName)

        component = self.dispatching.fire(self, qmlFile, routeName)

        if not component:
            try:
                component = self._componentCreator(qmlFile, routeName)
            except RuntimeError as e:
                self._handleQmlError(routeName, e)
                return


        item = self.show(component, routeName)
        self.itemAdded.fire(routeName, item)

        obj, method  = self._createHandler(routeName)


        if not obj:
            print("No handler found for routeName: {0}".format(routeName))
            return

        getattr(obj, method)(component, item)

        self.itemBooted.fire(routeName, component, item)

        return item

    def _createHandler(self, routeName):

        if routeName not in configures.handlers:
            return (None, None)

        handler = configures.handlers[routeName]

        clazz = self._handlerClass(handler)

        if not clazz:
            return (_FakeHandler(handler), 'invoke')

        method = handler.__qualname__.split('.')[-1:][0]

        obj = self.handlerCreator(clazz)

        self.handlerCreated.fire(obj)

        return (obj, method)

    def _handlerClass(self, handler):

        module = inspect.getmodule(handler)
        parentName = ".".join(handler.__qualname__.split('.')[:-1])

        parent = getattr(module, parentName)

        if inspect.isclass(parent):
            return parent

    def _handleQmlError(self, routeName, exception):

        if len(exception.args) < 2:
            print("Creating component '{0}' raised error '{1}'".format(routeName, exception))

        print("Creating component '{0}' raised the following errors:".format(routeName))

        for error in exception.args[1]:
            print(error.toString())

