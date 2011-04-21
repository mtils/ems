#coding=utf-8
'''
Created on 21.04.2011

@author: michi
'''
class AttributeProxyR(object):
    def __init__(self, baseObject):
        self.__baseObject = baseObject
        
    def getBaseObject(self):
        return self.__baseObject
    
    def setBaseObject(self, baseObject):
        self.__baseObject = baseObject
    
    def delBaseObject(self):
        self.__baseObject = None
        
    def __getattr__(self,key):
        try:
            return object.__getattribute__(self,key)
        except AttributeError:
            return self.__baseObject.__getattribute__(key)
    
    baseObject = property(getBaseObject,setBaseObject,delBaseObject,'')