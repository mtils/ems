'''
Created on 20.06.2011

@author: michi
'''
class OrmDecorator(object):
    def __init__(self, obj):
        self._object = obj
    
    def getReprasentiveString(self, view='default'):
        if hasattr(self._object,'__reprasentive_column__'):
            return self._object.__getattribute__(self._object.__reprasentive_column__)
        return repr(self._object)