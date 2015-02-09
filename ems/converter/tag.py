'''
Created on 25.10.2010

@author: michi
'''
from ems.converter.plugin import Plugin
from ems.xml.xml2dict import createNode
from abc import ABCMeta,abstractmethod,abstractproperty

class MappingException(SyntaxError):
    pass
class AttributeException(SyntaxError):
    pass
class ElementException(SyntaxError):
    pass

class Tag(Plugin):
    '''
    classdocs
    '''
    __metaclass__ = ABCMeta
    
    @abstractproperty
    def __str__(self):
        raise NotImplementedError("You have to implement a str overload")
    
    @abstractmethod
    def interpret(self,xmlDict,inputReader,outputWriter):
        pass
    
    def _createTagNode(self):
        return createNode()
    
    def _select(self,select,inputReader,outputWriter):
        tagNode = self._createTagNode()
        tagNode['tag'] = 'value-of'
        tagNode['attributes']['select'] = select
        return self.converter.interpretTag(tagNode,inputReader,outputWriter)
