'''
Created on 17.02.2011

@author: michi
'''

import sys

from ems.errorplugin import ErrorPlugin
from ems.singletonmixin import Singleton

class ErrorHandler(Singleton):
    
    def __init__(self):
        '''
        Constructor
        '''
        self.__pluginRegistry = {}
        self.__pluginNamesOrdered = []
    
    def registerPlugin(self,name,plugin):
        if not isinstance(plugin, ErrorPlugin):
            text = "The Plugin has to be instance of ems.errorplugin.ErrorPlugin"
            raise TypeError(text)
        if self.__pluginRegistry.has_key(name):
            raise KeyError("The Plugin %s is already registered" % name)
        plugin.emitter = self
        self.__pluginRegistry[name] = plugin
        self.__pluginNamesOrdered.append(name)
    
    def getPlugin(self,name):
        if self.__pluginRegistry.has_key(name):
            return self.__pluginRegistry[name]
        raise KeyError("The Plugin %s is not registred" % name)
    
    def notify(self,excType,excValue,excTraceback):
        if not len(self.__pluginNamesOrdered):
            sys.__excepthook__(excType,excValue,excTraceback)
            return
        for name in self.__pluginNamesOrdered:
            result = self.__pluginRegistry[name].notify(excType,excValue,excTraceback)
            if result:
                return
              
    @staticmethod
    def registerErrorHook():
        sys.excepthook = ErrorHandler.handleException
        
    @staticmethod
    def handleException(excType,excValue,excTraceback):
        ErrorHandler.getInstance().notify(excType,excValue,excTraceback)