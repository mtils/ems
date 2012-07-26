'''
Created on 26.07.2012

@author: michi
'''
from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QGraphicsView

class FixableGraphicsView(QGraphicsView):
    
    scrollingEnabledStateChanged = pyqtSignal(bool)
    
    def __init__(self, *args, **kwargs):
        QGraphicsView.__init__(self, *args, **kwargs)
        self._scrollingEnabled = False
        self.setScrollingEnabled(False)
    
    def scrollingEnabled(self):
        return self._scrollingEnabled
    
    def setScrollingEnabled(self, enabled=True):
        if enabled == self._scrollingEnabled:
            return
        self._scrollingEnabled = enabled
        
        self.scrollingEnabledStateChanged.emit(self._scrollingEnabled)
        if enabled:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    
    def scrollContentsBy(self, dx, dy):
        if not self._scrollingEnabled:
            return
        QGraphicsView.scrollContentsBy(self, dx, dy)
