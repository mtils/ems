'''
Created on 10.02.2011

@author: michi
'''
from __future__ import absolute_import
import os
import xml.sax.handler
import xml.etree.ElementTree as ET
import json
import datetime
from ems.configuration.loader.base import *
from ems.configuration.node import Node 
#from ems.config import 

class Xml(Base):
    '''
    classdocs
    '''
    TYPE_STRING = 'string'
    TYPE_BOOL = 'bool'
    TYPE_INT = 'int'
    TYPE_FLOAT = 'float'
    TYPE_LIST = 'list'
    TYPE_DICT = 'dict'
    TYPE_NONE = 'null'
    TYPE_DATE = 'date'
    TYPE_DATETIME = 'datetime'
    
    def load(self, fileName, configObj):
        self.configObj = configObj
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
                self.currentVarType = Xml.TYPE_STRING

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

                    if not 'id' in profileInfo:
                        raise CfgFileInvalidError("Profile missing Id")
                    if profileInfo.has_key('name'):
                        self.configObj.setProfileName(profileInfo['id'],
                                                      profileInfo['name'])
                    if 'standard' in profileInfo:
                        self.configObj.setDefaultProfile(profileInfo['id'])
                    self.configObj.setProfile(profileInfo['id'],Node())
                    self.currentProfile = profileInfo['id']

                if name == 'entry':
                    entryInfo = {} 
                    self.currentVarType = Xml.TYPE_STRING
                    for k, v in attrs.items():
                        if k == 'name':
                            entryInfo['name'] = v
                        if k == 'type':
                            self.currentVarType = v
                                
                    if 'name' not in entryInfo:
                        raise CfgFileInvalidError("Entry tag misses name attribute")
                    if self.currentProfile:
                        self.currentVarname = "%s:%s" % (self.currentProfile,entryInfo['name'])
                    else:
                        self.currentVarname = entryInfo['name']

                self.text_parts = []
                
            def endElement(self, name):
                if name == 'entry':
                    text = u''.join(self.text_parts).strip()
                    if self.currentVarType == Xml.TYPE_STRING:
                        self.configObj[self.currentVarname] = text
                    else:
                        if self.currentVarType == Xml.TYPE_INT:
                            self.configObj[self.currentVarname] = int(text)
                            
                        elif self.currentVarType == Xml.TYPE_FLOAT:
                            self.configObj[self.currentVarname] = float(text)
                            
                        elif self.currentVarType == Xml.TYPE_BOOL:
                            if text.lower() in ('false','0','no'):
                                self.configObj[self.currentVarname] = False
                            elif text.lower() in ('true','1','yes'):
                                self.configObj[self.currentVarname] = True
                            else:
                                raise TypeError("Unable to parse bool from {0}".format(name))
                        
                        elif self.currentVarType == Xml.TYPE_DATE:
                            splitted = text.split('-')
                            if not len(splitted) == 3:
                                raise TypeError("Unable to parse date {0}".format(text))
                            
                            self.configObj[self.currentVarname] = datetime.date(int(splitted[0]),
                                                                                int(splitted[1]),
                                                                                int(splitted[2]))
                            
                        elif self.currentVarType == Xml.TYPE_NONE:
                            self.configObj[self.currentVarname] = None
                        
                        elif self.currentVarType in (Xml.TYPE_LIST, Xml.TYPE_DICT):
                            result = json.loads(text)
                            if self.currentVarType == Xml.TYPE_LIST:
                                if not isinstance(result, list):
                                    raise TypeError('Unable to parse json string {0} to list.'.format(text))
                            if self.currentVarType == Xml.TYPE_DICT:
                                if not isinstance(result, dict):
                                    raise TypeError('Unable to parse json string {0} to dict.'.format(text))
                            self.configObj[self.currentVarname] = result
                            
                        else:
                            raise TypeError("Unknown type {0}".format(self.currentVarType))
                            
                        
            def characters(self, content):
                self.text_parts.append(content)
        try:
            if not os.path.exists(fileName):
                raise CfgFileNotFoundError("Config File %s does not exist" % fileName)
            builder = TreeBuilder(self.configObj)
            xml.sax.parse(fileName, builder)
            return True
        except IOError as e:
            raise CfgFileNotFoundError(str(e))
        except ValueError as e:
            raise CfgFileInvalidError(str(e))
        except xml.sax.SAXParseException as e:
            raise CfgFileInvalidError(str(e))
            
    
    def __addEntries(self,parentElement,profile):
        for key in profile:
            entry = ET.SubElement(parentElement, 'entry', {'name':key})
            entry.text = profile[key]

    def save(self, fileName, configObj):

        self.configObj = configObj

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
        else:
            self.__addEntries(root, self.configObj)
            tree = ET.ElementTree(root)
            tree.write(fileName, 'utf-8')