'''
Created on 17.02.2011

@author: michi
'''
from __future__ import print_function

import os.path

import six

from sqlalchemy import create_engine,MetaData
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker,scoped_session

from ems.event.hook import EventHook
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
        self.__initFired = False

        self.init = EventHook()
        self.engineAboutToLoad = EventHook()
        self.engineLoaded = EventHook()
        self.sessionMakerAboutToLoad = EventHook()
        self.sessionMakerLoaded = EventHook()
        self.metaDataCreator = lambda : MetaData()

    def getEngines(self):
        return self.__engines

    def getEngineConfigs(self):
        return self.__engineConfigs


    def getLoader(self):
        return self.__loader

    def setLoader(self, value):
        self.__loader = value

    def getEngine(self,handle='default',loaderHint=''):
        if handle not in self.__engines:
            self.loadEngine(handle, loaderHint)
        return self.__engines[handle]

    def loadEngine(self, handle='default', loaderHint=''):

        if handle in self.__engines:
            msg = "Engine with handle \"%s\" does already exist" % handle
            raise HandleAlreadyUsedError(msg)
        if isinstance(loaderHint, six.string_types):
            try:
                engineConfig = self.getCfgForHandle(handle)
            except NoConfigFound:
                engineConfig = self._loadConfig(loaderHint)
                self.setCfgForHandle(handle, engineConfig)
        else:
            engineConfig = loaderHint
            self.setCfgForHandle(handle, engineConfig)

        if 'driver' not in engineConfig:
            raise DriverNotConfiguredError("EngineConfig %s misses driver"
                                           % loaderHint)

        url = self.buildUrl(engineConfig)

        if not self.__initFired:
            self.init.fire(handle, engineConfig, url)
            self.__initFired = True

        self.__engines[handle] = engine = self._createEngine(url, handle)
        metadata = self.getMetaData(handle)

        self.engineAboutToLoad.fire(handle, engine, metadata)
        self.engineLoaded.fire(handle, engine, metadata)

        return self.__engines[handle]

    def _createEngine(self, url, handle):
        return create_engine(url,echo=self.logQueries)
    
    def buildUrl(self, cfg):
        url = URL(cfg['driver'])
        if 'username' in cfg:
            url.username = cfg['username']
        if 'password' in cfg:
            url.password = cfg['password']
        if 'host' in cfg:
            url.host = cfg['host']
        if 'port' in cfg:
            url.port = cfg['port']
        if 'database' in cfg:
            url.database = cfg['database']
        if 'databasefile' in cfg:
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
        if 'options' in cfg:
            url.query = cfg['options']
        return url
        
    def getCfgForHandle(self,handle):
        if handle in self.__engineConfigs:
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
        return handle in self.__engines 
    
    def remove(self,handle):
        if handle in self.__engineConfigs:
            self.__engines[handle].dispose()
            del self.__engines[handle]
            del self.__engineConfigs[handle]
            del self.__metaDatas[handle]
        else:
            raise KeyError("No engine with Handle %s found" % handle)

    def disposeEngine(self, handle):
        if handle in self.__engineConfigs:
            self.__engines[handle].dispose()

    def getMetaData(self, handle='default'):
        if handle not in self.__metaDatas:
            #self.__metaDatas[handle] = MetaData()
            self.__metaDatas[handle] = self.metaDataCreator()
            self.__metaDatas[handle].bind = self.getEngine(handle)
        return self.__metaDatas[handle]

    def getSession(self, handle='default'):
        return scoped_session(self.getSessionMaker(handle))

    def getSessionMaker(self, handle='default'):

        if handle in self.__sessionMakers:
            return self.__sessionMakers[handle]

        metadata = self.getMetaData(handle)

        maker = sessionmaker(bind=self.getEngine(handle),
                             autoflush=self.autoflush,
                             autocommit=self.autocommit,
                             expire_on_commit=False)

        self.__sessionMakers[handle] = maker

        self.sessionMakerAboutToLoad.fire(handle, metadata)
        self.sessionMakerLoaded.fire(handle, metadata)

        return self.__sessionMakers[handle]

    def printEngines(self):
        print("AlchemyLoader.printEngines:")
        for handle in self.__engines:
            print("    {0}:{1}".format(handle,self.__engines[handle].name))

    engines = property(getEngines, None, None, "connections's docstring")
    engineConfigs = property(getEngineConfigs, None, None, "connectionConfigs's docstring")
    loader = property(getLoader, setLoader, None, "loader's docstring")
