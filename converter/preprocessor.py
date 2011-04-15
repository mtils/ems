'''
Created on 25.10.2010

@author: michi
'''
from ems.converter.plugin import Plugin
from ems.xml.xml2dict import createNode
from abc import ABCMeta,abstractmethod

class PreProcessor(Plugin):
    '''
    classdocs
    '''
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def interpret(self,xmlDict):
        pass
    
    def _createTagNode(self):
        return createNode()
