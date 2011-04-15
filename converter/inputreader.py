'''
Created on 24.10.2010

@author: michi
'''

from ems.converter import iomodule
from abc import ABCMeta,abstractmethod

class DataNotFoundException(LookupError):
    pass

class DataCorruptException(IOError):
    pass

class XPathNotImplementedError(NotImplementedError):
    pass

class InputReaderPlugin:
    def notifyProgress(self):
        pass
    def notifyStateChange(self,state):
        pass

class InputReader(iomodule.IoModule):

    def __init__(self,options=None):
        self._plugin = None
        super(InputReader, self).__init__(options)
         
    def getSource(self):
        return self.__source

    def setSource(self, value):
        self.__source = value
        
    source = property(getSource, setSource, None, "source's docstring")
    
    def notify(self,eventType):
        if eventType == self.startProcess:
            if not self.source:
                raise AttributeError("No source set")
            if hasattr(self, 'init') and callable(getattr(self,'init')):
                self.init()
        if self._plugin is not None:
            self._plugin.notifyStateChange(eventType)
            
    def setPlugin(self,plugin):
        if not isinstance(plugin,InputReaderPlugin):
            raise TypeError("Plugin has to be instance of InputReaderPlugin")
        self._plugin = plugin
                
    @abstractmethod
    def getFieldNames(self):
        return []
    
    @abstractmethod
    def __len__(self):
        pass