'''
Created on 10.02.2011

@author: michi
'''
from __future__ import absolute_import
import os
import xml.sax.handler
import xml.etree.ElementTree as ET
from ems.configuration.loader.base import *
from ems.configuration.node import Node 
#from ems.config import 

class Xml(Base):
    '''
    classdocs
    '''
    def _load(self,fileName):
        """
    A simple function to converts XML data into native Python object.
    """
        class TreeBuilder(xml.sax.handler.ContentHandler):
            def __init__(self,configObj):
                self.stack = []
                self.text_parts = []
                self.configObj = configObj
                self.currentProfile = ''
                self.currentVarname = ''
                
            def startElement(self, name, attrs):
                if name == 'profile':
                    profileInfo = {}
                    for k, v in attrs.items():
                        if k == 'id':
                            profileInfo['id'] = v
                        if k == 'name':
                            profileInfo['name'] = v
                        if k == 'standard' and v in ('True','true','1'):
                            profileInfo['standard'] = True
                    
                    if not profileInfo.has_key('id'):
                        raise CfgFileInvalidError("Profile missing Id")
                    if profileInfo.has_key('name'):
                        self.configObj.setProfileName(profileInfo['id'],
                                                      profileInfo['name'])
                    if profileInfo.has_key('standard'):
                        self.configObj.setDefaultProfile(profileInfo['id'])
                    self.configObj.setProfile(profileInfo['id'],Node())
                    self.currentProfile = profileInfo['id']
                                        
                if name == 'entry':
                    entryInfo = {} 
                    for k, v in attrs.items():
                        if k == 'name':
                            entryInfo['name'] = v
                    if not entryInfo.has_key('name'):
                        raise CfgFileInvalidError("Entry tag misses name attribute")
                    if self.currentProfile:
                        self.currentVarname = "%s:%s" % (self.currentProfile,entryInfo['name'])
                    else:
                        self.currentVarname = entryInfo['name']

                self.text_parts = []
                
            def endElement(self, name):
                if name == 'entry':
                    text = u''.join(self.text_parts).strip()
                    self.configObj[self.currentVarname] = text 
            def characters(self, content):
                self.text_parts.append(content)
        try:
            if not os.path.exists(fileName):
                raise CfgFileNotFoundError("Config File %s does not exist" % fileName)
            builder = TreeBuilder(self.configObj)
            xml.sax.parse(fileName, builder)
            return True
        except IOError,e:
            raise CfgFileNotFoundError(str(e))
        except ValueError,e:
            raise CfgFileNotFoundError(str(e))
        except xml.sax.SAXParseException,e:
            raise CfgFileInvalidError(str(e))
            
    
    def __addEntries(self,parentElement,profile):
        for key in profile:
            entry = ET.SubElement(parentElement, 'entry', {'name':key})
            entry.text = profile[key]
    
    def _save(self,fileName):
        root = ET.Element("pyconfig")
        if len(self.configObj.profiles) > 1:
            for profileId in self.configObj.profiles:
                profile = self.configObj.getProfile(profileId)
                attr = {'id':profileId}
                try:
                    name = self.configObj.getProfileName(profileId)
                except KeyError:
                    name = ''
                if name:
                    attr['name'] = name
                if profileId == self.configObj.getDefaultProfileId():
                    attr['standard'] = 'true'
                profilePart = ET.SubElement(root, 'profile', attr)
                self.__addEntries(profilePart, profile)
            tree = ET.ElementTree(root)
            tree.write(fileName, 'utf-8')
        pass