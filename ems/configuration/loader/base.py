'''
Created on 10.02.2011

@author: michi
'''
from abc import ABCMeta,abstractmethod

class CfgFileNotFoundError(IOError):
    pass
class CfgFileInvalidError(SyntaxError):
    pass
class CfgFileFormatUnknownError(LookupError):
    pass
class CfgFileNotWritableError(IOError):
    pass
class CfgFileAccessDeniedError(IOError):
    pass

class Base(object):

    '''
    classdocs
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def load(self, fileName, configObj):
        pass

    @abstractmethod
    def save(self, fileName, configObj):
        pass
