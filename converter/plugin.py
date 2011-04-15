'''
Created on 24.10.2010

@author: michi
'''

import ems.converter

class Plugin(object):
    '''
    classdocs
    '''
    init = 1
    startProcess = 2
    endProcess = 3
    shutdown = 4
    
    def getConverter(self):
        return self.__converter
    
    def setConverter(self,converter):
        if not isinstance(converter, ems.converter.Converter):
            raise TypeError('The First Param has to be instanceof ems.converter.Converter')
        self.__converter = converter
    
    def delConverter(self):
        self.__converter = None
    
    def notify(self,eventType):
        pass
    
    converter = property(getConverter,setConverter,delConverter,"converters Docstring")