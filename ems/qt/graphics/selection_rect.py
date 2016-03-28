
from ems.qt import QtWidgets, QtGui, QtCore

QGraphicsItem = QtWidgets.QGraphicsItem
QGraphicsObject = QtWidgets.QGraphicsObject
QObject = QtCore.QObject
pyqtProperty = QtCore.pyqtProperty
QStyle = QtWidgets.QStyle
QBrush = QtGui.QBrush
QColor = QtGui.QColor
QRectF = QtCore.QRectF
Qt = QtCore.Qt
QEvent = QtCore.QEvent

class SelectionRect(QGraphicsObject):

    def __init__(self, parent=None):
        super(SelectionRect, self).__init__(parent)
        self._target = None
        self._visible = None
        self._margin = 10.0
        self.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable)

    def getTarget(self):
        return self._target

    def setTarget(self, target):
        if self._target is target or target is self:
            return
        if self._target:
            self._target.removeSceneEventFilter(self)
        self._target = target
        if self.scene() is not self._target.scene():
            self._target.scene().addItem(self)
        #self._target.positionChanged += self._moveWithTarget
        self._target.installSceneEventFilter(self)
        self.setPos(self._target.pos())
        self.setZValue(self._target.zValue()-1)

    target = pyqtProperty(QGraphicsItem, getTarget, setTarget)

    def boundingRect(self):
        if not self._target:
            return QRectF()
        targetRect = self._target.boundingRect()
        myRect = QRectF(targetRect.topLeft(), targetRect.size())
        myRect.setWidth(targetRect.width() + self._margin + self._margin)
        myRect.setHeight(targetRect.height() + self._margin + self._margin)
        #myRect.moveLeft(self._margin)
        myRect.moveTo(targetRect.x() - self._margin, targetRect.y() - self._margin)

        return myRect

    def paint(self, painter, option, widget=None):
        #super(TextItem, self).paint(painter, option, widget)

        #if not (option.state & QStyle.State_Selected):
            #return
        rect = self.boundingRect()

        innerRect = self._target.boundingRect()

        #w = rect.width()
        #h = rect.height()
        #s = 4
        brush = QBrush(QColor(128,179,255))
        #painter.setPen(Qt.NoPen)
        brush.setStyle(Qt.NoBrush)
        painter.setBrush(brush)
        #painter.setColor(QColor(128,179,255))
        painter.drawRect(innerRect)
        painter.drawRect(rect)
        #painter.fillRect(0, 0, s,  s, brush);
        #painter.fillRect(0, 0 + h - s, s, s, brush);
        #painter.fillRect(0 + w - s, 0, s, s, brush);

    def mouseMoveEvent(self, event):
        super(SelectionRect, self).mouseMoveEvent(event)
        self._target.setPos(self.pos())

    def sceneEventFilter(self, watched, event):
        return False
        print("event", event.type())
        # Redirect Mouse move to self
        if event.type() != QEvent.GraphicsSceneMouseMove:
            return False
        self.mouseMoveEvent(event)
        return True

    def _moveWithTarget(self, position):
        self.setPos(position)
