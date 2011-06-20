'''
Created on 20.06.2011

@author: michi
'''

from decorator import OrmDecorator

class OrmBaseObject(object):
    def __init__(self,initVals={},**kwargs):
        for key in initVals:
            self.__setattr__(key,initVals[key])
        for key in kwargs:
            self.__setattr__(key,kwargs[key])
        self._decoratorObj = None
    
    def ormDecorator(self):
        if not hasattr(self, '_decoratorObj') or self._decoratorObj is None:
            self._decoratorObj = OrmDecorator(self)
        return self._decoratorObj