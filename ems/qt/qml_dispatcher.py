
import inspect

from ems.event.hook import EventHook

class endpoint(object):

    handlers = {}

    def __init__(self, routeName):
        self.routeName = routeName

    def __call__(self, func):
        endpoint.handlers[self.routeName] = func
        return func

class QmlDispatcher(object):

    def __init__(self, qmlEngine, componentAdder):
        self._engine = qmlEngine
        self.requested = EventHook()
        self.handlerCreated = EventHook()
        self.requested += self._dispatchToHandler
        self.componentAdder = componentAdder
        self.handlerCreator = lambda c: c()

    def getEngine(self):
        return self._engine

    def setEngine(self, engine):
        self._engine = engine

    engine = property(getEngine, setEngine)

    def show(self, component, routeName):
        self.componentAdder(self.engine, component, routeName)

    def dispatch(self, routeName):
        component = self.requested.fire(self, routeName)
        if not component:
            print("No handler created a component for routeName: {0}".format(routeName))
            return
        self.show(component, routeName)

    def _showContents(self, engine, component, routeName):
        engine.show(component, routeName)

    def _dispatchToHandler(self, dispatcher, routeName):

        if routeName not in endpoint.handlers:
            return

        handler = endpoint.handlers[routeName]

        module = inspect.getmodule(handler)
        parentName = ".".join(handler.__qualname__.split('.')[:-1])

        parent = getattr(module, parentName)

        if not inspect.isclass(parent):
            return handler(self.engine, routeName)

        method = handler.__qualname__.split('.')[-1:][0]

        obj = self.handlerCreator(parent)

        self.handlerCreated.fire(obj)

        component = getattr(obj, method)(self.engine, routeName)

        return component