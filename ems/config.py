'''
Created on 09.02.2011

@author: michi
'''

import six

from ems.configuration.node import Node
from collections import OrderedDict
from ems.configuration.loader.xml import Xml
from ems.eventhook import EventHook

class NoDefaultProfileError(ReferenceError):
    pass

class CfgFileNameNotSettedError(SyntaxError):
    pass


class Config(object):
    '''
    classdocs
    '''
    def __init__(self, fileName=None, loader=None):
        '''
        Constructor
        '''
        self.__loader = None
        self.__defaultProfile = None
        self.__calculatedDefaultProfile = None
        self.__noProfile = '_noname_' 
        self.__profiles = OrderedDict()
        self.__fileName = fileName
        self.__profileNames = {}
        self.__configLoaded = False
        self.__autoload = True
        self.appPath = None

        self.loader = loader if loader else Xml()

        self.standardProfileChanged = EventHook()
        self.profileChanged = EventHook()
        self.profileDeleted = EventHook()
        self.profileNameChanged = EventHook()
        self.entryChanged = EventHook()
        self.entryDeleted = EventHook()
        self.configLoaded = EventHook()
        self.configSaved = EventHook()

    def isConfigLoaded(self):
        return self.__configLoaded


    def getAutoload(self):
        return self.__autoload

    def setAutoload(self, value):
        self.__autoload = value

    def getFileName(self):
        return self.__fileName

    def setFileName(self, value):
        self.__fileName = value

    def delFileName(self):
        del self.__fileName


    def getDefaultProfile(self):
        if self.__defaultProfile is None:
            if self.__calculatedDefaultProfile is None:
                if len(self.__profiles) < 2:
                    try:
                        self.__calculatedDefaultProfile = list(self.__profiles.keys())[0]
                    except IndexError:
                        self.__profiles[self.__noProfile] = Node()
                        self.__calculatedDefaultProfile = self.__noProfile
                else:
                    raise NoDefaultProfileError("%s %s %s" %
                                                ("More than on profile, you",
                                                "have to assign one via",
                                                "setDefaultProfile"))
                        
            return self.__calculatedDefaultProfile
        return self.__defaultProfile
    
    def clear(self):
        self.__profiles = OrderedDict()

    def getProfiles(self):
        self.__autoloadIfNeeded()
        return self.__profiles

    def setDefaultProfile(self, value):
        self.__defaultProfile = value
        self.standardProfileChanged.fire(value)

    def getDefaultProfileId(self):
        return self.__defaultProfile

    def setProfileName(self,profileId,name):
        self.__profileNames[profileId] = name
        self.profileNameChanged.fire(profileId, name)

    def __iter__(self):
        return self.__profiles[self.defaultProfile].__iter__()

    def getProfileName(self,profileId):
        if not len(profileId):
            profileId = self.getDefaultProfile()
        return self.__profileNames[profileId]


    def get(self, key):
        return self.__getitem__(key)

    def __getitem__(self,key):

        self.__autoloadIfNeeded()
        profileId, key = self.__getProfileAndVarName(key)

        return self.__profiles[profileId][key]

    def has_key(self, key):

        self.__autoloadIfNeeded()
        profileId, key = self.__getProfileAndVarName(key)

        return key in self.__profiles[profileId]

    def __setitem__(self,key,val):

        profileId, key = self.__getProfileAndVarName(key)
        if profileId not in self.__profiles:
            self.__profiles[profileId] = {}
        self.__profiles[profileId][key] = val
        self.entryChanged.fire(profileId, key, val)

    def __delitem__(self,key):

        profileId, key = self.__getProfileAndVarName(key)
        del self.__profiles[profileId][key]
        self.entryDeleted.fire(profileId, key)

    def __getProfileAndVarName(self,key):
        if isinstance(key, six.string_types):
            if ":" in key:
                return(key[0:key.find(":")],key[key.find(":")+1:])
        return (self.defaultProfile, key)

    def getProfile(self,name=''):

        self.__autoloadIfNeeded()

        if not len(name):
            name = self.getDefaultProfile()
        return self.__profiles[name]

    def setProfile(self, name, profile):
        if not isinstance(profile, Node):
            raise TypeError("Profile has to be instance of configuration.node.Node")
        self.__calculatedDefaultProfile = None
        self.__profiles[name] = profile
        self.profileChanged.fire(name)

    def delProfile(self,name):
        del self.__profiles[name]
        self.profileDeleted.fire(name)

    def load(self,fileName=''):
        self.disableEvents(True)
        if len(fileName):
            self.fileName = fileName

        self.loader.load(self.fileName, self)
        self.enableEvents(True)
        self.__configLoaded = True
        self.configLoaded.fire(self.fileName)

    def disableEvents(self, disable=True):

        for event in ('standardProfileChanged', 'profileChanged',
                      'profileDeleted', 'profileNameChanged', 'entryChanged',
                      'entryDeleted', 'configLoaded', 'configSaved'):
            getattr(self, event).fireBlocked = disable

    def enableEvents(self, enable=True):
        return self.disableEvents(not enable)

    def __autoloadIfNeeded(self):

        if not self.__autoload or self.__configLoaded:
            return

        # Only autoload if a value was never setted
        if self.entryChanged.wasFired or self.profileChanged.wasFired:
            return

        if self.__fileName is not None:
            self.load()

    def getLoader(self):
        if not self.fileName:
            raise CfgFileNameNotSettedError("Set Filename before getting a loader")
        return self.__loader

    def setLoader(self, loader):
        self.__loader = loader

    def save(self, fileName=''):
        if len(fileName):
            self.fileName = fileName

        self.loader.save(self.fileName, self)
        self.configSaved.fire(self.fileName)


    defaultProfile = property(getDefaultProfile, setDefaultProfile, None, "defaultProfile's docstring")
    profiles = property(getProfiles, None, None, "profiles's docstring")
    fileName = property(getFileName, setFileName, delFileName, "fileName's docstring")
    autoload = property(getAutoload, setAutoload, None, "autoload's docstring")
    loader = property(getLoader, setLoader)
