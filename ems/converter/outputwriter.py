'''
Created on 24.10.2010

@author: michi
'''

from ems.converter import iomodule
from abc import abstractmethod

class OutputWriter(iomodule.IoModule):
    '''
    classdocs
    '''

    def getTarget(self):
        return self.__target

    def setTarget(self, value):
        self.__target = value

    target = property(getTarget, setTarget, None, "target's docstring")
    
    @abstractmethod
    def dryRun(self,isDryRun=True):
        pass
    
    @abstractmethod
    def createElement(self,name,params={},namespace=None):
        pass
    
    @abstractmethod
    def setElementValue(self,value):
        pass
    
    def endElement(self):
        pass
    
    def notify(self,eventType):
        if eventType == self.startProcess:
            if not self.__target:
                raise AttributeError("No target set")
            if hasattr(self, 'init') and callable(getattr(self,'init')):
                self.init()