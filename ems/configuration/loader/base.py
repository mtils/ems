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

    def __init__(self,fileName=''):
        '''
        Constructor
        '''
        self.configObj = None
        self.__fileName = fileName

    def getFileName(self):
        return self.__fileName


    def setFileName(self, value):
        self.__fileName = value


    def delFileName(self):
        del self.__fileName

    def load(self,fileName=''):
        if not len(fileName):
            fileName = self.__fileName
        return self._load(fileName)
    
    def save(self,fileName=''):
        if not len(fileName):
            fileName = self.__fileName
        return self._save(fileName)
    
    @abstractmethod
    def _load(self,fileName):
        pass
    
    @abstractmethod
    def _save(self,fileName):
        pass
    
    fileName = property(getFileName, setFileName, delFileName, "fileName's docstring")
        
    
        