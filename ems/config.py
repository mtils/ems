'''
Created on 09.02.2011

@author: michi
'''
from ems.configuration.node import Node
from collections import OrderedDict
from ems.pluginemitter import PluginEmitter
from ems.configuration.loader.xml import Xml

class NoDefaultProfileError(ReferenceError):
    pass

class CfgFileNameNotSettedError(SyntaxError):
    pass


class Config(object):
    '''
    classdocs
    '''
    def __init__(self,fileName=None):
        '''
        Constructor
        '''
        self.__defaultProfile = None
        self.__calculatedDefaultProfile = None
        self.__noProfile = '_noname_' 
        self.__profiles = OrderedDict()
        self.__pluginEmitter = None
        self.__fileName = fileName
        self.__profileNames = {}
        self._loadInProgress = False
        self.__configLoaded = False
        self.__autoload = False
        self.appPath = None

    def getConfigLoaded(self):
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


    def getPluginEmitter(self):
        return self.__pluginEmitter

    def setPluginEmitter(self, emitter):
        if not isinstance(emitter, PluginEmitter):
            raise TypeError("emitter has to be instance of PluginEmitter")
        self.__pluginEmitter = emitter

    def getDefaultProfile(self):
        if self.__defaultProfile is None:
            if self.__calculatedDefaultProfile is None:
                if len(self.__profiles) < 2:
                    try:
                        self.__calculatedDefaultProfile = self.__profiles.keys()[0]
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
        if self.__autoload:
            if not self.__configLoaded and self.__fileName is not None:
                self.load()
        return self.__profiles

    def setDefaultProfile(self, value):
        self.__defaultProfile = value
        if not self._loadInProgress:
            self.notifyPlugins('standardProfileChanged', (value,))
            
    def getDefaultProfileId(self):
        return self.__defaultProfile
    
    def setProfileName(self,profileId,name):
        self.__profileNames[profileId] = name
        if not self._loadInProgress:
            self.notifyPlugins('profileNameChanged', (profileId,name))
    
    def __iter__(self):
        return self.__profiles[self.defaultProfile].__iter__()
    
    def getProfileName(self,profileId):
        if not len(profileId):
            profileId = self.getDefaultProfile()
        return self.__profileNames[profileId]

    def __getitem__(self,key):
        if self.__autoload:
            if not self.__configLoaded and self.__fileName is not None:
                self.load()
        names = self.__getProfileAndVarName(key)
        return self.__profiles[names[0]][names[1]]
    
    def has_key(self, key):
        if self.__autoload:
            if not self.__configLoaded and self.__fileName is not None:
                self.load()
        names = self.__getProfileAndVarName(key)
        return self.__profiles[names[0]].has_key(key)
    
    def __setitem__(self,key,val):
        names = self.__getProfileAndVarName(key)
#        print self.__profiles
#        print names
        self.__profiles[names[0]][names[1]] = val
        if not self._loadInProgress:
            self.notifyPlugins('entryChanged', (names[0],names[1],val))
    
    def __delitem__(self,key):
        names = self.__getProfileAndVarName(key)
        del self.__profiles[names[0]][names[1]]
        if not self._loadInProgress:
            self.notifyPlugins('entryDeleted', (names[0],names[1]))
    
    def __getProfileAndVarName(self,key):
        if isinstance(key, basestring):
            if ":" in key:
                return(key[0:key.find(":")],key[key.find(":")+1:])
        return (self.defaultProfile,key)
    
    def getProfile(self,name=''):
        if self.__autoload:
            if not self.__configLoaded and self.__fileName is not None:
                self.load()
        if not len(name):
            name = self.getDefaultProfile()
        return self.__profiles[name]
    
    def setProfile(self,name,profile):
        if not isinstance(profile, Node):
            raise TypeError("Profile has to be instance of configuration.node.Node")
        self.__calculatedDefaultProfile = None
        self.__profiles[name] = profile
        if not self._loadInProgress:
            self.notifyPlugins('profileChanged', (name,))
    
    def delProfile(self,name):
        del self.__profiles[name]
        if not self._loadInProgress:
            self.notifyPlugins('profileDeleted', (name,))
    
    def notifyPlugins(self,eventName,params):
        if self.pluginEmitter is None:
            return
        self.pluginEmitter.notify(self,eventName,params)
    
    def load(self,fileName=''):
        self._loadInProgress = True
        if len(fileName):
            self.fileName = fileName
            
        self.getLoader().load(self.fileName)
        self._loadInProgress = False
        self.__configLoaded = True
        self.notifyPlugins('configLoaded',(self.fileName,))
    
    def getLoader(self):
        if not self.fileName:
            raise CfgFileNameNotSettedError("Set Filename before getting a loader")
        loader = Xml()
        loader.configObj = self
        return loader
    
    def save(self,fileName=''):
        if len(fileName):
            self.fileName = fileName
            
        self.getLoader().save(self.fileName)
        self.notifyPlugins('configSaved',(self.fileName,))
            
    

    defaultProfile = property(getDefaultProfile, setDefaultProfile, None, "defaultProfile's docstring")
    profiles = property(getProfiles, None, None, "profiles's docstring")
    pluginEmitter = property(getPluginEmitter, setPluginEmitter, None, "pluginEmitter's docstring")
    fileName = property(getFileName, setFileName, delFileName, "fileName's docstring")
    autoload = property(getAutoload, setAutoload, None, "autoload's docstring")
    configLoaded = property(getConfigLoaded, None, None, "configLoaded's docstring")
    