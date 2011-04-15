'''
Created on 25.10.2010

@author: michi
'''
from ems.converter import Converter
from ems.converter.outputwriter import OutputWriter
from ems.sql.table import Table

class Database(OutputWriter):
    '''
    classdocs
    '''
    
    def notify(self,eventType):
        if eventType == self.startProcess:
            self.currentDepth = 0
            self.currentTable = None
            self.currentTableName = ""
            self.currentColumnName = None
            self.currentParams = {}
            self.currentTableCacheId = ''
            self.tableIdCache = {}
            self.lastTableIds = {}
            self.fakeCounter = 0
            self.truncatedTables = {}

        if eventType == self.endProcess:
            #self.fileHandle.close()
            pass
        super(Database, self).notify(eventType)
        pass
    
    def dryRun(self,isDryRun=True):
        pass

    def createElement(self,name,params={},namespace=None):
        self.currentDepth += 1
        self.currentParams = params
        if self.currentDepth == 1:
            self.currentTable = Table(name)
            self.currentTableName = name
            if not self.tableIdCache.has_key(name):
                self.tableIdCache[name] = {}
        else:
            self.currentColumnName = name
    
    def setElementValue(self,value):
        if self.currentDepth == 2:
            if self.currentParams.has_key('identifying'):
                self.currentTableCacheId += unicode(value)
            if self.currentColumnName.find(",") == -1: 
                self.currentTable[self.currentColumnName] = value
            else:
                columns = self.currentColumnName.split(",")
                values = value.split(",")
                i=0
                cacheId = []
                for name in columns:
                    self.currentTable[name] = values[i]
                    cacheId.append(name)
                    cacheId.append(values[i])
                    i+=1
                self.currentTableCacheId = "-".join(cacheId)
                self.target.execute(self.currentTable.generateInsertStatement())
                self.tableIdCache[self.currentTableName][self.currentTableCacheId] = 1
    
    def endElement(self):
        if self.currentDepth == 1:
            #Table was already written
            if not self.tableIdCache[self.currentTableName].has_key(self.currentTableCacheId):
                #From here actual write action
                self.fakeCounter += 1
                
                #if updateMode is replace, truncate the table first
                if self.converter.writeMode == Converter.replace:
                    if not self.truncatedTables.has_key(self.currentTableName):
                        self.target.truncateTable(self.currentTableName)
                        self.truncatedTables[self.currentTableName] = True
                self.target.execute(self.currentTable.generateInsertStatement())
                self.tableIdCache[self.currentTableName][self.currentTableCacheId] = self.target.getLastInsertId()
                
            try:
                self.lastTableIds[self.currentTableName] = \
                    self.tableIdCache[self.currentTableName][self.currentTableCacheId]
            except LookupError:
                pass
            self.currentTableCacheId = ''
            
        self.currentDepth -= 1
    
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
        if self.lastTableIds.has_key(tableName):
            return self.lastTableIds[tableName]
        else:
            raise RuntimeError("Last Insert Id of table %s is unknown" % tableName)
