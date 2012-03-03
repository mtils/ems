'''
Created on 01.02.2010

@author: michi
'''
from abc import ABCMeta,abstractmethod

class BasePlugin(object):
    '''
    classdocs
    '''
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def notify(self,caller,eventName,params):
        pass

    def getEmitter(self):
        return self.__emitter

    def setEmitter(self, value):
        if not isinstance(value, PluginEmitter):
            raise TypeError("The Emitter has to by class or subclass of ems.pluginemitter.PluginEmitter")
        self.__emitter = value

    def delEmitter(self):
        del self.__emitter

    emitter = property(getEmitter, setEmitter, delEmitter, "emitter's docstring")

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
        self.__callable2PluginName = {}
        self.__disabledPluginNames = set()
    
    
    def registerPlugin(self,name,plugin):
        if not isinstance(plugin, BasePlugin):
            raise TypeError("The Plugin has to be instance of ems.pluginemitter.BasePlugin")
        if self.__pluginRegistry.has_key(name):
            raise KeyError("The Plugin %s is already registered" % name)
        plugin.emitter = self
        self.__pluginRegistry[name] = plugin
        self.__pluginNamesOrdered.append(name)
    
    def enablePlugin(self, pluginName):
        try:
            self.__disabledPluginNames.remove(pluginName)
            return True
        except KeyError:
            return False
    
    def disablePlugin(self, pluginName):
        self.__disabledPluginNames.add(pluginName)
        return True
    
    def registerForEventName(self,eventName,method, pluginName=None):
        if not callable(method):
            raise TypeError("The method is not callable")
        
        if not self.__pluginsForEventName.has_key(eventName):
            self.__pluginsForEventName[eventName] = []
        self.__pluginsForEventName[eventName].append(method)
        
        if pluginName is not None:
            if not self.__callable2PluginName.has_key(method):
                self.__callable2PluginName[method] = pluginName
    
    def getPlugin(self,name):
        if self.__pluginRegistry.has_key(name):
            return self.__pluginRegistry[name]
        raise KeyError("The Plugin %s is not registred" % name)
    
    def notify(self,caller,eventName,params):
        for name in self.__pluginNamesOrdered:
            if name not in self.__disabledPluginNames:
                self.__pluginRegistry[name].notify(caller,eventName,params)
        if self.__pluginsForEventName.has_key(eventName):
            for method in self.__pluginsForEventName[eventName]:
                if self.__callable2PluginName.has_key(method):
                    pluginName = self.__callable2PluginName[method]
                    if pluginName in self.__disabledPluginNames:
                        continue
                method(caller,eventName,params)
    
    def eventNameHasSubscriber(self, eventName):
        if self.__pluginsForEventName.has_key(eventName):
            for method in self.__pluginsForEventName[eventName]:
                if self.__callable2PluginName.has_key(method):
                    pluginName = self.__callable2PluginName[method]
                    if pluginName in self.__disabledPluginNames:
                        continue
                return True
        return False