'''
Created on 04.08.2011

@author: michi
'''
import sys
from PyQt4.QtCore import QRect, Qt, QSize, QRectF, QObject, QEvent
from PyQt4.QtGui import QTableView, QHeaderView, QPainter, QPixmap, QStyle, \
    QStyleOptionButton, QIcon

class HeaderEventFilter(QObject):
    def eventFilter(self, object, event):
        if(event.type() == QEvent.Paint):
            print self.parent()
            print "Hallo"
        else:
            print event.type()
        return False
class AddableHeader(QHeaderView):
    def __init__(self, addIcon, removeIcon, parent=None,
                 hMargin=5, vMargin=2, defaultWidth=32,
                 buttonIconSize=QSize(22,22)):
        QHeaderView.__init__(self, Qt.Vertical, parent)
        self.hMargin = hMargin
        self.vMargin = vMargin
        self.addIcon = addIcon
        self.removeIcon = removeIcon
        self.defaultWidth = defaultWidth
        self._addImageDims = {
                                'width':0,
                                'height':0,
                                'widthHalf':0,
                                'heightHalf':0
                                }
        self._removeImageDims = {
                                'width':0,
                                'height':0,
                                'widthHalf':0,
                                'heightHalf':0
                                }
        self.buttonIconSize = buttonIconSize
    
    def paintEvent(self, event):
        result = super(AddableHeader, self).paintEvent(event)
        painter = QPainter(self.viewport())
        lastSection = self.model().rowCount() - 1
        if lastSection < 0:
            lastSection = 0
        

        y = self.sectionPosition(lastSection) + self.sectionSize(lastSection)
        addImageSectionRect = QRect(0, y,
                                    self.width(),
                                    #self.sectionSize(lastSection)
                                    self.defaultWidth)
        
        #painter.drawImage(addImageSectionRect, self._addImage)
        
        opt = QStyleOptionButton()
        opt.initFrom(self)
        opt.rect = addImageSectionRect
        opt.features = QStyleOptionButton.None
        opt.iconSize = self.buttonIconSize
        opt.state = QStyle.State_Enabled
        #opt.text = "H"
        opt.icon = self.addIcon
        
        self.style().drawControl(QStyle.CE_PushButton, opt, painter)

        return None
    
    def sizeHint(self):
        size = super(AddableHeader, self).sizeHint()
        newSize = QSize(self.defaultWidth, size.height())
        #newSize.setWidth(self.removeIcon.pixmap().width() + self.hMargin + self.hMargin) 
        return newSize
    
    def mousePressEvent(self, event):
        print event.pos()
        return QHeaderView.mousePressEvent(self, event)
        #action = self.actionAt(event.pos())
        
        #if action is not None:
        #    if isinstance(action, ParamAction):
        #        action.triggerWithParams(self.parent().model(),
        #                                 self.parent().rowAt(event.y()),
        #                                 self._additionalParams)
        #    else:
        #        action.trigger()
        
    def paintSection(self, painter, rect, row):
#        imgRect = QRect(rect)
#        imgRect.setX(rect.x()+self.hMargin)
#        imgRect.setY( rect.y() + ((rect.height()/2) - self._removeImageDims['heightHalf']))
#        imgRect.setWidth(self._removeImage.width())
#        imgRect.setHeight(self._removeImage.height())
        
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
    def __init__(self, addImage, removeImage, parent=None):
        QTableView.__init__(self, parent)
        self.setVerticalHeader(AddableHeader(addImage, removeImage, self))
    


if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)
    view = QTableView(app)
    view.show()
    app.exec_()
    