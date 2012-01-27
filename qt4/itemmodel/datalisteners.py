'''
Created on 06.04.2011

@author: michi
'''

from PyQt4.QtCore import QObject, pyqtSignal, Qt, QTimer

class DisplayedRowsListener(QObject):
    
    visibleRowsChanged = pyqtSignal(int,int)
    
    def __init__(self, timeout=200, parent=None):
        QObject.__init__(self, parent)
        self.timeout = timeout
    
    def listenTo(self, itemView):
        self.scrollBar = itemView.verticalScrollBar()
        self.scrollBar.valueChanged.connect(self.onValueChanged)
        self.scrollBar.rangeChanged.connect(self.onRangeChanged)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.onTimeOut)
        self.timer.start(self.timeout)
    
        
    def onValueChanged(self, value):
        self.timer.stop()
        self.timer.start(self.timeout)
    
    def onRangeChanged(self, scrollMin, scrollMax):
        self.timer.stop()
        self.timer.start(self.timeout)
    
    def onTimeOut(self):
        self.visibleRowsChanged.emit(self.scrollBar.sliderPosition(),
                                     self.scrollBar.sliderPosition()+self.scrollBar.pageStep())
        self.timer.stop()