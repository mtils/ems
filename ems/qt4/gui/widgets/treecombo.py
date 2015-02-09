'''
Created on 27.06.2011

@author: michi
'''
from PyQt4.QtCore import QVariant, Qt, pyqtSlot, QTimer, SLOT, QString, \
    QAbstractItemModel, QModelIndex, pyqtSignal, QPoint, QObject, QEvent
from PyQt4.QtGui import QComboBox, QTreeWidget, QTreeWidgetItem, \
    QTreeWidgetItemIterator, QStyledItemDelegate, QWidget, QVBoxLayout
from ems.qt4.util import variant_to_pyobject
    

class TreeWidgetIterator(object):
    def __init__(self, parent):
        self.parent = parent
        self._it = QTreeWidgetItemIterator(self.parent)
        
    def __iter__(self):
        return self
        
    def next(self):
        item = self._it.value()
        self._it += 1
        if not item:
            raise StopIteration
        return item


class ViewPortEventFilter(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
    
    def eventFilter(self, obj, event):
        #print "EventFilter"
        if event.type() == QEvent.MouseButtonPress:
            return True
        return False

class CustomTreeWidgetViewPort(QWidget):
    def __init__(self, parent=None):
        super(CustomTreeWidgetViewPort, self).__init__(parent)
    
    def mousePressEvent(self, event):
        pass


class CustomTreeWidget(QTreeWidget):
    
    itemSelected = pyqtSignal(QTreeWidgetItem)
    closed = pyqtSignal()
    
    def __init__(self, parent=None):
        super(CustomTreeWidget, self).__init__(parent)
        #self.setViewport(CustomTreeWidgetViewPort(self))
        #print self.viewport().parent()
        #print self.viewport().installEventFilter(ViewPortEventFilter(self.viewport()))
    
    def preShow(self):
        #print "preShowCalled"
        pass
        #self.grabKeyboard()
        #self.viewport().grabMouse()
        
    def mousePressEvent(self, event):
        result = super(CustomTreeWidget, self).mousePressEvent(event)
        #return result
        if event.button() == Qt.LeftButton:
            self.close()
        return result
    
    def mouseReleaseEvent_(self, event):
        pass#print "Ich bin dat"
        
    
    def keyPressEvent(self, event):
        result = super(CustomTreeWidget, self).keyPressEvent(event)
        
        if event.key() in(Qt.Key_Escape, Qt.Key_Return, Qt.Key_Enter):
            self.close()
        return result
    
    def close_(self):
        result = super(CustomTreeWidget, self).close()
#        item = self.currentItem().text(0)
#        if isinstance(item, QTreeWidgetItem):
#            self.itemSelected.emit(item)
        self.closed.emit()
#        self.releaseMouse()
#        self.releaseKeyboard()
        return None
        return result
        

class FlatTreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        self._items = {}
        super(FlatTreeModel, self).__init__(parent)
        self.pathSeparator = u' > '
        
    def data(self, index, role=Qt.DisplayRole):
#        print "data r:%s c:%s" % (index.row(), index.column())
        row = index.row()
        col = index.column()
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()
        if role == Qt.DisplayRole:
            if self._items.has_key(row):
                return self._items[row][col]
        if role == Qt.UserRole:
            if self._items.has_key(row):
                return self._items[row][1]
        return QVariant()
    
    def append(self, treeWidgetItem):
        self.beginResetModel()
        nextIndex = len(self._items)
        treeWidgetItem.flatIndex = nextIndex
        self._items[nextIndex] = {}
        name = self.buildDisplayedName(treeWidgetItem)
        self._items[nextIndex][0] = QVariant(QString.fromUtf8(name))
        self._items[nextIndex][1] = QVariant(treeWidgetItem.text(1))
        self.endResetModel()
    
    
    def buildDisplayedName(self, item ):
        stack = self._buildDisplayedStack(item)
        stack.reverse()
        return self.pathSeparator.join(stack)
    
    def _buildDisplayedStack(self, item, stack=None):
        
        if stack is None:
            stack = []
        if isinstance(item.parent(), QTreeWidgetItem):
            stack.append(unicode(item.text(0)))
            self._buildDisplayedStack(item.parent(),stack)
        else:
            stack.append(unicode(item.text(0)))
        return stack
        
    def rowCount(self, parent=QModelIndex()):
        return len(self._items)
    
    def columnCount(self, parent=QModelIndex()):
        return 1
    
    def index(self, row, col, parent=QModelIndex()):
        return self.createIndex(row, col)
    
    def parent(self, index):
        return QModelIndex()

class TreeComboBox(QComboBox):
    def __init__(self, parent=None):
        super(TreeComboBox, self).__init__(parent)
        self.itemTreeView = CustomTreeWidget(self)
        self.itemTreeView.setColumnCount(1)
        self.itemTreeView.setHeaderHidden(True)
        self.itemTreeView.setWindowFlags(self.itemTreeView.windowFlags() | Qt.Popup)
        #self.setView(self.itemTreeView)
        #self.setModel(self.view())
        self.flatModel = FlatTreeModel(self)
        self.setModel(self.flatModel)
        self._flatItemTree = {}
        self.initialExpand = True
        self.__nextCurrentIndex = None
        self.__currentText = ''
        #print self.itemView
        
        self.itemTreeView.currentItemChanged.connect(self.onCurrentItemChanged)
        self.itemTreeView.closed.connect(self.hidePopup)
        
    @pyqtSlot()
    def hidePopup(self):
        #print "hidePopup"
        super(TreeComboBox, self).hidePopup()
        
    def onCurrentItemChanged(self, cur, prev):
        self.setCurrentIndex(cur.flatIndex)
        #print "onCurrentItemChanged %s %s" % (cur.text(0), cur.flatIndex)
    
    
    def value(self):
        return self.itemData(self.currentIndex(), Qt.UserRole)
    
    def setValue(self, value):
        for i in range(self.count()):
            if variant_to_pyobject(self.itemData(i)) == value:
                self.setCurrentIndex(i)
    
    def addItemFlat(self, depth, texts):
        
        self._flatItemTree[depth] = QTreeWidgetItem(texts)
        
        if depth == 0:
            self.itemTreeView.addTopLevelItem(self._flatItemTree[depth])
            self.flatModel.append(self._flatItemTree[depth])
        else:
            newItem = QTreeWidgetItem(texts)
            self._flatItemTree[depth-1].addChild(newItem)
            self._flatItemTree[depth] = newItem
            self.flatModel.append(newItem)
            
#    def keyPressEvent(self, event):
#        return super(TreeComboBox, self).keyPressEvent(event)
#   
#    def mousePressEvent(self, event):
#        print "TreeWidget:mousePressEvent"
#        super(TreeComboBox, self).mousePressEvent(event)
#    
#    def mouseReleaseEvent(self, event):
#        print "TreeWidget:mouseReleaseEvent"
#        super(TreeComboBox, self).mouseReleaseEvent(event)
    
    def showPopup(self):
        self.itemTreeView.expandAll()
        pos = QPoint(self.pos())
        pos.setY(pos.y()+self.height())
        #pos.setX(pos.x()-200)
        self.itemTreeView.move(self.parent().mapToGlobal(pos))
        self.itemTreeView.setMinimumWidth(self.width())
        self.itemTreeView.setMaximumWidth(self.width())
        self.itemTreeView.preShow()
        self.itemTreeView.show()

if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import QApplication, QDialog, QHBoxLayout
    
    app = QApplication(sys.argv)
    dlg = QDialog()
    dlg.setLayout(QHBoxLayout(dlg))
    dlg.setMinimumWidth(300)
    dlg.combo = TreeComboBox(dlg)
    dlg.layout().addWidget(dlg.combo)
    
    dlg.combo.addItemFlat(0, ('Opa',))
    dlg.combo.addItemFlat(1, ('Name',))
    dlg.combo.addItemFlat(1, ('Vorname',))
    dlg.combo.addItemFlat(0, ('Oma',))
    
    dlg.exec_()
    
    
    
    app.exec_()