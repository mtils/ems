'''
Created on 20.06.2011

@author: michi
'''

from decorator import OrmDecorator #@UnresolvedImport

class OrmBaseObject(object):
    def __init__(self,initVals={},**kwargs):
        for key in initVals:
            self.__setattr__(key,initVals[key])
        for key in kwargs:
            self.__setattr__(key,kwargs[key])
        self._decoratorObj = None
    
    @classmethod
    def __ormDecorator__(cls):
        if not hasattr(cls, '__decoratorObj__') or cls.__decoratorObj__ is None:
            cls.__decoratorObj__ = OrmDecorator(cls)
        return cls.__decoratorObj__