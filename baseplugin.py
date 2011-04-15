'''
Created on 28.11.2010

@author: michi
'''

from abc import ABCMeta,abstractmethod

import ems.pluginemitter

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
        if not isinstance(value, ems.pluginemitter.PluginEmitter):
            raise TypeError("The Emitter has to by class or subclass of ems.pluginemitter.PluginEmitter")
        self.__emitter = value

    def delEmitter(self):
        del self.__emitter

    emitter = property(getEmitter, setEmitter, delEmitter, "emitter's docstring")
    