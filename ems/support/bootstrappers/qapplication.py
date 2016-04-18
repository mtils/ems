
import os.path
from abc import ABCMeta, abstractmethod

from six import add_metaclass

from ems.app import Bootstrapper

@add_metaclass(ABCMeta)
class QApplicationBootstrapper(Bootstrapper):

    def __init__(self):
        self.app = None
        self._win = None

    def bootstrap(self, app):

        self.app = app

        self.setupPaths()

        self.app.booted += self.createWindowAndFireGuiReady

        self.hookIntoStartEvents(app)

    def createWindowAndFireGuiReady(self, app):
        self.win = self.createHiddenMainWindow(app)
        app['events'].fire('gui.ready')

    @abstractmethod
    def createHiddenMainWindow(self, app):
        raise NotImplementedError()

    def showMainWindow(self, *args):
        self.win.show()

    def hideMainWindow(self):
        self.win.hide()

    def setupPaths(self):
        pass

    def hookIntoStartEvents(self, app):

        if app.bound('auth'):
            app['events'].listen('auth.loggedIn', self.showMainWindow)
            app['events'].listen('auth.loggedOut', self.hideMainWindow)
            return

        app['events'].listen('gui.ready', self.showMainWindow)