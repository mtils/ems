
from ems.app import app
from ems.qt import QtWidgets, QtCore, QtQuick

QWidget = QtWidgets.QWidget
QDialog = QtWidgets.QDialog
QQuickItem = QtQuick.QQuickItem
pyqtProperty = QtCore.pyqtProperty
QPointF = QtCore.QPointF
Qt = QtCore.Qt

class QQuickViewWidget(QWidget):

    def __init__(self, item):
        super(QQuickViewWidget, self).__init__()
        self._item = None
        self._selfChanging = False
        self._setItem(item)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def getItem(self):
        return self._item

    item = pyqtProperty(QQuickItem, getItem)

    def _setItem(self, item):
        self._item = item
        #self.item.widget = self
        app().browser = self
        self.item.destroyed.connect(self._closeAndDestroy)
        self.item.window().destroyed.connect(self._closeAndDestroy)
        self.item.window().xChanged.connect(self._updateByItem)
        self.item.window().yChanged.connect(self._updateByItem)
        self.item.window().widthChanged.connect(self._updateByItem)
        self.item.window().heightChanged.connect(self._updateByItem)
        self._updateByItem()


    def resizeEvent(self, event):
        if not self._selfChanging:
            #self.resize(event.oldSize())
            event.ignore()

    def moveEvent(self, event):
        if not self._selfChanging:
            #self.move(event.oldPos())
            event.ignore()

    def _updateByItem(self):
        print("_updateByItem")
        self._selfChanging = True
        self.raise_()
        offset = self._item.mapToScene(QPointF(self._item.x(), self._item.y()))
        self.move(self._item.window().x() + offset.x() , self._item.window().y() + offset.y())
        self.resize(self._item.width(), self._item.height())
        self._selfChanging = False

    def _closeAndDestroy(self, *args):
        print("_closeAndDestroy")
        item = self._item
        if not item:
            return
        window = item.window()
        self.destroy()
        #del self