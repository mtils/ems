'''
Created on 04.08.2011

@author: michi
'''
import sys
from PyQt4.QtCore import QRect, Qt, QSize, QRectF, QObject, QEvent, pyqtSignal
from PyQt4.QtGui import QTableView, QHeaderView, QPainter, QPixmap, QStyle, \
    QStyleOptionButton, QIcon, QStandardItem, QWidget, QScrollBar

class HeaderEventFilter(QObject):
    def eventFilter(self, object, event):
        if(event.type() == QEvent.Paint):
            print self.parent()
        else:
            print event.type()
        return False

class AddableVHeader(QHeaderView):
    
    removeRowButtonClicked = pyqtSignal(int)
    addRowButtonClicked = pyqtSignal()
    
    def __init__(self, addIcon, removeIcon, parent=None,
                 hMargin=5, vMargin=2, defaultWidth=32,
                 buttonIconSize=QSize(20,20)):
        QHeaderView.__init__(self, Qt.Vertical, parent)
        self.hMargin = hMargin
        self.vMargin = vMargin
        self.addIcon = addIcon
        self.removeIcon = removeIcon
        self.defaultWidth = defaultWidth
        self._addButtonRect = QRect(0, 0,
                                    self.width(),
                                    self.defaultWidth)
        #self.setViewport(AddableViewport(self))
        
        self.buttonIconSize = buttonIconSize
    
    def paintEvent(self, event):
        result = super(AddableVHeader, self).paintEvent(event)
        painter = QPainter(self.viewport())
        lastSection = self.model().rowCount()
        if lastSection < 0:
            lastSection = 0
        
        if self.model().rowCount() == 0:
            rect = QRect(0, 0,self.width(), self.defaultWidth)
            self._drawButton(painter, rect, True)
            return result
    
    def _drawButton(self, painter, rect, add=False):
            

            opt = QStyleOptionButton()
            opt.initFrom(self)
            opt.rect = rect
            opt.features = QStyleOptionButton.None
            opt.iconSize = self.buttonIconSize
            opt.state = QStyle.State_Enabled
            #opt.text = "H"
            if add:
                opt.icon = self.addIcon
            else:
                opt.icon = self.removeIcon
            
            self.style().drawControl(QStyle.CE_PushButton, opt, painter)
    
#    def size(self):
#        height = super(AddableVHeader, self).size()
##        print "ich werde gefragt"
#        return height
    
    def sizeHint(self):
        size = super(AddableVHeader, self).sizeHint()
        #print "sizeHint %s" % size.height()
        newSize = QSize(self.defaultWidth, size.height())
        
        #newSize.setWidth(self.removeIcon.pixmap().width() + self.hMargin + self.hMargin) 
        return newSize
    
    def mousePressEvent(self, event):
        if self._addButtonRect.contains(event.pos()):
            self.addRowButtonClicked.emit()
            return QHeaderView.mousePressEvent(self, event)
        row = self.parent().rowAt(event.pos().y())
        if row != -1:
            self.removeRowButtonClicked.emit(row)
        return QHeaderView.mousePressEvent(self, event)
        
    def paintSection(self, painter, rect, row):
        if row == 0:
            self._drawButton(painter, rect, True)
        else:
            self._drawButton(painter, rect, False)
            

class AddableViewport(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
    
    def resizeEvent(self, event):
        res = super(AddableViewport, self).resizeEvent(event)
        return res
    
    def height(self):
        height = super(AddableViewport, self).height()
        return height + 32
    
    def size(self):
        size = super(AddableViewport, self).size()
        return size
    
    def geometry(self, *args, **kwargs):
        size = QWidget.geometry(self, *args, **kwargs)
        return size
    
    def _getattribute__(self, name):
        att = super(AddableViewport, self).__getattribute__(name)

        return att
#    def minimumSizeHint(self):
#        size = super(AddableViewport, self).minimumSizeHint()
#        print size
#        return size
class CustomScrollbar(QScrollBar):
    def __init__(self, parent=None):
        QScrollBar.__init__(self, parent)
    
    def maximum(self, *args, **kwargs):
        
        max = QScrollBar.maximum(self, *args, **kwargs)
        return max
        
class AddableTableView(QTableView):
    def __init__(self, addIcon, removeIcon, parent=None):
        QTableView.__init__(self, parent)
        self.setVerticalHeader(AddableVHeader(addIcon, removeIcon, self))
        #self.setVerticalScrollBar(CustomScrollbar(self))
        #print self.viewport().styleSheet()
        #self.viewport().setStyleSheet('margin-bottom: 32px;')
        #self.setViewport(AddableViewport(self))
        #print self.viewOptions()
        #self.setViewportMargins(0, 0, 0, self.verticalHeader().defaultWidth)
        #self.verticalHeader().addRowButtonClicked.connect(self.onAddRowButtonClicked)
        #self.verticalHeader().removeRowButtonClicked.connect(self.onRemoveRowButtonClicked)
    
#    def sizeHint(self):
#        size = super(AddableTableView, self).sizeHint()
#        print size
#        size.setHeight(size.height() + self.verticalHeader().defaultWidth)
#        print size
#        return size

    def resizeEvent_(self, event):
        res = QTableView.resizeEvent(self, event)
        self.verticalScrollBar().setMaximum(self.verticalScrollBar().maximum())
        return res
    
    def onAddRowButtonClicked(self):
        l = []
        r = self.model().rowCount()
        for i in range(self.model().columnCount()):
            l.append(QStandardItem("%s:%s" % (r,i+1)))
        self.model().appendRow(l)
    
    def onRemoveRowButtonClicked(self, row):
        self.model().takeRow(row)
    
    
#    def updateEditorGeometries(self, *args, **kwargs):
#        res = None
#        #res = QTableView.updateEditorGeometries(self, *args, **kwargs)
#        print "updateEditor %s" % res
#        return res
    


if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)
    view = QTableView(app)
    view.show()
    app.exec_()
    