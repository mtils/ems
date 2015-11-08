
import os.path

from PyQt5.QtWidgets import QApplication

from ems.util import platformName
from ems.app import App as BaseApp

class App(QApplication, BaseApp):
    
    def __init__(self, **kwargs):#argv, appPath=None):
        '''
        Constructor
        '''
        super().__init__(**kwargs)
        #QApplication.__init__(self, argv)
        #BaseApp.__init__(self, argv, appPath)

        self._services = {}
        self._serviceTimers = {}
        self._standardActions = {}
        self._widgetController = None

    def start(self, path, argv):
        BaseApp.start(self, path, argv)
        return QApplication.exec_()