'''
Created on 25.10.2010

@author: michi
'''
from ems.converter.tag import Tag,AttributeException,ElementException,\
    MappingException

class Variable(Tag):
    
    '''
    classdocs
    '''
    def interpret(self,xmlDict,inputReader,outputWriter):
        if xmlDict['attributes'].has_key('name'):
            name = xmlDict['attributes']['name']
            if name[0] =='{':
                name = self._select(name[1:-1], inputReader, outputWriter)
            if not name:
                raise MappingException(
                        "Only assign runtime names as varname which are sure")
            select = ''
            if xmlDict['attributes'].has_key('select'):
                select = xmlDict['attributes']['select']
                self.converter.setVar(name,self._select(select,inputReader,outputWriter))
            else:
                childCount = len(xmlDict['children'])
                if childCount:
                    if childCount == 1:
                        self.converter.setVar(name,self.converter.interpretTag(xmlDict['children'][0],inputReader,outputWriter))
                    else:
                        raise ElementException(
                                    "Tag variable can only have one children")
                else:
                    self.converter.setVar(name,xmlDict['cdata'])
        else:
            raise AttributeException("Tag variable needs a name attribute")
    
    def __str__(self):
        return "variable"