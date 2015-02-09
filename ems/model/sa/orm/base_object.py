'''
Created on 20.06.2011

@author: michi
'''
from sqlalchemy.orm import object_mapper, RelationshipProperty 
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
    
    def __serialize__(self):
        return ""
    
    @staticmethod
    def createRelatedObject(obj, propertyName):
        mp = object_mapper(obj)
        prop = mp.get_property(propertyName)
        if isinstance(prop, RelationshipProperty):
            try:
                remoteClass = prop.mapper.class_manager.class_
                if isinstance(remoteClass, type):
                    obj.__setattr__(propertyName, remoteClass())
                    return obj.__getattribute__(propertyName)
            except AttributeError:
                return False
        return False

    @staticmethod
    def getClassByEntityId(entityId):
        for cls in OrmBaseObject.__subclasses__():
            if cls.entityId == entityId:
                return cls