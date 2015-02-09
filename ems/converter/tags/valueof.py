'''
Created on 25.10.2010

@author: michi
'''
from ems.converter.tag import Tag,AttributeException

class ValueOf(Tag):
    '''
    classdocs
    '''
    parsedXPaths = []
    
    def interpret(self,xmlDict,inputReader,outputWriter):
        
        if xmlDict['attributes'].has_key('select'):
            select = xmlDict['attributes']['select']
            untypedValue = None
            #self.parsedXPaths.append(select)
            #variable
            if select.startswith('$'):
                untypedValue = self.converter.getVar(select[1:])
            #constant
            elif select.startswith("'"):
                untypedValue = select[1:-1]
            #ask writer
            elif select.startswith('writer:'):
                untypedValue = outputWriter.select(select[7:])
            #nested xpath query
            elif select.startswith('{') and select.endswith('}'):
                tmpDict = {'attributes':{'select':select[1:-1]}}
                value = self.interpret(tmpDict, inputReader, outputWriter)
                newDict = {'attributes':{'select':value}}
                untypedValue =  self.interpret(newDict, inputReader, outputWriter)
            else:
                untypedValue = inputReader.select(select)
            
            if not xmlDict['attributes'].has_key('type'):
                return untypedValue
            
            if xmlDict['attributes']['type'] == 'bool':
                try:
                    return bool(int(untypedValue)) # bool('0') == True
                except ValueError:
                    return False
            elif xmlDict['attributes']['type'] == 'int':
                try:
                    return int(untypedValue)
                except ValueError:
                    return 0
            elif xmlDict['attributes']['type'] in ('float','double'):
                try:
                    if isinstance(untypedValue, basestring):
                        untypedValue = untypedValue.replace(',','.')
                    return float(untypedValue)
                except ValueError:
                    return 0.0
            elif xmlDict['attributes']['type'] == 'string':
                return unicode(untypedValue)
            return untypedValue
            
        else:
            raise AttributeException(
                    "The tag value-of needs a select attribute")
    
    def isFieldExpression(self, path):
        if path.startswith('$'):
            return False
        if path.startswith("'"):
            return False
        if path.startswith("writer:"):
            return False
        if path.startswith("{"):
            return False
        return True
    
    def __str__(self):
        return "value-of"
    
    def notify(self,eventType):
        if eventType == self.startProcess:
#            print "startProcess"
            self.parsedXPaths = []