'''
Created on 24.10.2010

@author: michi
'''
import re

import xlrd

from ems.converter.inputreader import InputReader,DataCorruptException,\
    DataNotFoundException, XPathNotImplementedError
from ems.core.mimetype import MimeTypeDB
from ems.core.mimetype import MimeType

class Excel(InputReader):
    '''
    classdocs
    '''
    offset = 0

    def notify(self,eventType):
        if eventType == self.startProcess:
            self.currentIndex = 0
            self.currentRow = None
            self.readerClass = None

            if not hasattr(self,'fieldNames') or not self.fieldNames:
                self.fieldNames = self.getFieldNames()
            self.fieldIndexes = {}
            i = 0
            for name in self.fieldNames:
                self.fieldIndexes[name] = i
                i += 1
            
            
        super(Excel, self).notify(eventType)
    
    def getReaderClass(self):
        if self.readerClass is None:
            book = xlrd.open_workbook(self.source)
            self.readerClass = book.sheet_by_index(0)
            self.currentIndex = 0
            self.set_charset('iso-8859-15')
        return self.readerClass
    
    def __iter__(self):
        return self
    
    def next(self):
        readerClass = self.getReaderClass()
        try:
            if self._plugin is not None:
                self._plugin.notifyProgress()

            if self.currentIndex == 0:
                if self.offset > 0:
                    for i in range(self.offset):
                        self.currentIndex +=1
            self.currentIndex += 1
            self.currentRow = readerClass.row(self.currentIndex)

            if self.currentRow:
                return self.currentRow
            raise StopIteration
        except LookupError:
            raise StopIteration
    
    def select(self,xpath):
        if xpath == '//':
            return self
        else:
            if xpath in self.fieldNames:
                index = self.fieldIndexes[xpath]
                #if isinstance(self.currentRow[index].value, basestring):
                #    return unicode(self.currentRow[index].value,"iso-8859-15")
                return self.currentRow[index].value
            else:
                if re.match('^[a-zA-Z\-_]+$',xpath) is not None:
                    raise DataNotFoundException("%s not found in source"
                                                % xpath,xpath)
    
    def getType(self):
        return self.file
    
    def getCurrentPosition(self):
        return self.currentIndex
    
    def getSupportedMimeTypes(self):
        if not len(self.supportedMimeTypes):
            self.supportedMimeTypes = []
            try:
                self.supportedMimeTypes.append(MimeTypeDB.get(suffix='.xls'))
            except KeyError:
                self.supportedMimeTypes.append(MimeType('application/ms-excel',['.xls',]))
                
        return self.supportedMimeTypes
    
    def getFieldNames(self):
        if not hasattr(self,'fieldNames') or not self.fieldNames:
            cells = self.getReaderClass().row(0)
            fieldNames = []
            for cell in cells:
                fieldNames.append(cell.value) 
            return fieldNames
        return self.fieldNames
    
    def __len__(self):
        return self.getReaderClass().nrows - 1