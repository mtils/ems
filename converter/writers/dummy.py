'''
Created on 25.10.2010

@author: michi
'''
from random import randint
from ems.converter import Converter
from ems.converter.outputwriter import OutputWriter


class Dummy(OutputWriter):
    '''
    classdocs
    '''
    
    def notify(self,eventType):
        if eventType == self.init:
            self.verbosity = 0
        if eventType == self.startProcess:
#            self.verbosity = 0
            self.currentDepth = 0
            self.createElementCount = 0
            if not hasattr(self, 'createElementLimit'):
                self.createElementLimit = 0

        if eventType == self.endProcess:
            pass
        super(Dummy, self).notify(eventType)
    
    def dryRun(self,isDryRun=True):
        pass

    def createElement(self,name,params={},namespace=None):
        self.currentDepth += 1
        self.createElementCount += 1
        if self.createElementLimit != 0:
            if self.createElementCount > self.createElementLimit:
                raise StopIteration("Process stopped after %s Iterations"
                                    % self.createElementLimit)
        if self.verbosity != 0:
            print "Depth: %s Name:%s" % (self.currentDepth,name)
    
    def setElementValue(self,value):
        if self.verbosity != 0:
            print "Value: %s" % value
    
    def endElement(self):
        self.currentDepth -= 1
    
    def getCurrentPosition(self):
        return 0
    
    def getSupportedMimeTypes(self):
        return []
    
    def getType(self):
        return self.db
    
    def select(self,xpath):
        return randint(0,1000)
