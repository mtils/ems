'''
Created on 04.10.2012

@author: michi
'''

from PyQt4.QtCore import pyqtSignal

from ems.qt4.applicationservice import ApplicationService #@UnresolvedImport

class ModelUpdateService(ApplicationService):
    
    objectIdsUpdated = pyqtSignal(str, list)
    
    objectsUpdated = pyqtSignal(str)
    
    modelUpdated = pyqtSignal()
    
    def triggerUpdate(self, modelObjectName, keys=None):
        if keys is not None:
            self.objectIdsUpdated.emit(modelObjectName, keys)
        else:
            self.objectsUpdated.emit(modelObjectName)
        self.modelUpdated.emit()