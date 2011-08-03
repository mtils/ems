'''
Created on 24.10.2010

@author: michi
'''

from ems.converter.inputreader import InputReader
from ems.core.mimetype import MimeTypeDB
from lib.ems.core.mimetype import MimeType

#from dbfpy.dbf import *

class Excel(InputReader):
    '''
    classdocs
    '''
    def select(self,xpath):
        pass
    
    def getType(self):
        return self.file
    
    def getCurrentPosition(self):
        return 0
    
    def getSupportedMimeTypes(self):
        if not len(self.supportedMimeTypes):
            self.supportedMimeTypes = []
            try:
                self.supportedMimeTypes.append(MimeTypeDB.get(suffix='.xls'))
            except KeyError:
                self.supportedMimeTypes.append(MimeType('application/ms-excel',['.xls',]))
                
        return self.supportedMimeTypes
    
    def getFieldNames(self):
        return []
    
    def __len__(self):
        raise NotImplementedError()