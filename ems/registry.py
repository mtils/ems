'''
Created on 04.02.2011

@author: michi
'''
from singletonmixin import Singleton

class Registry(Singleton):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.__objectRegistry = {}
    
    def registerObject(self,name,object,throwExceptionIfExists=False):
        if self.__objectRegistry.has_key(name) and throwExceptionIfExists:
            raise KeyError("The Object %s is already registered" % name)
        self.__objectRegistry[name] = object
    
    def getObject(self,name):
        if self.__objectRegistry.has_key(name):
            return self.__objectRegistry[name]
        raise KeyError("The Object %s is not registred" % name)
    
    def __getattr__(self, key):
        try:
            return super(Registry, self).__getattr__(key)
        except AttributeError:
            return self.getObject(key)
    
    def __setattr__(self,key,val):
        if isinstance(key, basestring) and key.startswith("_Registry"):
            return super(Registry, self).__setattr__(key,val)
        return self.registerObject(key, val)
    
    def __delattr__(self,name):
        del self.__objectRegistry[name]
        return True
    
    def __getitem__(self,key):
        return self.getObject(key)
    
    def __setitem__(self,key,val):
        return self.registerObject(key, val)
    
    def __delitem__(self,key):
        return self.__delattr__(key)