'''
Created on 26.07.2012

@author: michi
'''
from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QGraphicsView, QGraphicsItem

class FixableGraphicsView(QGraphicsView):
    
    scrollingEnabledStateChanged = pyqtSignal(bool)
    
    def __init__(self, *args, **kwargs):
        QGraphicsView.__init__(self, *args, **kwargs)
        self._scrollingEnabled = True
        self.setScrollingEnabled(False)
        self._permanentCenterOn = None
        self._isPermanentCenteredOnItem = False
    
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
    
    def permanentlyCenterOn(self, gfxItem):
        if not isinstance(gfxItem, QGraphicsItem):
            raise TypeError("FixedGraphicsView can only be centered on QGraphicsItem")
        self._permanentCenterOn = gfxItem
        self._isPermanentCenteredOnItem = True
    
    def isPermanentlyCentered(self):
        return isinstance(self._permanentCenterOn, QGraphicsItem)
    
    def resizeEvent(self, event):
        QGraphicsView.resizeEvent(self, event)
        if self._isPermanentCenteredOnItem:
            #print "frameWidth:", self.frameWidth(), 'myWidth:', self.width()
            self._permanentCenterOn.resize(self.width()-self.frameWidth(),
                                           self.height()-self.frameWidth())
            self.centerOn(self._permanentCenterOn)
