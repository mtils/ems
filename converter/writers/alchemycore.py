'''
Created on 25.10.2010

@author: michi
'''
from sqlalchemy import MetaData

from ems.converter import Converter
from ems.converter.outputwriter import OutputWriter

class MetaDataNotSetException(AttributeError):
    pass
class SchemaItemNotFoundException(AttributeError):
    pass

class AlchemyCore(OutputWriter):
    '''
    classdocs
    '''
    commaMask = "<#|.|#>"
    rowIdSeparator = '|=|'
    
    def notify(self,eventType):
        if eventType == self.startProcess:
            self.__currentDepth = 0
            self.__currentTableDict = None
            self.__currentTableName = ""
            self.__currentColumnName = None
            self.__currentParams = {}
            self.__currentTableCacheId = ''
            self.__lastTableName = ''
            self.__tableIdCache = {}
            self.__lastTableIds = {}
            self.__truncatedTables = {}
            self._con = None
            self.__rowsHaveMultipleColumns = False
            self.__insertQueue = []
            self._transaction = None
            self.begin()

        if eventType == self.endProcess:
            if self.__rowsHaveMultipleColumns:
                self._doMultiColumnFlush(self.__lastTableName)
            self.commit()
        super(AlchemyCore, self).notify(eventType)
        pass
    
    def dryRun(self,isDryRun=True):
        pass
    
    def setConnection(self, connection):
        self._con = connection
    
    def getConnection(self):
        if self._con is None:
            self._con = self.target.connect()
        return self._con
    
    def begin(self):
        if self._transaction is None:
            self._transaction = self.getConnection().begin()
        return self._transaction
    
    def commit(self):
        if self._transaction is not None:
            self._transaction.commit()
            self._transaction = None
        else:
            raise SyntaxError("First start an transaction with begin")
    
    def rollback(self):
        if self._transaction is not None:
            self._transaction.rollback()
            self._transaction = None
        else:
            raise SyntaxError("First start an transaction with begin")
    
    def getMetaData(self):
        try:
            if not isinstance(self.__metaData, MetaData):
                self.__metaData = MetaData()
        except AttributeError:
            self.__metaData = MetaData()
        return self.__metaData
    
    def setMetaData(self,metadata):
        if not isinstance(metadata, MetaData):
            raise TypeError('MetaData has to be instance of MetaData')
        self.__metaData = metadata
    
    def delMetaData(self):
        del self.__metaData
    
    metaData = property(getMetaData,setMetaData,delMetaData,'Set MetaData')
    
    def _doMultiColumnFlush(self, tableName):
        try:
            table = self.metaData.tables[tableName]
        except KeyError,e:
            raise SchemaItemNotFoundException(str(e))
        ins = table.insert()
        self.getConnection().execute(ins,self.__insertQueue)
    
    
    def _doMultiColumnInsert(self, tableName, params={},namespace=None):
        
        if tableName != self.__lastTableName:
            if self.__lastTableName:
                self._doMultiColumnFlush(self.__lastTableName)
                self.__insertQueue = []
            self.__lastTableName = tableName
            
        if params.has_key('columns'):
            columns = params['columns'].split(',')
        else:
            try:
                columns = self.metaData.tables[tableName].c
            except KeyError,e:
                raise SchemaItemNotFoundException(str(e))
            
        values = params['values'].replace("\,",self.commaMask) 
        
        values = values.split(',')
        valueDict = {}
        i=0
        for col in columns:
            valueDict[str(col)] = values[i].replace(self.commaMask,',')
            i+=1
        self.__insertQueue.append(valueDict)
        
        
    def createElement(self,name,params={},namespace=None):
        self.__currentDepth += 1
#        print "createElement name:%s depth: %s" % (name,self.__currentDepth)
        
        #Multiple Columns Per Row Mode
        if params.has_key('values'):
            self.__rowsHaveMultipleColumns = True
            self._doMultiColumnInsert(name, params, namespace)
        else:
            self.__rowsHaveMultipleColumns = False
            self.__currentParams = params
            if self.__currentDepth == 1:
                self.__currentTableDict = {}
                self.__currentTableName = name
                if not self.__tableIdCache.has_key(name):
                    self.__tableIdCache[name] = {}
            elif self.__currentDepth == 2:
                self.__currentColumnName = name
    
    def setElementValue(self,value):
#        print "setElementValue value:%s depth: %s" % (value,self.__currentDepth)
        if self.__rowsHaveMultipleColumns is True:
            return
        if self.__currentDepth == 2:
            if self.__currentParams.has_key('identifying'):
                self.__currentTableCacheId += self.rowIdSeparator + unicode(value)
            self.__currentTableDict[self.__currentColumnName] = value
            
    def endElement(self):
#        print "endElement depth: %s" % self.__currentDepth
        
        if self.__rowsHaveMultipleColumns is False:
            if self.__currentDepth == 1:
                #Table was already written
                if not self.__tableIdCache[self.__currentTableName].\
                    has_key(self.__currentTableCacheId):
                    
                    try:
                        table = self.metaData.tables[self.__currentTableName]
                    except KeyError,e:
                        raise SchemaItemNotFoundException(str(e))
                    
                    #From here actual write action
                    #if updateMode is replace, truncate the table first
                    if self.converter.writeMode == Converter.replace:
                        if not self.__truncatedTables.has_key(self.__currentTableName):
                            
                            
                            self.getConnection().execute(table.delete())
                            self.__truncatedTables[self.__currentTableName] = True

                    ins = table.insert().values(**self.__currentTableDict)
                    result = self.getConnection().execute(ins)
                    insertedId = result.inserted_primary_key
                    
                    if isinstance(insertedId, list):
                        self.__tableIdCache[self.__currentTableName]\
                            [self.__currentTableCacheId] = insertedId[0]
                    else:
                        self.__tableIdCache[self.__currentTableName]\
                            [self.__currentTableCacheId] = insertedId
                
                try:
                    self.__lastTableIds[self.__currentTableName] = \
                        self.__tableIdCache[self.__currentTableName][self.__currentTableCacheId]
                except LookupError:
                    pass
                self.__currentTableCacheId = ''
            
        self.__currentDepth -= 1
    
    def getLastInsertIdOfTableCacheId(self,tableName,tableCacheId):
        pass
    
    def getCurrentPosition(self):
        return 0
    
    def getSupportedMimeTypes(self):
        return []
    
    def getType(self):
        return self.db
    
    def select(self,xpath):
        tableName = xpath.split('/')[0]
        if self.__lastTableIds.has_key(tableName):
            return self.__lastTableIds[tableName]
        else:
            raise RuntimeError("Last Insert Id of table %s is unknown" % tableName)
