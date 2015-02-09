'''
Created on 04.10.2012

@author: michi
'''
from PyQt4.QtCore import QObject, pyqtSignal

class ApplicationService(QObject):
    
    nameChanged = pyqtSignal(unicode)
    
    titleChanged = pyqtSignal(unicode)
    
    descriptionChanged = pyqtSignal(unicode)
    
    pollingIntervalChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self._name = u""
        self._title = u""
        self._description = u""
        self._pollingIntervall = 5000
    
    def isAutoStartEnabled(self):
        raise NotImplementedError("Please implement isAutoStartEnabled")
    
    def hasOwnTimer(self):
        raise NotImplementedError("Please implement hasOwnTimer")
    
    def name(self):
        return self._name
    
    def setName(self, name):
        if self._name == name:
            return
        self._name = name
        self.nameChanged(self._name)
    
    def title(self):
        return self._title
    
    def setTitle(self, title):
        if self._title == title:
            return
        self._title = title
        self.titleChanged.emit(self._title)
    
    def description(self):
        return self._description
    
    def setDescription(self, description):
        if self._description == description:
            return
        self._description = description
        self.descriptionChanged.emit(self._description)
    
    def pollingInterval(self):
        return self._pollingIntervall
    
    def setPollingInterval(self, interval):
        if self._pollingIntervall == interval:
            return
        self._pollingIntervall = interval
        self.pollingIntervalChanged.emit(self._pollingIntervall)
    
    def trigger(self):
        raise NotImplementedError("Please implement trigger")
    
    def start(self):
        raise NotImplementedError("Please implement start")
    
    def stop(self):
        raise NotImplementedError("Please implement stop")