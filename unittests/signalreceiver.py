'''
Created on 17.02.2011

@author: michi
'''
from PyQt4.QtCore import QObject

class SignalReceiver(QObject):
    def __init__(self,parent=None):
        super(SignalReceiver, self).__init__(parent)
        self.signalQueue = []
        
    def recSignal(self,*args):
        self.signalQueue.append(args)
    
    def curEntry(self):
        count = len(self.signalQueue)
        if count > 0:
            return self.signalQueue[count-1]
    
    def prevEntry(self):
        count = len(self.signalQueue)
        if count > 1:
            return self.signalQueue[count-2]
    