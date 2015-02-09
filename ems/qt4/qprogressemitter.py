'''
Created on 19.01.2012

@author: michi
'''

from PyQt4.QtCore import QObject, pyqtSignal, QString

from ems.view.progressemitter import ProgressEmitter #@UnresolvedImport

class QProgressEmitter(QObject, ProgressEmitter):
    
    globalProgressChanged = pyqtSignal(int)
    globalRangeChanged = pyqtSignal(int, int)
        
    subProgressChanged = pyqtSignal(int)
    subRangeChanged = pyqtSignal(int, int)
        
    globalStepChanged = pyqtSignal(int)
    subStepChanged = pyqtSignal(int)
    
    globalStepMessageChanged = pyqtSignal(QString)
    subStepMessageChanged = pyqtSignal(QString)
        
    finished = pyqtSignal(bool)
    
    
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        ProgressEmitter.__init__(self)
        
        self.__lastParams = None
        self.globalStepMessages = {}
        self.subStepMessages = {}
    
    def setGlobalProgress(self, progressValue, params=None):
        ProgressEmitter.setGlobalProgress(self, progressValue, params)
        self.__lastParams = params
        self.globalProgressChanged.emit(progressValue)
        
    
    def setGlobalProgressRange(self, minValue, maxValue, params=None):
        ProgressEmitter.setGlobalProgressRange(self, minValue, maxValue, params)
        self.__lastParams = params
        self.globalRangeChanged.emit(minValue, maxValue)
    
    def setSubProgressRange(self, minValue, maxValue, params=None):
        ProgressEmitter.setSubProgressRange(self, minValue, maxValue, params)
        self.__lastParams = params
        self.subRangeChanged.emit(minValue, maxValue)
    
    def setSubProgress(self, progressValue, params=None):
        ProgressEmitter.setSubProgress(self, progressValue, params)
        self.__lastParams = params
        self.subProgressChanged.emit(progressValue)
    
    def setGlobalProgressStep(self, step, params=None):
        ProgressEmitter.setGlobalProgressStep(self, step, params)
        self.__lastParams = params
        self.globalStepChanged.emit(step)
        if self.globalStepMessages.has_key(step):
            if isinstance(params, (int, float, basestring, QString)):
                msg = QString.fromUtf8(self.globalStepMessages[step]).arg(params)
            else:
                msg = QString.fromUtf8(self.globalStepMessages[step])
            self.globalStepMessageChanged.emit(msg)
    
    def setSubProgressStep(self, step, params=None):
        ProgressEmitter.setSubProgressStep(self, step, params)
        self.__lastParams = params
        self.subStepChanged.emit(step)
        if self.subStepMessages.has_key(step):
            if isinstance(params, (int, float, basestring, QString)):
                msg = QString.fromUtf8(self.subStepMessages[step]).arg(params)
            else:
                msg = QString.fromUtf8(self.subStepMessages[step])
            self.subStepMessageChanged.emit(msg)
    
    def setFinished(self, isFinished=True):
        ProgressEmitter.setFinished(self, isFinished)
        self.finished.emit(isFinished)
    
    def params(self):
        return self.__lastParams
    
    def setGlobalStepMessage(self, stepId, message):
        self.globalStepMessages[stepId] = message
    
    def setSubStepMessage(self, stepId, message):
        self.subStepMessages[stepId] = message