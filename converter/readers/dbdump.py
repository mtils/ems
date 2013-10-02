'''
Created on 24.10.2010

@author: michi
'''
from xml.etree import ElementTree as et

from ems.converter.inputreader import InputReader
from ems.core.mimetype import MimeTypeDB
from ems.core.mimetype import MimeType



class DBDump(InputReader):
    '''
    classdocs
    '''
    def select(self,xpath):
        pathMode = None 
        if xpath.startswith("//"):
            query = xpath[2:]
            pathMode = 'all'
        elif xpath.startswith("/"):
            query = xpath[1:]
            pathMode = 'abs'
        elif xpath.startswith('.'):
            query = xpath
            pathMode = 'rel'
        else:
            query = xpath
            pathMode = 'rel'
        
        # /: forward to root Node
        if query == '' and pathMode == 'abs':
            if self.__nextCount < 1:
                self.next()
            return self
        
        # //: iterate all elements
        if pathMode == 'all':
            if query != '':
                self.__nodeTest['query'] = "node-name(.)"
                self.__nodeTest['result'] = query
            return self
        
        if pathMode == 'rel':
            if query.endswith(')'):
                functionSplit = query.rstrip(')').split("(")
                func = functionSplit[0]
                par = functionSplit[1]
                elem = self.getNodeTestElement(par)
                if elem is not None:
                    if func == 'node-name':
                        return elem.tag
            else:
                nodePath = query[:query.rfind('/')]
                elem = self.getNodeTestElement(nodePath)
                if elem is not None:
                    nodeQuery = query[query.rfind('/')+1:]
                    if nodeQuery.startswith('@'):
                        try:
                            return elem.attrib[nodeQuery[1:]]
                        except KeyError:
                            return None
                        
    def getNodeTestElement(self,nodeTest):
        stackLength = len(self.__elementStack)
        if nodeTest == '.':
            if stackLength > 0:
                return self.__elementStack[stackLength-1]
            return None
        if nodeTest == '..':
            if stackLength > 1:
                return self.__elementStack[stackLength-2]
            return None
        
    def getType(self):
        return self.file
    
    def getCurrentPosition(self):
        return self.currentIndex
    
    def notify(self,eventType):
        if eventType == self.startProcess:
            self.currentIndex = -1
            self.__iterator = None
            self.__nextCount = 0
            self.__elementStack = []
            self.__nodeTest = {}
        super(DBDump, self).notify(eventType)
    
    def __iter__(self):
        return self
    
    def next(self):
        self.__nextCount += 1
        event,node = self.__getIterator().next()
        if event == 'start':

            self.__elementStack.append(node)

            if self.__nodeTest.has_key('query'):
                result = self.select(self.__nodeTest['query'])
                if result != self.__nodeTest['result']:
                    self.next()

        if event == 'end':
            self.__elementStack.pop()
            return self.next()
        
        self.currentIndex += 1
        if self._plugin is not None:
                self._plugin.notifyProgress()
                
        return self
    
    def __getIterator(self):
        if self.__iterator is None:
            self.__iterator = et.iterparse(open(self.source),events=("start","end"))
        return self.__iterator
    
    def getSupportedMimeTypes(self):
        if not len(self.supportedMimeTypes):
            self.supportedMimeTypes = []
            try:
                self.supportedMimeTypes.append(MimeTypeDB.get(suffix='.xml'))
            except KeyError:
                self.supportedMimeTypes.append(MimeType('text/xml',['.xml',]))
        return self.supportedMimeTypes
    
    def getFieldNames(self):
        return ["id","name"]
    
    def __len__(self):
        return 0