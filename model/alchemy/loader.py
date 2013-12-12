'''
Created on 17.02.2011

@author: michi
'''
import os.path

from sqlalchemy import create_engine,MetaData
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker,scoped_session

from ems.exceptions import DuplicateIdentifierError

class DriverNotConfiguredError(KeyError):
    pass

class HandleAlreadyUsedError(DuplicateIdentifierError):
    pass

class NoConfigFound(KeyError):
    pass

class ConnectionNotFoundError(KeyError):
    pass

class AlchemyLoader(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.__engines = {}
        self.__engineConfigs = {}
        self.__metaDatas = {}
        self.__loader = None
        self.__configurators = {}
        self.__sessionMakers = {}
        self.logQueries = False
        self.appPath = None
        self.autoflush = False
        self.autocommit = False
        self.expireOnCommit = False

    def getEngines(self):
        return self.__engines

    def getEngineConfigs(self):
        return self.__engineConfigs


    def getLoader(self):
        return self.__loader

    def setLoader(self, value):
        self.__loader = value
    
    def addConfigurator(self,cfgFunction,handle='default'):
        if not callable(cfgFunction):
            raise TypeError('cfgFunction has to be callable')
        if not self.__configurators.has_key(handle):
            self.__configurators[handle] = []
        self.__configurators[handle].append(cfgFunction)
    
    def _applyConfigurators(self,handle,eventName):
        if self.__configurators.has_key(handle):
            for cfgFunc in self.__configurators[handle]:
                cfgFunc(self,
                        eventName,
                        self.getEngine(handle),
                        self.getMetaData(handle),
                        handle)
    
    def getEngine(self,handle='default',loaderHint=''):
        if not self.__engines.has_key(handle):
            self.loadEngine(handle,loaderHint)
        return self.__engines[handle]
    
    def loadEngine(self,handle='default',loaderHint=''):
        if self.__engines.has_key(handle):
            msg = "Engine with handle \"%s\" does already exist" % handle
            raise HandleAlreadyUsedError(msg)
        if isinstance(loaderHint, basestring):
            try:
                engineConfig = self.getCfgForHandle(handle)
            except NoConfigFound:
                engineConfig = self._loadConfig(loaderHint)
                self.setCfgForHandle(handle, engineConfig)
        else:
            engineConfig = loaderHint
            self.setCfgForHandle(handle, engineConfig)
        
        if not engineConfig.has_key('driver'):
            raise DriverNotConfiguredError("EngineConfig %s misses driver"
                                           % loaderHint)
#        print self.getCfgForHandle(handle)
        url = self.buildUrl(engineConfig)
        self.__engines[handle] = self._createEngine(url, handle)
        self._applyConfigurators(handle,'engineAboutToLoad')
        self._applyConfigurators(handle, "engineLoaded")
        return self.__engines[handle]
    
    def _createEngine(self, url, handle):
        return create_engine(url,echo=self.logQueries)
    
    def buildUrl(self, cfg):
        url = URL(cfg['driver'])
        if cfg.has_key('username'):
            url.username = cfg['username']
        if cfg.has_key('password'):
            url.password = cfg['password']
        if cfg.has_key('host'):
            url.host = cfg['host']
        if cfg.has_key('port'):
            url.port = cfg['port']
        if cfg.has_key('database'):
            url.database = cfg['database']
        if cfg.has_key('databasefile'):
            if os.path.isabs(cfg['databasefile']):
                url.database = cfg['databasefile']
            else:
                if self.appPath is not None:
                    url.database = os.path.join(self.appPath,
                                            cfg['databasefile'])
                else:
                    if self.__loader is None:
                        raise TypeError("Loader not set to retrieve appPath")
                    if self.__loader.appPath is None:
                        raise TypeError("appPath of loader not set")
                    url.database = os.path.join(self.__loader.appPath,
                                                cfg['databasefile'])
        if cfg.has_key('options'):
            url.query = cfg['options']
        return url
        
    def getCfgForHandle(self,handle):
        if self.__engineConfigs.has_key(handle):
            return self.__engineConfigs[handle]
        raise NoConfigFound("No Config for handle %s found" % handle)
    
    def _loadConfig(self,configName):
        if self.__loader is None:
            raise NoConfigFound("No Config for configName %s found" % configName)
        return self.__loader.getCfg(configName)
    
    def setCfgForHandle(self,handle,config):
        self.__engineConfigs[handle] = config
    
    def removeActiveEngines(self):
        handleDict = []
        for handle in self.__engines:
            handleDict.append(handle)
        for handle in handleDict:
            try:
                self.remove(handle)
            except Exception:
                pass
        pass
    
    def hasCon(self,handle):
        return self.__engines.has_key(handle) 
    
    def remove(self,handle):
        if self.__engineConfigs.has_key(handle):
            self.__engines[handle].dispose()
            del self.__engines[handle]
            del self.__engineConfigs[handle]
            del self.__metaDatas[handle]
        else:
            raise KeyError("No engine with Handle %s found" % handle)
    
    def disposeEngine(self, handle):
        if self.__engineConfigs.has_key(handle):
            self.__engines[handle].dispose()
    
    def getMetaData(self,handle='default'):
        if not self.__metaDatas.has_key(handle):
            self.__metaDatas[handle] = MetaData()
            self.__metaDatas[handle].bind = self.getEngine(handle)
        return self.__metaDatas[handle]
    
    def getSession(self, handle='default'):
        return scoped_session(self.getSessionMaker(handle))
    
    def getSessionMaker(self, handle='default'):
        if not self.__sessionMakers.has_key(handle):
            self.__sessionMakers[handle] = \
                sessionmaker(bind=self.getEngine(handle),
                             autoflush=self.autoflush,
                             autocommit=self.autocommit,
                             expire_on_commit=False)
            self._applyConfigurators(handle, "sessionMakerAboutToLoad")
            self._applyConfigurators(handle, "sessionMakerLoaded")
        return self.__sessionMakers[handle]
    
    def printEngines(self):
        print "AlchemyLoader.printEngines:"
        for handle in self.__engines:
            print "    %s:%s" % (handle,self.__engines[handle].name) 
    
    engines = property(getEngines, None, None, "connections's docstring")
    engineConfigs = property(getEngineConfigs, None, None, "connectionConfigs's docstring")
    loader = property(getLoader, setLoader, None, "loader's docstring")
