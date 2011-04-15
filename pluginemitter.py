'''
Created on 01.02.2010

@author: michi
'''
from ems.baseplugin import BasePlugin

class PluginEmitter(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.__pluginRegistry = {}
        self.__pluginNamesOrdered = []
        self.__pluginsForEventName = {}
    
    def registerPlugin(self,name,plugin):
        if not isinstance(plugin, BasePlugin):
            raise TypeError("The Plugin has to be instance of ems.baseplugin.BasePlugin")
        if self.__pluginRegistry.has_key(name):
            raise KeyError("The Plugin %s is already registered" % name)
        plugin.emitter = self
        self.__pluginRegistry[name] = plugin
        self.__pluginNamesOrdered.append(name)
    
    def registerForEventName(self,eventName,method):
        if not callable(method):
            raise TypeError("The method is not callable")
        if not self.__pluginsForEventName.has_key(eventName):
            self.__pluginsForEventName[eventName] = []
        self.__pluginsForEventName[eventName].append(method)
    
    def getPlugin(self,name):
        if self.__pluginRegistry.has_key(name):
            return self.__pluginRegistry[name]
        raise KeyError("The Plugin %s is not registred" % name)
    
    def notify(self,caller,eventName,params):
        for name in self.__pluginNamesOrdered:
            self.__pluginRegistry[name].notify(caller,eventName,params)
        if self.__pluginsForEventName.has_key(eventName):
            for method in self.__pluginsForEventName[eventName]:
                method(caller,eventName,params)        