'''
Created on 24.10.2010

@author: michi
'''
import re

from PyQt4.QtCore import QAbstractItemModel,Qt

from ems.converter.inputreader import InputReader,DataCorruptException,\
    DataNotFoundException, XPathNotImplementedError
from ems.core.mimetype import MimeType
from ems.qt4.util import variant_to_pyobject
from ems.model.sa.orm.base_object import OrmBaseObject

class QItemModel(InputReader):
    '''
    classdocs
    '''
    def select(self,xpath):
        if xpath == '//':
            self.__currentXpath = xpath
            return self
        elif xpath == '//row':
            self.__currentXpath = xpath
            return self
        elif xpath == 'fieldNames()':
            return self.getFieldNames()
        elif self.currentRow.has_key(xpath):
            return self.currentRow[xpath]
        else:
            raise XPathNotImplementedError(xpath)
    
    def getType(self):
        return self.interface
    
    def getCurrentPosition(self):
        return self.currentIndex
    
    def notify(self,eventType):
        if eventType == self.startProcess:
            self.currentIndex = -1
            self.currentRow = {}
            self.__columns = []
            self.__nextCount = 0
            self.__elementStack = []
            self.__nodeTest = {}
        super(QItemModel, self).notify(eventType)
    
    def __iter__(self):
        return self
    
    def next(self):
        self.__nextCount += 1
        try:
            if self._plugin is not None:
                self._plugin.notifyProgress()
            self.currentIndex += 1
            if self.currentIndex >= self.__len__():
                raise StopIteration()
            
            row = {}
            i=0
            
            for col in self.getFieldNames():
                index = self.source.index(self.currentIndex, i)
                val = variant_to_pyobject(self.source.data(index,Qt.DisplayRole))
                if isinstance(val, OrmBaseObject):
                    if hasattr(val.__class__, '__ormDecorator__'):
                        row[col] = val.__class__.__ormDecorator__().\
                            getReprasentiveString(val)
                    else:
                        row[col] = unicode(val)
                else:
                    row[col] = val
                
                i += 1
            self.currentRow = row
            if self.currentRow:
                return self.currentRow
            raise StopIteration
        except LookupError:
            raise StopIteration
    
    def getSupportedMimeTypes(self):
        if not len(self.supportedMimeTypes):
            self.supportedMimeTypes = [MimeType('model/qabstractitem')]
        return self.supportedMimeTypes
    
    def getFieldNames(self):
        if not len(self.__columns):
            for i in range(self.source.columnCount()):
                columnName = unicode(self.source.headerData(i,
                                                     Qt.Horizontal,
                                                     Qt.DisplayRole).toString())
                self.__columns.append(columnName)
        return self.__columns
    
    def __len__(self):
        return self.source.rowCount()