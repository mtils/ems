'''
Created on 01.02.2010

@author: michi
'''
import os.path
import sys

from PyQt4.QtGui import QApplication

from ems.util import platformName

class MainApplication(QApplication):
    '''
    classdocs
    '''

    def __init__(self,argv,appPath=None):
        '''
        Constructor
        '''
        QApplication.__init__(self,argv)

        if appPath is None:
            self.appPath = os.path.abspath(os.path.dirname(argv[0]))
        else:
            self.appPath = appPath
            
    def getRelativePath(self,path):
        rPath = path.replace(self.appPath, "")
        if rPath.startswith(os.path.sep):
            return rPath[1:]
        return rPath
    
    def getAbsolutePath(self, path):
        if os.path.isabs(path):
            return path
        if not path.startswith(os.path.sep):
            return os.path.join(self.appPath, path)
        return path
    
    def platform(self):
        return platformName()