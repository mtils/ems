'''
Created on 24.10.2010

@author: michi
'''
from __future__ import absolute_import
import csv as csv_o
import re

from ems.converter.inputreader import InputReader,DataCorruptException,\
    DataNotFoundException, XPathNotImplementedError
from ems.core.mimetype import MimeTypeDB
from dbfpy.dbf import *

class CSVReader(InputReader):
    '''
    classdocs
    '''
    defaultDelimiter = '\t'
    
    def select(self,xpath):
        if xpath == '//':
            return self
        else:
            if xpath in self.getReaderClass().fieldnames:
                if isinstance(self.currentRow[xpath], basestring):
                    return unicode(self.currentRow[xpath],"iso-8859-15")
                return self.currentRow[xpath]
            else:
                if re.match('^[a-zA-Z\-_]+$',xpath) is not None:
                    raise DataNotFoundException("%s not found in source"
                                                % xpath,xpath)
    
    def getReaderClass(self):
        if self.readerClass == None:
            fp = open(self.source,"r")
            self.readerClass = csv_o.DictReader(fp,delimiter=self.defaultDelimiter,quoting=csv_o.QUOTE_NONE)
            #self.readerClass = Dbf(self.source,readOnly=True)
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
        super(CSVReader, self).notify(eventType)
    
    def __iter__(self):
        return self
    
    def next(self):
        #if row.has_key(tableData['columns'][columnName]['key']):
        #return
        readerClass = self.getReaderClass()
        try:
            if self._plugin is not None:
                self._plugin.notifyProgress()
            self.currentIndex += 1
            self.currentRow = readerClass.next()
            if self.currentRow:
                return self.currentRow
            raise StopIteration
        except LookupError:
            raise StopIteration
    
    def getSupportedMimeTypes(self):
        if not len(self.supportedMimeTypes):
            self.supportedMimeTypes = []
            self.supportedMimeTypes.append(MimeTypeDB.get(suffix='.csv'))
        return self.supportedMimeTypes
    
    def getFieldNames(self):
        #print self.getReaderClass().fieldnames
        return self.getReaderClass().fieldnames
    
    def __len__(self):
        fp = open(self.source,"r")
        lines = len(fp.readlines())
        return lines