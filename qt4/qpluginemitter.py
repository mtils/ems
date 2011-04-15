'''
Created on 09.02.2011

@author: michi
'''
from PyQt4.QtCore import QObject,SIGNAL

class QPluginEmitter(QObject):
    def notify(self,caller,eventName,params):
        parString = [eventName,'(']
        comma = ''
        for par in params:
            parString.append(comma)
            parString.append('PyQt_PyObject')
            comma = ','
        parString.append(")")
        signalName = "".join(parString)
        self.emit(SIGNAL(signalName),*params)
