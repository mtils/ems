'''
Created on 24.07.2012

@author: michi
'''
from PyQt4.QtCore import pyqtSignal, pyqtSlot
from PyQt4.QtGui import QAction

class Action(QAction):
    def __init__(self, *args, **kwargs):
        QAction.__init__(self, *args, **kwargs)
        