'''
Created on 09.02.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSignal,SIGNAL,QObject


from ems.config import Config

class QConfig(QObject,Config):
    
    standardProfileChanged = pyqtSignal(str)
    
    profileChanged = pyqtSignal(str)
    
    profileDeleted = pyqtSignal(str)
    
    profileNameChanged = pyqtSignal(str,str)
    
    entryChanged = pyqtSignal(str,str,str)
    
    entryDeleted = pyqtSignal(str,str)
    
    configLoaded = pyqtSignal(str)
    
    configSaved = pyqtSignal(str)
    
    
    def __init__(self,fileName='',parent=None):
        Config.__init__(self, fileName)
        QObject.__init__(self,parent)
    
    def notifyPlugins(self,eventName,params):
        if eventName == 'standardProfileChanged':
            self.standardProfileChanged.emit(params[0])
        elif eventName == 'profileChanged':
            self.profileChanged.emit(params[0])
        elif eventName == 'profileDeleted':
            self.profileDeleted.emit(params[0])
        elif eventName == 'profileNameChanged':
            self.profileNameChanged.emit(params[0],params[1])
        elif eventName == 'entryChanged':
            self.entryChanged.emit(params[0],params[1],str(params[2]))
        elif eventName == 'entryDeleted':
            self.entryDeleted.emit(params[0],params[1])
        elif eventName == 'configLoaded':
            self.configLoaded.emit(params[0])
        elif eventName == 'configSaved':
            self.configSaved.emit(params[0])
