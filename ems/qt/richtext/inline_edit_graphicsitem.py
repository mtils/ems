
from ems.qt import QtCore, QtGui

class TextItem(QGraphicsTextItem):

    def __init__(self, text, position, scene,
                 font=QFont("Times", PointSize), matrix=QMatrix()):
        super(TextItem, self).__init__(text)
        self.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable)
        self.setFont(font)
        self.setPos(position)
        self.setMatrix(matrix)
        scene.clearSelection()
        scene.addItem(self)
        self.setSelected(True)
        global Dirty
        Dirty = True
        self.setTextInteractionFlags(Qt.TextEditable | Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)


    def parentWidget(self):
        return self.scene().views()[0]


    def itemChange(self, change, variant):
        if change != QGraphicsItem.ItemSelectedChange:
            global Dirty
            Dirty = True
        return QGraphicsTextItem.itemChange(self, change, variant)


    def mouseDoubleClickEvent(self, event):
        dialog = TextItemDlg(self, self.parentWidget())
        dialog.exec_()
       
    def hoverEnterEvent(self, event):
        print "HoverEnter"
        print event.pos()
        print self.boundingRect()
        self.setCursor(Qt.IBeamCursor)
        QGraphicsTextItem.hoverEnterEvent(self, event)
    
    def hoverLeaveEvent(self, event):
        print "HoverLeave"
        
        QGraphicsTextItem.hoverLeaveEvent(self, event)