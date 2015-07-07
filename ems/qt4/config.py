'''
Created on 09.02.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSignal,SIGNAL,QObject


from ems.config import Config

class QConfig(QObject):

    standardProfileChanged = pyqtSignal(str)

    profileChanged = pyqtSignal(str)

    profileDeleted = pyqtSignal(str)

    profileNameChanged = pyqtSignal(str, str)

    entryChanged = pyqtSignal(str, str, object)

    entryDeleted = pyqtSignal(str, str)

    configLoaded = pyqtSignal(str)

    configSaved = pyqtSignal(str)

    def __init__(self, fileName='', parent=None, loader=None, config=None):

        self.__config = config if config else Config(fileName, loader=loader)
        QObject.__init__(self, parent)
        self.__connectToHooks()

    def getDefaultProfile(self):
        return self.__config.getDefaultProfile()

    def setDefaultProfile(self, value):
        return self.__config.setDefaultProfile(value)

    def getProfiles(self):
        return self.__config.getProfiles()

    def getFileName(self):
        return self.__config.getFileName()

    def setFileName(self, value):
        return self.__config.setFileName(value)

    def delFileName(self):
        return self.__config.delFileName()

    def getAutoload(self):
        return self.__config.getAutoload()

    def setAutoload(self, value):
        return self.__config.setAutoload(value)

    def __getattr__(self, name):
        return getattr(self.__config, name)

    def __getitem__(self, key):
        return self.__config.__getitem__(key)

    def has_key(self, key):
        return self.__config.has_key(key)

    def __setitem__(self, key, val):
        return self.__config.__setitem__(key, val)

    def __delitem__(self,key):
        return self.__config.__delitem__(key)

    def __connectToHooks(self):

        self.__config.standardProfileChanged += self.standardProfileChanged.emit
        self.__config.profileChanged += self.profileChanged.emit
        self.__config.profileDeleted += self.profileDeleted.emit
        self.__config.profileNameChanged += self.profileNameChanged.emit
        self.__config.entryChanged += self.entryChanged.emit
        self.__config.entryDeleted += self.entryDeleted.emit
        self.__config.configLoaded += self.configLoaded.emit
        self.__config.configSaved += self.configSaved.emit

    @property
    def baseConfig(self):
        return self.__config

    defaultProfile = property(getDefaultProfile, setDefaultProfile, None, "defaultProfile's docstring")
    profiles = property(getProfiles, None, None, "profiles's docstring")
    fileName = property(getFileName, setFileName, delFileName, "fileName's docstring")
    autoload = property(getAutoload, setAutoload, None, "autoload's docstring")