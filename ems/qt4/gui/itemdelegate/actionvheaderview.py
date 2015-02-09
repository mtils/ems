'''
Created on 07.06.2011

@author: michi
'''
from PyQt4.QtCore import Qt, QSize, QRect
from PyQt4.QtGui import QHeaderView, QAction, QTableView

class ParamAction(QAction):
    def triggerWithParams(self, model, row, additionalParams={}):
        self.trigger()
        
class ActionVHeaderView(QHeaderView):
    
    def __init__(self, iconSize=16, parent=None, additionalParams={}):
        if not isinstance(parent, QTableView):
            raise TypeError("Parent has to be QTableView")
        super(ActionVHeaderView, self).__init__(Qt.Vertical, parent)
        self._actions = []
        self._additionalParams = additionalParams
        self.margin = 4
        if isinstance(iconSize, QSize):
            self.setIconSize(iconSize)
        else:
            self.setIconSize(QSize(iconSize,iconSize))
        
    def mousePressEvent(self, event):
        action = self.actionAt(event.pos())
        
        if action is not None:
            if isinstance(action, ParamAction):
                action.triggerWithParams(self.parent().model(),
                                         self.parent().rowAt(event.y()),
                                         self._additionalParams)
            else:
                action.trigger()
    
    def mouseMoveEvent(self, event):
        action = self.actionAt(event.pos())
        if action is not None:
            self.setToolTip(action.text())
    
    def actionAt(self, point):
        for action in self._actions:
            for rect in action.localRects:
                if rect.contains(point):
                    return action
    
    def sizeHint(self):
#        width = (len(self._actions)* (self.iconSize().width() + self.margin)) +\
#            self.margin + super(ActionVHeaderView, self).sizeHint().width()
        width = (len(self._actions)* (self.iconSize().width() + self.margin)) +\
            self.margin
        return QSize(width,24)
    
    def addAction(self, action):
        action.localRects = []
        self._actions.append(action)

    def paintSection(self, painter, rect, index):
        #super(ActionVHeaderView, self).paintSection(painter, rect, index)
        xOffset = rect.x()
        for action in self._actions:
            iconRect = QRect(xOffset+self.margin,
                             rect.y() + ((rect.height()/2) - (self.iconSize().height()/2)),
                             self.iconSize().width(),
                             self.iconSize().height())
            
            action.localRects.append(iconRect)
            painter.drawImage(iconRect,action.icon().pixmap(self.iconSize()).toImage())
            xOffset += (self.iconSize().width() + self.margin)
    