'''
Created on 20.06.2011

@author: michi
'''

from sqlalchemy.orm import object_mapper

class OrmDecorator(object):
    def __init__(self, cls):
        self._class = cls
        self._shownProperties = []
    
    def getReprasentiveString(self, obj, view='default'):
        if hasattr(self._class,'__reprasentive_column__'):
            return obj.__getattribute__(self._class.__reprasentive_column__)
        return repr(obj)
    
    def getFriendlyName(self, obj, view='default'):
        if hasattr(self._class, "__friendlyName__"):
            return self._class.__friendlyName__
        return self._class.__name__
    
    def getPropertyFriendlyName(self, propertyName):
        if hasattr(self._class, "__propertyFriendlyNames__"):
            notDottedProperty = str(propertyName).split('.')[-1:][0]
            if self._class.__propertyFriendlyNames__.has_key(notDottedProperty):
                return self._class.__propertyFriendlyNames__[notDottedProperty]
            else:
                print notDottedProperty
                print self._class.__propertyFriendlyNames__
        return propertyName
    
    def getShownProperties(self):
        if not len(self._shownProperties):
            if hasattr(self._class,'__shownProperties__'):
                self._shownProperties = self._class.__shownProperties__
            else:
                mapper = object_mapper(self._class())
                for prop in mapper.iterate_properties:
                    self._shownProperties.append(prop.key)
        
        return self._shownProperties