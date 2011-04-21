#coding=utf-8
'''
Created on 21.04.2011

@author: michi
'''
class AttributeProxyR(object):
    
    def __init__(self, baseObject):
        self._baseObject = baseObject
        
    def getBaseObject(self):
        return self._baseObject
    
    def setBaseObject(self, baseObject):
        self._baseObject = baseObject
    
    def delBaseObject(self):
        self._baseObject = None
        
    def __getattr__(self,key):
        try:
            return object.__getattribute__(self,key)
        except AttributeError:
            return self._baseObject.__getattribute__(key)
    
    baseObject = property(getBaseObject,setBaseObject,delBaseObject,'')