'''
Created on 28.11.2010

@author: michi
'''

from abc import ABCMeta,abstractmethod

import ems.errorhandler

class ErrorPlugin(object):
    '''
    classdocs
    '''
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def notify(self,caller,eventName,params):
        pass

    def getHandler(self):
        return self.__handler

    def setHandler(self, value):
        if not isinstance(value, ems.errorhandler):
            raise TypeError("The Errorhandler has to by class or subclass of ems.errorhandler")
        self.__handler = value

    def delHandler(self):
        del self.__handler

    handler = property(getHandler, setHandler, delHandler, "emitter's docstring")
    