'''
Created on 25.10.2010

@author: michi
'''
from __future__ import absolute_import, print_function
import csv as csv_o
import codecs,cStringIO
from random import randint

from ems.converter import Converter
from ems.core.mimetype import MimeTypeDB
from ems.converter.outputwriter import OutputWriter

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv_o.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv_o.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
            
class CSV(OutputWriter):
    '''
    classdocs
    '''
    
    def notify(self,eventType):
        
        if eventType == self.init:
            self.printEveryNLines = 0
        if eventType == self.startProcess:
            self.processedRows = 0
            self.__writerOptions = {}
            self.__writeHeader = True
            if not self.options.has_key('encoding'):
                self.options['encoding'] = 'utf-8'
            
            self.__writerOptions['encoding'] = self.options['encoding']
                
            if not self.options.has_key('dialect'):
                if not self.options.has_key('delimiter'):
                    self.options['delimiter'] = ','
                if not self.options.has_key('quotechar'):
                    self.options['quotechar'] = '\\'
                if not self.options.has_key('quoting'):
                    self.options['quoting'] = csv_o.QUOTE_MINIMAL
                for key in ('delimiter','quotechar','quoting'):
                    self.__writerOptions[key] = self.options[key]
            else:
                self.__writerOptions['dialect'] = self.options['dialect']
                
            if not self.options.has_key('writeHeader'):
                self.options['writeHeader'] = self.__writeHeader
            else:
                self.__writeHeader = self.options['writeHeader']
            
            self.__writer = None
            self.__headerWritten = False
            self.__headerCols = []
            self.currentDepth = 0
            self.__currentRow = []


        if eventType == self.endProcess:
            self._getWriter().stream.close()
        super(CSV, self).notify(eventType)
    
    def dryRun(self,isDryRun=True):
        pass

    def createElement(self,name,params={},namespace=None):
        self.currentDepth += 1
        
        if self.currentDepth == 1:
            self.__currentRow = []
        if self.__writeHeader is True:
            if self.currentDepth == 2 and not self.__headerWritten:
                self.__headerCols.append(name)
            
#            print "create Col %s" % name
    
    def setElementValue(self,value):
        if self.currentDepth == 2:
            if value is None:
                value = ""
            if isinstance(value, (tuple, list)):
                if len(value):
                    value = u",".join(value)
                else:
                    value = ''
            self.__currentRow.append(unicode(value))
    
    def endElement(self):
        self.currentDepth -= 1
        if self.currentDepth == 0:
            if self.__writeHeader and not self.__headerWritten:
                self._getWriter().writerow(self.__headerCols)
                self.__headerWritten = True
            self._getWriter().writerow(self.__currentRow)
            self.processedRows += 1
            if self.printEveryNLines:
                if (self.processedRows % self.printEveryNLines) == 0:
                    print('Processed {0} lines'.format(self.processedRows))
    
    def getCurrentPosition(self):
        return 0
    
    def getSupportedMimeTypes(self):
        return [MimeTypeDB.get(suffix='.csv')]
    
    def getType(self):
        return self.file
    
    def select(self,xpath):
        return randint(0,1000)
    
    def _getWriter(self):
        if self.__writer is None:
            self.__writer = UnicodeWriter(open(self.target,'wb')
                                          ,**self.__writerOptions)
        return self.__writer
