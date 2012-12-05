'''
Created on 25.10.2010

@author: michi
'''
from ems.converter.tag import Tag,AttributeException

class ForEach(Tag):
    '''
    classdocs
    '''
    def interpret(self,xmlDict,inputReader,outputWriter):
        if xmlDict['attributes'].has_key('select'):
            select = xmlDict['attributes']['select']
            result = self._select(select, inputReader, outputWriter)
            assignDataTo = False
            if xmlDict['attributes'].has_key('as'):
                assignDataTo = xmlDict['attributes']['as']
                if assignDataTo and assignDataTo.find(':'):
                    assignDataTo = assignDataTo.split(':')
            if hasattr(result, '__iter__'):
                for data in result:
                    if assignDataTo:
                        if isinstance(assignDataTo, basestring):
                            self.converter.setVar(assignDataTo,data)
                        else:
                            self.converter.setVar(assignDataTo[0],data)
                            self.converter.setVar(assignDataTo[1],result[data])
                    for child in xmlDict['children']:
                        self.converter.interpretTag(child,inputReader,outputWriter)

        else:
            raise AttributeException("The tag for-each needs a select attribute")
    
    def __str__(self):
        return "for-each"