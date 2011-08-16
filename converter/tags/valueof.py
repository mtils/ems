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
            #self.parsedXPaths.append(select)
            #variable
            if select.startswith('$'):
                return self.converter.getVar(select[1:])
            #constant
            elif select.startswith("'"):
                return select[1:-1]
            #ask writer
            elif select.startswith('writer:'):
                return outputWriter.select(select[7:])
            #nested xpath query
            elif select.startswith('{') and select.endswith('}'):
                tmpDict = {'attributes':{'select':select[1:-1]}}
                value = self.interpret(tmpDict, inputReader, outputWriter)
                newDict = {'attributes':{'select':value}}
                return self.interpret(newDict, inputReader, outputWriter)
            else:
                return inputReader.select(select)
        else:
            raise AttributeException(
                    "The tag value-of needs a select attribute")
    
    def __str__(self):
        return "value-of"
    
    def notify(self,eventType):
        if eventType == self.startProcess:
#            print "startProcess"
            self.parsedXPaths = []