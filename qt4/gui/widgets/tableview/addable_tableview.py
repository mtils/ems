'''
Created on 04.08.2011

@author: michi
'''
import sys
from PyQt4.QtCore import QRect, Qt, QSize, QRectF, QObject, QEvent, pyqtSignal
from PyQt4.QtGui import QTableView, QHeaderView, QPainter, QPixmap, QStyle, \
    QStyleOptionButton, QIcon, QStandardItem

class HeaderEventFilter(QObject):
    def eventFilter(self, object, event):
        if(event.type() == QEvent.Paint):
            print self.parent()
            print "Hallo"
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
        self._addButtonRect = QRect()
        
        self.buttonIconSize = buttonIconSize
    
    def paintEvent(self, event):
        result = super(AddableVHeader, self).paintEvent(event)
        painter = QPainter(self.viewport())
        lastSection = self.model().rowCount() - 1
        if lastSection < 0:
            lastSection = 0
        

        y = self.sectionPosition(lastSection) + self.sectionSize(lastSection)
        self._addButtonRect = QRect(0, y,
                                    self.width(),
                                    self.defaultWidth)
        opt = QStyleOptionButton()
        opt.initFrom(self)
        opt.rect = self._addButtonRect
        opt.features = QStyleOptionButton.None
        opt.iconSize = self.buttonIconSize
        opt.state = QStyle.State_Enabled
        #opt.text = "H"
        opt.icon = self.addIcon
        
        self.style().drawControl(QStyle.CE_PushButton, opt, painter)

        return result
    
    def sizeHint(self):
        size = super(AddableVHeader, self).sizeHint()
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
        opt = QStyleOptionButton()
        opt.initFrom(self)
        opt.rect = rect
        opt.features = QStyleOptionButton.None
        opt.state = QStyle.State_Enabled
        opt.icon = self.removeIcon
        opt.iconSize = self.buttonIconSize
        
        self.style().drawControl(QStyle.CE_PushButton, opt, painter)
        
        #painter.drawImage(imgRect, self.removeImage)


class AddableTableView(QTableView):
    def __init__(self, addIcon, removeIcon, parent=None):
        QTableView.__init__(self, parent)
        self.setVerticalHeader(AddableVHeader(addIcon, removeIcon, self))
        #self.verticalHeader().addRowButtonClicked.connect(self.onAddRowButtonClicked)
        #self.verticalHeader().removeRowButtonClicked.connect(self.onRemoveRowButtonClicked)
    
    def onAddRowButtonClicked(self):
        l = []
        r = self.model().rowCount()
        for i in range(self.model().columnCount()):
            l.append(QStandardItem("%s:%s" % (r,i+1)))
        self.model().appendRow(l)
        print "addButton"
    
    def onRemoveRowButtonClicked(self, row):
        print "removeButton %s" % row
        self.model().takeRow(row)


if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)
    view = QTableView(app)
    view.show()
    app.exec_()
    