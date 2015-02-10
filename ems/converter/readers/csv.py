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
from ems.core.mimetype import MimeType

class CSVReader(InputReader):
    '''
    classdocs
    '''
    defaultDelimiter = '\t'
    delimiter = ","
    escapeChar = ''
    quoting = csv_o.QUOTE_ALL
    quoteChar = None
    fieldNames = None
    offset = 0
    readerClass = None

    remapping = {}

    def guessFormat(self, testChars=1024):
        dialect = None
        with open(self.source,"r") as csvfile:
            dialect = csv_o.Sniffer().sniff(csvfile.read(testChars))
            csvfile.seek(0)
            csvfile.close()
        if dialect:
            return dialect

    def hasHeader(self, testChars=1024):
        with open(self.source,"r") as csvfile:
            return csv_o.Sniffer().has_header(csvfile.read(testChars))

    def select(self,xpath):
        if xpath == '//':
            return self
        else:
            if self.remapping.has_key(xpath):
                xpath = self.remapping[xpath]
            if xpath in self.getReaderClass().fieldnames:
#                print "xpath: %s" % xpath
                if isinstance(self.currentRow[xpath], basestring):
                    #print xpath, self.currentRow[xpath]
                    return unicode(self.currentRow[xpath],self.get_charset())
                if self.currentRow[xpath] is None:
                    raise DataNotFoundException("%s not found in source"
                                                % xpath,xpath)
                return self.currentRow[xpath]
            else:
                if re.match('^[a-zA-Z\-_]+$',xpath) is not None:
                    raise DataNotFoundException("%s not found in source"
                                                % xpath,xpath)
    
    def getReaderClass(self):
        if self.readerClass == None:
            fp = open(self.source,"r")
            if self.quoteChar is not None:
                self.readerClass = csv_o.DictReader(fp,
                                                    delimiter=self.delimiter,
                                                    quoting=self.quoting,
                                                    quotechar=self.quoteChar,
                                                    fieldnames=self.fieldNames)
            else:
                self.readerClass = csv_o.DictReader(fp,
                                                    delimiter=self.delimiter,
                                                    quoting=csv_o.QUOTE_NONE,
                                                    fieldnames=self.fieldNames)

            self.currentIndex = -1
        return self.readerClass

    def getType(self):
        return self.file
    
    def getCurrentPosition(self):
        return self.currentIndex
    
    def notify(self,eventType):
        if eventType == self.init:
            self.set_charset('iso-8859-15')
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
            if self.currentIndex == 0:
                if self.offset > 0:
                    for i in range(self.offset):
                        readerClass.next()
            self.currentRow = readerClass.next()
            if self.currentRow:
                return self.currentRow
            raise StopIteration
        except LookupError:
            raise StopIteration
    
    def getSupportedMimeTypes(self):
        if not len(self.supportedMimeTypes):
            self.supportedMimeTypes = []
            try:
                self.supportedMimeTypes.append(MimeTypeDB.get(suffix='.csv'))
            except Exception:
                self.supportedMimeTypes.append(MimeType('text/csv',['.csv',]))
        return self.supportedMimeTypes
    
    def getFieldNames(self):
        #print self.getReaderClass().fieldnames
        if self.fieldNames is None:
            return self.getReaderClass().fieldnames
        return self.fieldNames
    
    def __len__(self):
        fp = open(self.source,"r")
        lines = len(fp.readlines())
        return lines