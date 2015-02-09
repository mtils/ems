'''
Created on 19.02.2011

@author: michi
'''
from PyQt4.QtCore import QObject,pyqtSignal,QCoreApplication,QEventLoop

from ems.converter.plugin import Plugin
from ems.converter.inputreader import InputReaderPlugin

class QReaderEmitter(InputReaderPlugin,QObject):
    
    stateChanged = pyqtSignal(int)
    
    progressChanged = pyqtSignal(int)
    
    def __init__(self,parent=None):
        QObject.__init__(self,parent)
        self.pollProcessEvents = True
        self.counter = 0
    
    def notifyStateChange(self,state):
        if state == Plugin.startProcess:
            self.counter = 0
        self.stateChanged.emit(state)
    
    def notifyProgress(self):
        self.counter += 1
        self.progressChanged.emit(self.counter)
        if self.pollProcessEvents:
            QCoreApplication.processEvents(flags=QEventLoop.AllEvents)
