
from ems.app import Bootstrapper
from ems.gui.interfaces.dialogs import AbstractFileDialog, FileDialog, ProxyFileDialog
from ems.qt4.gui.dialogs import Qt4FileDialog

class StandardDialogBootstrapper(Bootstrapper):

    def bootstrap(self, app):
        app.bind(AbstractFileDialog, Qt4FileDialog)
        app.bind(FileDialog, ProxyFileDialog)