

from abc import ABCMeta,abstractmethod
from ems.ioc.container import Container
from ems.event.dispatcher import Dispatcher
from ems.eventhook import EventHook

class App(Container):

    def __init__(self):
        super(App, self).__init__()
        self._bootstrappers = [
            EventBootstrapper()
        ]
        self.path = ''
        self.argv = []

        self.starting = EventHook()
        self.started = EventHook()

        self.bootstrapping = EventHook()
        self.bootstrapped = EventHook()

    def addBootstrapper(self, bootstrapper):
        if not isinstance(bootstrapper, Bootstrapper):
            raise TypeError('Bootstrapper has to be Bootstrapper (abc)')
        self._bootstrappers.append(bootstrapper)

    def getBootstrappers(self):
        return self._bootstrappers;

    bootstrappers = property(getBootstrappers)

    def start(self, path, argv):

        self.path = path
        self.argv = argv
        self.starting.fire(argv)

        for bootstrapper in self._bootstrappers:
            self.bootstrapping.fire(bootstrapper)
            bootstrapper.bootstrap(self)
            self.bootstrapped.fire(bootstrapper)

        self.started.fire(self)

class Bootstrapper(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def bootstrap(self, app):
        pass

class EventBootstrapper(Bootstrapper):

    def __init__(self):
        self._dispatcher = Dispatcher()

    def bootstrap(self, app):
        self.app = app
        app.alias('events', Dispatcher)
        app.share('events', self._dispatcher)
        self._injectEventForwards(app)

    def _injectEventForwards(self, app):
        app.bootstrapping += self.fireBootstrapping
        app.bootstrapped += self.fireBootstrapped
        app.started += self.fireStarted

    def fireBootstrapping(self, bootstrapper):
        self._dispatcher.fire('bootstrapping', bootstrapper)

    def fireBootstrapped(self, bootstrapper):
        self._dispatcher.fire('bootstrapped', bootstrapper)

    def fireStarted(self, app):
        self._dispatcher.fire('app.started', app)