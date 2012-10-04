'''
Created on 01.02.2010

@author: michi
'''
import os.path

from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QApplication

from ems.util import platformName

class MainApplication(QApplication):
    '''
    classdocs
    '''

    def __init__(self,argv,appPath=None):
        '''
        Constructor
        '''
        QApplication.__init__(self,argv)
        
        self._services = {}
        self._serviceTimers = {}

        if appPath is None:
            self.appPath = os.path.abspath(os.path.dirname(argv[0]))
        else:
            self.appPath = appPath
            
    def getRelativePath(self,path):
        rPath = path.replace(self.appPath, "")
        if rPath.startswith(os.path.sep):
            return rPath[1:]
        return rPath
    
    def getAbsolutePath(self, path):
        if os.path.isabs(path):
            return path
        if not path.startswith(os.path.sep):
            return os.path.join(self.appPath, path)
        return path
    
    def platform(self):
        return platformName()
    
    def _startOrCreateTimer(self, serviceName):
        if self._services[serviceName].hasOwnTimer():
            return
        if not self._serviceTimers.has_key(serviceName):
            self._serviceTimers[serviceName] = QTimer()
            self._serviceTimers[serviceName].timeout.connect(self._services[serviceName].trigger)
        
        self._serviceTimers[serviceName].start(self._services[serviceName].pollingInterval())
        
    
    def addService(self, name, service):
        if self._services.has_key(name):
            raise AttributeError("The service with the name '{0}' already exists".format(name))
        self._services[name] = service
        
        if self._services[name].isAutoStartEnabled():
            self.startService(name)
    
    def removeService(self, name):
        if not self._services.has_key(name):
            raise AttributeError("The service with the name '{0}' does not exist".format(name))
        self._services[name].stop()
        self._services[name].deleteLater()
    
    def startService(self, name):
        if not self._services.has_key(name):
            raise AttributeError("The service with the name '{0}' does not exist".format(name))
        self._services[name].start()
        self._startOrCreateTimer(name)
    
    def services(self):
        return self._services.values()
            
    
    def stopService(self, name):
        if not self._services.has_key(name):
            raise AttributeError("The service with the name '{0}' does not exist".format(name))
        self._services[name].start()