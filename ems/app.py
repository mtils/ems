
import os.path
from abc import ABCMeta,abstractmethod

from ems.ioc.container import Container
from ems.event.dispatcher import Dispatcher
from ems.event.hook import EventHook

class App(Container):

    _shortCut = None

    def __init__(self, argv, path=None, **kwargs):
        kwargs['argv'] = argv

        super(App, self).__init__(**kwargs)

        self._bootstrappers = [
            EventBootstrapper()
        ]
        self.argv = argv
        self.path = path

        self.starting = EventHook()
        self.started = EventHook()

        self.bootstrapping = EventHook()
        self.bootstrapped = EventHook()
        self.booted = EventHook()

        App._shortCut = self.appInstance

        self._setPath(argv, path)

        self.shareInstance(App, self)

    def addBootstrapper(self, bootstrapper):
        if not isinstance(bootstrapper, Bootstrapper):
            raise TypeError('Bootstrapper has to be Bootstrapper (abc)')
        self._bootstrappers.append(bootstrapper)

    def getBootstrappers(self):
        return self._bootstrappers;

    bootstrappers = property(getBootstrappers)

    def start(self, path=None, argv=None):

        self.path = path
        self.argv = argv
        self.starting.fire(argv)

        for bootstrapper in self._bootstrappers:
            self.bootstrapping.fire(bootstrapper)
            bootstrapper.bootstrap(self)
            self.bootstrapped.fire(bootstrapper)

        self.booted.fire(self)

        self.started.fire(self)

    def appInstance(self, abstract=None, *args, **kwargs):

        if abstract is None:
            return self

        return self.make(abstract, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.appInstance(*args, **kwargs)

    def _setPath(self, argv, path):
        self.path = path if path else os.path.abspath(os.path.dirname(argv[0]))

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
        app.shareInstance('events', self._dispatcher)
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

def app(abstract=None, *args, **kwargs):
    return App._shortCut(abstract, *args, **kwargs)

def relative_path(path):

    appPath = app_path()

    if not path.startswith(appPath):
        return path

    rPath = path.replace(appPath, "")
    if rPath.startswith(os.path.sep):
        return rPath[1:]
    return rPath

def absolute_path(path):

    if os.path.isabs(path):
        return path

    if not path.startswith(os.path.sep):
        return os.path.join(app_path(), path)

    return path

def app_path(subPath=None):

    if subPath is None:
        return app().path

    return absolute_path(subPath)