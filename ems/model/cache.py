'''
Created on 04.07.2011

@author: michi
'''
from ems.singletonmixin import Singleton

class SessionGetterNotSetError(Exception):
    pass

class ModelCache(Singleton):
    entries = {}
    sessionGetter = None
    def __init__(self):
        pass
        
    def setEntry(self, name, val):
        self.entries[name] = val
    
    def getEntry(self, name):
        if self.sessionGetter is None:
            raise SessionGetterNotSetError("Please assign a sessiongetter callable")
        return self.entries[name]