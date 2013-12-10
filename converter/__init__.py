import os
import mimetypes

from ems.converter.inputreader import InputReader
from ems.converter.outputwriter import OutputWriter
from ems.converter.tag import Tag
from ems.converter.modifier import Modifier, ModifierException
from ems.converter.plugin import Plugin
from ems.converter.preprocessor import PreProcessor
from ems.xml.xml2dict import xml2obj

class Converter(object):
    
    reader = 1
    writer = 2
    tag = 3
    modifier = 4
    preprocessor = 5
    
    replace = 1
    update = 2
    sync = 3
    
    breakOnErrors = False
    
    def __init__(self):
        self.plugins = {}
        self.plugins[self.reader] = {}
        self.plugins[self.writer] = {}
        self.plugins[self.tag] = {}
        self.plugins[self.modifier] = {}
        self.plugins[self.preprocessor] = []
        self._variables = {}
        self._ignoredTopLevelTags = {}
        self.writeMode = Converter.replace
    
    def getReaderForFileName(self, filename):
        mimeTypeFound = False
        mimeType = mimetypes.guess_type(filename)
#        print mimeType
        if mimeType[0] is not None and mimeType[1] is not None:
            mimeTypeFound = True
        #print mimetypes.guess_extension(mimeType[0])
        
            
        
        
        if mimeTypeFound:
#            print "mimeType found"
            for reader in self.plugins[self.reader]:
                mimeTypes = self.plugins[self.reader][reader].getSupportedMimeTypes()
                for mType in mimeTypes:
                    #print "%s %s" % (mType, mType.suffixes)
                    if mimeType[0] == str(mType):  
                        return self.plugins[self.reader][reader]
        try:
            extension = ".%s" % unicode(filename).split('.')[-1:][0]
#            print "File: %s %s" % (filename, extension)
            for reader in self.plugins[self.reader]:
                mimeTypes = self.plugins[self.reader][reader].getSupportedMimeTypes()
                
                for mType in mimeTypes:
#                    print mType
                    if extension.lower() in mType.suffixes:
#                        print extension
#                        print self.plugins[self.reader][reader]
                        return self.plugins[self.reader][reader]
        except StopIteration, e:
            pass
        
        raise NotImplementedError("Keinen passenden Importer zu Datei %s gefunden" % filename) 
        

    def setVar(self,n,v):
        self._variables[n] = v
   
    def getVar(self,n):
        try:
            return self._variables[n]
        except LookupError:
            return None
    
    def getReaders(self):
        return self.plugins[self.reader]

    readers = property(getReaders, None, None, "readers's docstring")

    def getWriters(self):
        return self.plugins[self.writer]

    writers = property(getWriters, None, None, "writers's docstring")

    def getTags(self):
        return self.plugins[self.tag]
    
    tags = property(getTags,None,None,"Tags docstring")
    
    def getModifiers(self):
        return self.plugins[self.modifier]
    
    modifiers = property(getModifiers,None,None,"Modifiers docstring")
    
    
    def addPlugin(self,type,plugin):
        if not isinstance(plugin, Plugin):
            raise TypeError("The plugin has to be an Instance of ems.converter.plugin.Plugin")
        
        plugin.converter = self
        
        if type == self.reader:
            if isinstance(plugin, InputReader):
                self.plugins[self.reader][self._getPluginName(plugin)] = plugin
            else:
                raise TypeError("The reader has to be an Instance of InputReader")
            
        elif type == self.writer:
            if isinstance(plugin, OutputWriter):
                self.plugins[self.writer][self._getPluginName(plugin)] = plugin
            else:
                raise TypeError("The writer has to be an Instance of OutputWriter")
        
        elif type == self.tag:
            if isinstance(plugin, Tag):
                self.plugins[self.tag][self._getPluginName(plugin)] = plugin
            else:
                raise TypeError("The tag has to be an Instance of Tag")
            
        elif type == self.modifier:
            if isinstance(plugin, Modifier):
                self.plugins[self.modifier][self._getPluginName(plugin)] = plugin
            else:
                raise TypeError("The tag has to be an Instance of Tag")
            
        elif type == self.preprocessor:
            if isinstance(plugin, PreProcessor):
                self.plugins[self.preprocessor].append(plugin)
            else:
                raise TypeError("The preprocessor has to be an Instance of Preprocessor")
            
        else:
            raise TypeError("Unknown type \"%s\" of plugin" % type)
    
    def _getPluginName(self,plugin):
        if isinstance(plugin, Tag) or isinstance(plugin, Modifier):
            return "%s" % plugin
        return type(plugin).__name__
    
    def getMimeTypes(self,type):
        mimeTypes = []
        for reader in self.plugins[type]:
            for mimeType in self.plugins[type][reader].getSupportedMimeTypes():
                try:
                    mimeTypes.append(mimeType)
                except TypeError:
                    pass 
        return mimeTypes
    
    def getExtensions(self, type):
        mimeTypes = self.getMimeTypes(type)
        extensions = []
        for mimeType in mimeTypes:
            for ext in mimetypes.guess_all_extensions(str(mimeType)):
                try:
                    extensions.append(ext)
                except TypeError:
                    pass
        return extensions
    
    def setInputUri(self,uri):
        self.__inputUri = uri
    
    def ignoreToplevelTag(self,name,ignore=True):
        self._ignoredTopLevelTags[name] = ignore
    
    def _applyPreProcessors(self,xmlDict):
        for preprocessor in self.plugins[self.preprocessor]:
            preprocessor.interpret(xmlDict)
    
    def convert(self,reader,writer,mappingFile,writeMode=1):
        '''
        Starts conversion. You have to configure the reader and writer manually
        
        @param reader: ems.converter.reader.InputReader
        @type reader: ems.converter.reader.InputReader
        @param writer: ems.converter.writer.OutputWriter
        @type writer: ems.converter.writer.OutputWriter
        @param mappingFile: string The path to mapping xml File
        @type mappingFile: string 
        '''
        self.writeMode = writeMode
        if isinstance(reader, InputReader) and isinstance(writer, OutputWriter):
#            print self.plugins[self.tag]['value-of'].parsedXPaths
            if os.path.exists(mappingFile):
                xmlDict = self.getDictionaryOfMapping(open(mappingFile).read())
                for preprocessor in self.plugins[self.preprocessor]:
                    preprocessor.notify(Plugin.startProcess)
                  
                for tag in self.plugins[self.tag]:
                    self.plugins[self.tag][tag].notify(Plugin.startProcess)
                    
                for modifierName in self.plugins[self.modifier]:
                    self.plugins[self.modifier][modifierName].notify(Plugin.startProcess)
                    
                self._applyPreProcessors(xmlDict)
                reader.notify(Plugin.startProcess)
                writer.notify(Plugin.startProcess)
                self._parse(
                            reader, 
                            writer, 
                            xmlDict
                            )
                
                reader.notify(Plugin.endProcess)
                writer.notify(Plugin.endProcess)
                
            else:
                raise IOError("Mappingfile \"%s\" not found" % mappingFile)
        else:
            raise TypeError("First Param has to be InputReader, second OutputWriter")
        pass
    
    def _parse(self,reader,writer,mappingDict):
        if len(mappingDict['children']):
            if mappingDict['children'][0]['tag'] == 'mapping':
                if len(mappingDict['children'][0]['children']):
                    for child in mappingDict['children'][0]['children']:
                        if not self._ignoredTopLevelTags.has_key(child['tag']):
                            self.interpretTag(child, reader, writer)
                else:
                    raise SyntaxError("Mapping is empty")
            else:
                raise SyntaxError("Xml Data not well-formed or has no mapping root")
        else:
            raise SyntaxError("Xml Data is empty or not well-formed")
    
    def interpretTag(self,xmlDict,reader,writer):
        try:
            return self.plugins[self.tag][xmlDict['tag']].interpret(xmlDict,reader,writer)
        except LookupError,e:
            if not self.plugins[self.tag].has_key(xmlDict['tag']):
                raise SyntaxError("Tag \"%s\"is not supported or loaded" % xmlDict['tag'])
            if self.breakOnErrors:
                raise e
        except ModifierException,e:
            if self.breakOnErrors:
                raise e
        except ValueError, e:
            if self.breakOnErrors:
                raise e

    def getDictionaryOfMapping(self,mappingString):
        return xml2obj(mappingString)

    def getUsedPaths(self, mappingFile):
        mappingDict = self.getDictionaryOfMapping(open(mappingFile).read())
        results = []
        Converter._searchValueOfs(mappingDict, results)
        return results
    
    def getUsedFieldNames(self, mappingFile):
        valueOfs = self.getUsedPaths(mappingFile)
        result = []
        for valueOf in valueOfs:
            select = valueOf['attributes']['select']
            if self.plugins[self.tag]['value-of'].isFieldExpression(select):
                result.append(select)
        return result
    
    @staticmethod
    def _searchValueOfs(mappingDict, result):
        if mappingDict['tag'] == 'value-of':
            result.append(mappingDict)
        if mappingDict['children']:
            for child in mappingDict['children']:
                Converter._searchValueOfs(child, result)
