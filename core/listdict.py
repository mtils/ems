'''
Created on 24.11.2010

@author: michi
'''
from ems.core.mirrordict import MirrorDict

class ListDict(list):
    
    def __init__(self,listObject=[],nameMap={}):
        for item in listObject:
            self.append(item)
        self.nameMap = nameMap

    def getNameMap(self):
        return self.__nameMap

    def setNameMap(self, value):
        if isinstance(value, MirrorDict):
            self.__nameMap = value
        elif isinstance(value, dict):
            self.__nameMap = MirrorDict(value)
        else:
            raise TypeError("NameMap has to be Dict or MirrorDict")

    def delNameMap(self):
        del self.__nameMap

    nameMap = property(getNameMap, setNameMap, delNameMap, "The nameMap to map values to indexes")
            
    def __delitem__(self, key):
        if isinstance(key, int):
            return super(ListDict, self).__delitem__(key)
        if isinstance(key, basestring):
            return self.__delitem__(self.__nameMap.index(key))
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return super(ListDict, self).__getitem__(key)
        if isinstance(key, basestring):
            return self.__getitem__(self.__nameMap.index(key))
        
    def __setitem__(self, key, value):
        if isinstance(key, int):
            return super(ListDict, self).__setitem__(key,value)
        if isinstance(key, basestring):
            return self.__setitem__(self.__nameMap.index(key))
    
    def keys(self):
        names = []
        for num in xrange(0,len(self)):
            names.append(self.__nameMap[num])
        return names
    
    def has_key(self,key):
        if isinstance(key, int):
            length = len(self)
            if length:
                return (key >= 0) and (key < length)
            return False
        if isinstance(key, basestring):
            return self.__nameMap.has_value(key)
    
    def items(self):
        return [(self.__nameMap[num],self.__getitem__(num)) for num in xrange(0,len(self))]