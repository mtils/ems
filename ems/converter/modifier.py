'''
Created on 25.10.2010

@author: michi
'''
from ems.converter.plugin import Plugin
from abc import ABCMeta,abstractmethod,abstractproperty
class ModifierException(SyntaxError):
    pass
class Modifier(Plugin):
    '''
    classdocs
    '''
    __metaclass__ = ABCMeta
    
    @abstractproperty
    def __str__(self):
        raise NotImplementedError("You have to implement a str overload")
    
    @abstractmethod
    def interpret(self,params):
        pass
