
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
            component = self._componentCreator(qmlFile, routeName)


        item = self.show(component, routeName)
        self.itemAdded.fire(routeName, item)

        #if component:
            #item = self.show(component, routeName)
            #self.itemAdded.fire(routeName, item)
            #return item

        #print(self._fileLoader.fileName(routeName))

        obj, method  = self._createHandler(routeName)

        if not obj:
            print("No handler created a component for routeName: {0}".format(routeName))
            return

        getattr(obj, method)(item, routeName)

        #item = self.show(component, routeName)

        self.itemBooted.fire(routeName, item)

        #if hasattr(obj, 'bootItem'):
            #getattr(obj, 'bootItem')(routeName, item)

        return item

    def _createHandler(self, routeName):

        if routeName not in configures.handlers:
            return

        handler = configures.handlers[routeName]

        clazz = self._handlerClass(handler)

        if not clazz:
            return (_FakeHandler(handler), 'invoke')

        method = handler.__qualname__.split('.')[-1:][0]

        obj = self.handlerCreator(clazz)

        self.handlerCreated.fire(obj)

        return (obj, method)

        component = getattr(obj, method)(self.engine, routeName)

        return component

    def _handlerClass(self, handler):

        module = inspect.getmodule(handler)
        parentName = ".".join(handler.__qualname__.split('.')[:-1])

        parent = getattr(module, parentName)

        if inspect.isclass(parent):
            return parent
