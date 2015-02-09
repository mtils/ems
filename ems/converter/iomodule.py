'''
Created on 24.10.2010

@author: michi
'''
from abc import ABCMeta,abstractmethod
from ems.core.optionsproperty import OptionsProperty
from ems.converter.plugin import Plugin

class IoModule(Plugin,OptionsProperty):
    '''
    classdocs
    '''
    __metaclass__ = ABCMeta
    
    file = 1
    db = 2
    interface = 3
    
    def __init__(self,options={}):
        '''
        Constructor
        '''
        self.options = options
        self.supportedMimeTypes = []
        self.__charset = ""
        self.notify(self.init)
    
    def set_charset(self,charset):
        self.__charset = charset
        return
        
    def get_charset(self):
        return self.__charset
    
    def del_charset(self):
        self.__charset = None
    
    charset = property(get_charset, set_charset, del_charset, "charset's docstring")
    
    @abstractmethod
    def select(self,xpath):
        pass
    
    @abstractmethod
    def getType(self):
        return
    
    @abstractmethod
    def getCurrentPosition(self):
        return
    
    @abstractmethod
    def getSupportedMimeTypes(self):
        return
