'''
Created on 24.10.2010

@author: michi
'''
import re

from dbfpy.dbf import *

from ems.converter.inputreader import InputReader,DataCorruptException,\
    DataNotFoundException, XPathNotImplementedError
from ems.core.mimetype import MimeTypeDB

from ems.core.mimetype import MimeType

class DBase(InputReader):
    '''
    classdocs
    '''
    def select(self,xpath):
        if xpath in ('//', '//row'):
            return self
        elif xpath == 'fieldNames()':
            return self.getFieldNames()
        else:
            if xpath in self.getReaderClass().fieldNames:
                if isinstance(self.currentRow[xpath], basestring):
                    return unicode(self.currentRow[xpath],"iso-8859-15")
                return self.currentRow[xpath]
            else:
                if re.match('^[a-zA-Z\-_]+$',xpath) is not None:
                    raise DataNotFoundException("%s not found in source"
                                                % xpath,xpath)
    
    def getReaderClass(self):
        if self.readerClass == None:
            self.readerClass = Dbf(self.source,readOnly=True)
            self.currentIndex = -1
            self.set_charset('iso-8859-15')
        return self.readerClass
    
    def getType(self):
        return self.file
    
    def getCurrentPosition(self):
        return self.currentIndex
    
    def notify(self,eventType):
        if eventType == self.startProcess:
            self.currentIndex = -1
            self.currentRow = None
            self.readerClass = None
        super(DBase, self).notify(eventType)
    
    def __iter__(self):
        return self
    
    def next(self):
        readerClass = self.getReaderClass()
        try:
            if self._plugin is not None:
                self._plugin.notifyProgress()
            self.currentIndex += 1
            self.currentRow = readerClass[self.currentIndex]
            if self.currentRow:
                return self.currentRow
            raise StopIteration
        except LookupError:
            raise StopIteration
    
    def getSupportedMimeTypes(self):
        if not len(self.supportedMimeTypes):
            self.supportedMimeTypes = []
            try:
                self.supportedMimeTypes.append(MimeTypeDB.get(suffix='.dbf'))
            except KeyError:
                self.supportedMimeTypes.append(MimeType('application/x-dbase',['.dbf',]))
        return self.supportedMimeTypes
    
    def getFieldNames(self):
        return self.getReaderClass().fieldNames
    
    def __len__(self):
        return self.getReaderClass().recordCount