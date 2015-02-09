'''
Created on 25.10.2010

@author: michi
'''
from ems.converter.tag import Tag,AttributeException,ElementException

class Element(Tag):
    '''
    classdocs
    '''
    def interpret(self,xmlDict,inputReader,outputWriter):
        if not xmlDict['attributes'].has_key('name'):
            raise AttributeException("Tag 'element' needs a name attribute")
        name = xmlDict['attributes']['name']
        if name[0] =='{':
            name = self._select(name[1:-1], inputReader, outputWriter)
            
        attributes = {}
        nodeHasChildren = False
        if len(xmlDict['children']):
            nodeHasChildren = True
        
        #First iterate through attribute nodes (createElement is called first)
        if nodeHasChildren:
            for child in xmlDict['children']:
                if child['tag'] == 'attribute':
                    attributeName = self.extractAttributeName(child, inputReader, outputWriter)
                    attributes[attributeName] = \
                        self.interpretAttribute(child, inputReader, outputWriter)

        outputWriter.createElement(name,attributes)

        if nodeHasChildren:
            for child in xmlDict['children']:
                if child['tag'] != 'attribute':
                    value = self.converter.interpretTag(child,inputReader,outputWriter)
                    if child['tag'] != 'element':
                        outputWriter.setElementValue(value)
        else:
            outputWriter.setElementValue(xmlDict['cdata'])
        outputWriter.endElement()
    
    def extractAttributeName(self,xmlDict,inputReader,outputWriter):
        if xmlDict['attributes'].has_key('name'):
            name = xmlDict['attributes']['name']
            if name[0] =='{':
                name = self._select(name[1:-1], inputReader, outputWriter)
            if not name:
                raise SyntaxError("Only assign runtime attributenames which are sure")
            return unicode(name)
        else:
            raise SyntaxError("Tag attribute nees a name")
        pass
        
    def interpretAttribute(self,xmlDict,inputReader,outputWriter):
        select = ''
        try:
            select = xmlDict['attributes']['select']
            return self._select(select,inputReader,outputWriter)
        except LookupError:
            childCount = len(xmlDict['children'])
            if childCount:
                if childCount == 1:
                    return self.converter.interpretTag(xmlDict['children'][0],inputReader,outputWriter)
                else:
                    raise ElementException("Tag attribute can only have one children")
                pass
            else:
                return xmlDict['cdata']
        
    
    def __str__(self):
        return "element"