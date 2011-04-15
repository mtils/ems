'''
Created on 10.01.2011

@author: michi
'''
from PyQt4.QtGui import QItemDelegate,QStyledItemDelegate
from PyQt4.QtCore import Qt

class TrDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super(TrDelegate, self).__init__(parent)
        self.delegates = {}
        print "ich bins"
    
    def draw(self, painter, option, index):
        pass
    def drawDisplay(self, painter, option, rect, text):
        print text
#        super(TrDelegate, self).drawDisplay(painter, option, rect, text)
