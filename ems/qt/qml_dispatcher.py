
import inspect

from ems.event.hook import EventHook

class endpoint(object):

    handlers = {}

    def __init__(self, routeName):
        self.routeName = routeName

    def __call__(self, func):
        endpoint.handlers[self.routeName] = func
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

class QmlDispatcher(object):

    def __init__(self, qmlEngine, componentAdder):
        self._engine = qmlEngine
        self.requested = EventHook()
        self.handlerCreated = EventHook()
        #self.requested += self._dispatchToHandler
        self.itemAdded = EventHook()
        self.componentAdder = componentAdder
        self.handlerCreator = lambda c: c()

    def getEngine(self):
        return self._engine

    def setEngine(self, engine):
        self._engine = engine

    engine = property(getEngine, setEngine)

    def show(self, component, routeName):
        return self.componentAdder(self.engine, component, routeName)

    def dispatch(self, routeName):

        component = self.requested.fire(self, routeName)

        if component:
            item = self.show(component, routeName)
            self.itemAdded.fire(routeName, item)
            return item

        obj, method  = self._createHandler(routeName)

        if not obj:
            print("No handler created a component for routeName: {0}".format(routeName))
            return

        component = getattr(obj, method)(self.engine, routeName)

        item = self.show(component, routeName)

        self.itemAdded.fire(routeName, item)

        if hasattr(obj, 'bootItem'):
            getattr(obj, 'bootItem')(routeName, item)

        return item

    def bootItem(self, item, routeName):
        pass

    def _showContents(self, engine, component, routeName):
        engine.show(component, routeName)

    def _createHandler(self, routeName):

        if routeName not in endpoint.handlers:
            return

        handler = endpoint.handlers[routeName]

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
