'''
Created on 25.10.2010

@author: michi
'''
from __future__ import absolute_import
import csv as csv_o
import codecs,cStringIO
from random import randint

from xlwt import Workbook, Font, XFStyle #@UnresolvedImport

from ems.converter import Converter
from ems.core.mimetype import MimeTypeDB
from ems.converter.outputwriter import OutputWriter

class Excel(OutputWriter):
    '''
    classdocs
    '''
    
    def notify(self,eventType):
        if eventType == self.init:
            self.verbosity = 0
        if eventType == self.startProcess:
            
            self.__writerOptions = {}
            self.__writeHeader = True
            
            if not self.options.has_key('encoding'):
                self.options['encoding'] = 'utf-8'
            
            self.__rowFormatStrings = []
            self.__rowFormats = []
            self.__formatNumbers = False
            
            if self.options.has_key('rowFormats'):
                self.__rowFormatStrings = self.options['rowFormats']
            
                if self.options.has_key('formatNumbers'):
                    if self.options['formatNumbers']:
                        self.__formatNumbers = True
                        for fmtString in self.__rowFormatStrings:
                            style = XFStyle()
                            style.num_format_str = fmtString
                            self.__rowFormats.append(style)
            
                
            if not self.options.has_key('writeHeader'):
                self.options['writeHeader'] = self.__writeHeader
            else:
                self.__writeHeader = self.options['writeHeader']
            
            self.__writer = Workbook()
            self.__workbook = self.__writer.add_sheet('Ergebnis')
            self.__workbook.country_code = 49
            self.__headerWritten = False
            self.__headerCols = []
            self.verbosity = 0
            self.currentDepth = 0
            self.__currentRow = -1
            self.__currentCol = -1
            self.__stylesWritten = False
            
            if self.__writeHeader:
                self.__currentRow = 0


        if eventType == self.endProcess:
            self._getWriter().save(self.target)
        super(Excel, self).notify(eventType)
    
    def dryRun(self,isDryRun=True):
        pass

    def createElement(self, name, params={}, namespace=None):
        self.currentDepth += 1
        
        if self.currentDepth == 1:
            self.__currentCol = -1
            self.__currentRow += 1
            
        if self.currentDepth == 2:
            self.__currentCol += 1
            if self.__writeHeader is True and not self.__headerWritten:
                self.__headerCols.append(name)
        
    def setElementValue(self,value):
        if self.currentDepth == 2:
            if value is None:
                value = ""
            if isinstance(value, (tuple, list)):
                if len(value):
                    value = u",".join(value)
                else:
                    value = ''
            if self.__formatNumbers:
                try:
                    style = self.__rowFormats[self.__currentCol]
                    self.__workbook.write(self.__currentRow, self.__currentCol,
                                          value, style)
                except IndexError:
                    self.__workbook.write(self.__currentRow, self.__currentCol, value)
            else:
                self.__workbook.write(self.__currentRow, self.__currentCol, value)
    
    def endElement(self):
        self.currentDepth -= 1
        if self.currentDepth == 0:
            if self.__writeHeader and not self.__headerWritten:
                fnt = Font()
                fnt.bold = True
                style = XFStyle()
                style.font = fnt
                i = 0
                for col in self.__headerCols:
                    self.__workbook.write(0, i, col, style)
                    i += 1
                self.__headerWritten = True
            
    
    def getCurrentPosition(self):
        return 0
    
    def getSupportedMimeTypes(self):
        return [MimeTypeDB.get(suffix='.xls')]
    
    def getType(self):
        return self.file
    
    def select(self,xpath):
        return randint(0,1000)
    
    def _getWriter(self):
        if self.__writer is None:
            self.__writer = Workbook()
        return self.__writer
    
    
