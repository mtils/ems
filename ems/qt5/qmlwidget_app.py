
import os.path
import sys

from PyQt5.QtWidgets import QApplication

from ems.util import platformName
from ems.app import App as BaseApp

class App(QApplication, BaseApp):
    
    def __init__(self, argv, path=None):
        '''
        Constructor
        '''
        kwargs = {
            'argv': sys.argv,
            'path': path
        }
        #print(kwargs)
        #super().__init__(argv, path=path)
        #super().__init__(argv)
        
        #super().__init__(**kwargs)
        BaseApp.__init__(self, argv, path)
        try:
            QApplication.__init__(self, argv)
        except TypeError:
            pass
        
        #QApplication.__init__(self, argv)
        #QApplication.__init__(self, [])

        self._services = {}
        self._serviceTimers = {}
        self._standardActions = {}
        self._widgetController = None

    def start(self, path, argv):
        BaseApp.start(self, path, argv)
        return QApplication.exec_()