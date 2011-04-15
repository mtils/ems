'''
Created on 01.02.2010

@author: michi
'''
import os.path

from PyQt4.QtGui import QApplication


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
        