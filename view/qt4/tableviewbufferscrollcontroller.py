'''
Created on 21.01.2011

@author: michi
'''
from PyQt4.QtCore import QObject,SIGNAL
from PyQt4.QtGui import QResizeEvent,QAbstractItemView,QScrollBar

class TableViewBufferScrollController(QObject):
    def __init__(self, parent):
        if not isinstance(parent, QAbstractItemView):
            raise TypeError('Parent Arg has to be instanceof QAbstractItemView')
        super(TableViewBufferScrollController, self).__init__(parent)
        parent.verticalScrollBar().installEventFilter(self)
        self.tableView = parent
        self.vHeader = parent.verticalHeader()
#        parent.setVerticalScrollBar(QScrollBar(parent))
        self.vScrollBar = parent.verticalScrollBar()
        self.vScrollBar.setTracking(True)
        self.connect(self.vScrollBar, SIGNAL("valueChanged(int)"), self.on_scroll)
    
    def on_scroll(self, value):
        pass
        
    def eventFilter(self, object, event):
        if isinstance(event, QResizeEvent):
            #1128 Results gesamt
            #ScrollBarValue ist immer getFirstVisibleIndex!!
#            print object.verticalOffset()

            self.vScrollBar.setMaximum(self.getScrollBarMaximum())
            self.vScrollBar.setValue(self.getFirstVisibleIndex())
            self.vScrollBar.setPageStep(10)

        return False
    
    def getFirstVisibleIndex(self):
        return self.vHeader.visualIndexAt(1)
    
    def getLastVisibleIndex(self):
        return self.vHeader.visualIndexAt(self.vHeader.height()-1)
    
    def getVisibleRowsCount(self):
        return self.getLastVisibleIndex() - self.getFirstVisibleIndex()
    
    def getScrollBarMaximum(self):
        return 1128 - self.getVisibleRowsCount()