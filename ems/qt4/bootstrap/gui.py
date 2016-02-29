
from six import u

from ems.app import Bootstrapper
from ems.gui.interfaces.dialogs import AbstractFileDialog, FileDialog, ProxyFileDialog
from ems.qt4.gui.dialogs import Qt4FileDialog

from PyQt4.QtCore import QDir

class StandardDialogBootstrapper(Bootstrapper):

    def bootstrap(self, app):
        self.app = app
        app.bind(AbstractFileDialog, Qt4FileDialog)
        app.bind(FileDialog, self.createProxyFileDialog)

    def createProxyFileDialog(self):
        proxy = self.app(ProxyFileDialog)
        proxy.fallbackDirectory = u(QDir.homePath())
        return proxy