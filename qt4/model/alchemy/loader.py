'''
Created on 17.02.2011

@author: michi
'''
from PyQt4.QtCore import QObject,pyqtSignal

from sqlalchemy import create_engine
from ems.model.alchemy.loader import AlchemyLoader

class ConListener(object):
    def __init__(self, emitter):
        self.__emitter = emitter
        
    def connect(self, dbapi_con, con_record):
        self.__emitter.connected.emit(True)

class ConEmitter(QObject):
    
    connected = pyqtSignal(bool)
    
    def __init__(self, parent = None):
        super(ConEmitter, self).__init__(parent)
        self.listener = ConListener(self)
        

class QAlchemyLoader(AlchemyLoader,QObject):
    
    loaded = pyqtSignal(str)
    
    removed = pyqtSignal(str)

    def __init__(self,parent=None):
        AlchemyLoader.__init__(self)
        QObject.__init__(self,parent)
        self.__emitters = {}
    
    def loadEngine(self,handle='default',loaderHint=''):
        engine = AlchemyLoader.loadEngine(self, handle, loaderHint)
        self.loaded.emit(handle)
        return engine
    
    def getEmitter(self, handle="default"):
        if not self.__emitters.has_key(handle):
            self.__emitters[handle] = ConEmitter()
        return self.__emitters[handle]
    
    def remove(self,handle):
        AlchemyLoader.remove(self, handle)
        self.__emitters[handle].connected.emit(False)
        self.removed.emit(handle)
        del self.__emitters[handle]
    
    def _createEngine(self, url, handle):
        return create_engine(url,
                             echo=self.logQueries,
                             listeners=[self.getEmitter(handle).listener])
    
    def disposeEngine(self, handle):
        AlchemyLoader.disposeEngine(self, handle)
        self.__emitters[handle].connected.emit(False)
    