'''
Created on 25.10.2010

@author: michi
'''
from ems.converter.tag import Tag,AttributeException,MappingException,\
    ElementException

class ModifierNotFoundException(MappingException):
    pass

class Modifier(Tag):
    '''
    classdocs
    '''
    def interpret(self,xmlDict,inputReader,outputWriter):
        if xmlDict['attributes'].has_key('name'):
            if self.converter.modifiers.has_key(xmlDict['attributes']['name']):
                modifier = self.converter.modifiers[xmlDict['attributes']['name']]
                params = {}
                paramsList = []
                paramWithNameFound = False
                paramWithoutNameFound = False
                
                if len(xmlDict['children']):
                    
                    for child in xmlDict['children']:
                        if child['tag'] == 'param':
                            
                            if child['attributes'].has_key('name'):
                                paramWithNameFound = True
                            else:
                                paramWithoutNameFound = True
                                
                            if paramWithNameFound and paramWithoutNameFound:
                                raise AttributeException(
                                    "You can't mix named with not named params")
                            
                            childCount = len(child['children']) 
                            if childCount:
                                if childCount == 1:
                                    if paramWithNameFound:
                                        params[child['attributes']['name']] = \
                                            self.converter.interpretTag(
                                                                        child['children'][0]
                                                                        ,inputReader
                                                                        ,outputWriter
                                                                        )
                                    else:
                                        paramsList.append(self.converter.interpretTag(
                                                                        child['children'][0]
                                                                        ,inputReader
                                                                        ,outputWriter
                                                                        ))
                                else:
                                    raise ElementException(
                                        "Tag param can only have one children")
                            else:
                                if paramWithNameFound:
                                    params[child['attributes']['name']] = child['cdata']
                                else:
                                    paramsList.append(child['cdata'])
                                    
                        else:
                            raise ElementException(
                                    "Tag modifier can only have param children")
                if paramWithNameFound:
                    return modifier.interpret(params)
                else:
                    return modifier.interpret(paramsList)
            else:
                raise ModifierNotFoundException(
                        "Modifier \"%s\"is not supported or loaded" %
                        xmlDict['attributes']['name']
                )
            
        else:
            raise AttributeException("Tag modifier misses name attribute")
    
    def __str__(self):
        return "modifier"