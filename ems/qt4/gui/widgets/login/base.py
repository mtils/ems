'''
Created on 23.09.2011

@author: michi
'''
from PyQt4.QtGui import QGridLayout, QLabel, QWidget

from ems.qt4.gui.widgets.dialogable import DialogableWidget

class LoginBaseWidget(DialogableWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=None)
    