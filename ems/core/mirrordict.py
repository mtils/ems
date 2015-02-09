'''
Created on 24.11.2010

@author: michi
'''
class MirrorDict(object):
    def __init__(self,dictionary={}):
        self.__original = dictionary
        self.__mirror = {}
        for key,value in dictionary.items():
            self.__mirror[value] = key
    
    def __contains__(self, key):
        if key in self.__original:
            return True
        if key in self.__mirror:
            return True
    
    def __delitem__(self, key):
        value = self.__original[key]
        del self.__original[key]
        del self.__mirror[value]
    
    def __getitem__(self, key):
        return self.__original[key]
        
    def __setitem__(self, key, value):
        if key in self.__original:
            self.__delitem__(key)
        self.__original[key] = value
        self.__mirror[value] = key
    
    def index(self,value):
        return self.__mirror[value]
    
    def has_key(self,key):
        return self.__original.has_key(key)
    
    def has_value(self,value):
        return self.__mirror.has_key(value)
        
    def __len__(self):
        return len(self.__original)
    
    def __iter__(self):
        return iter(self.__original)
    