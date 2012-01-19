'''
Created on 19.01.2012

@author: michi
'''
class ProgressEmitter(object):
    def __init__(self):
        
        self.__globalProgress = 0
        self.__globalProgressRange = [0,0]
        self.__subProgress = 0
        self.__subProgressRange = [0,0]
        
        self.__currentGlobalProgressStep = None
        self.__currentSubProgressStep = None
        
        self.onGlobalProgressChanged = None
        self.onGlobalRangeChanged = None
        
        self.onSubProgressChanged = None
        self.onSubProgressRangeChanged = None
        
        self.onGlobalStepChanged = None
        self.onSubStepChanged = None
        
        self.onFinished = None
    
    def increaseGlobalProgress(self):    
        self._setGlobalProgress(self.__globalProgress + 1)
    
    def setGlobalProgress(self, progressValue, params=None):
        self.__globalProgress = progressValue
        if callable(self.onGlobalProgressChanged):
            self.onGlobalProgressChanged(progressValue, params)
        if self.__globalProgress == self.__globalProgressRange[1]:
            self.setFinished(True)
    
    def setGlobalProgressRange(self, minValue, maxValue, params=None):
        self.__globalProgress = [minValue, maxValue]
        if callable(self.onGlobalRangeChanged):
            self.onGlobalRangeChanged(minValue, maxValue, params)
    
    def setSubProgressRange(self, minValue, maxValue, params=None):
        self.__subProgressRange = [minValue, maxValue]
        if callable(self.onSubProgressRangeChanged):
            self.onSubProgressRangeChanged(minValue, maxValue, params)
    
    def setSubProgress(self, progressValue, params=None):
        self.__subProgress = progressValue
        if callable(self.onSubProgressChanged):
            self.onSubProgressChanged(progressValue, params)
        
    def increaseSubProgress(self, params=None):
        self.setSubProgress(self.__subProgress + 1, params)
    
    def setGlobalProgressStep(self, step, params=None):
        self.setSubProgress(0,params)
        self.__currentGlobalProgressStep = step
        if callable(self.onGlobalStepChanged):
            self.onGlobalStepChanged(step, params)
    
    def setSubProgressStep(self, step, params=None):
        self.__currentSubProgressStep = step
        if callable(self.onSubStepChanged):
            self.onSubStepChanged(step, params)
    
    def setFinished(self, isFinished=True):
        if callable(self.onFinished):
            self.onFinished()