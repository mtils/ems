'''
Created on 27.06.2011

@author: michi
'''
from PyQt4.QtCore import QVariant, Qt, pyqtSlot, QTimer, SLOT, QString, \
    QAbstractItemModel, QModelIndex, pyqtSignal
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

class TreePopupDelegate(QStyledItemDelegate):
    def setModelData(self, editor, model, index):
        #print model.data(index)
        return super(TreePopupDelegate, self).setModelData(editor, model, index)
        
    def setEditorData(self, editor, index):
        #print index
        return super(TreePopupDelegate, self).setEditorData(editor, index)
    
    def paint(self, painter, option, index):
        super(TreePopupDelegate, self).paint(painter, option, index)
    
    def createEditor(self, parent, option, index):
        #print "createEditor"
        return super(TreePopupDelegate, self).createEditor(parent, option, index)
    
    def editorEvent(self, event, model, option, index):
        #print "editorEvent %s %s %s %s" % (event, model, option, index)
        return super(TreePopupDelegate, self).editorEvent(event, model, option, index)

class CustomTreeWidget(QTreeWidget):
    closed = pyqtSignal()
    def __init__(self, parent=None):
        super(CustomTreeWidget, self).__init__(parent)
        
    def mousePressEvent(self, event):
        result = super(CustomTreeWidget, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.close()
        return result
    
    def keyPressEvent(self, event):
        result = super(CustomTreeWidget, self).keyPressEvent(event)
        if event.key() in(Qt.Key_Escape, Qt.Key_Return, Qt.Key_Enter):
            self.close()
        return result
    
    def close(self):
        result = super(CustomTreeWidget, self).close()
        self.closed.emit()
        return result
        

class FlatTreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        self._items = {}
        super(FlatTreeModel, self).__init__(parent)
        self.pathSeparator = u' > '
        
    def data(self, index, role=Qt.DisplayRole):
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
        nextIndex = len(self._items)
        treeWidgetItem.flatIndex = nextIndex
        self._items[nextIndex] = {}
        name = self.buildDisplayedName(treeWidgetItem)
        self._items[nextIndex][0] = QVariant(QString.fromUtf8(name))
        self._items[nextIndex][1] = QVariant(treeWidgetItem.text(1))
    
    
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
        self.itemView = CustomTreeWidget()
        self.itemView.setColumnCount(1)
        self.itemView.setHeaderHidden(True)
        self.itemView.setWindowFlags(Qt.Popup)
        #self.setModel(self.itemView.model())
        self.flatModel = FlatTreeModel(self)
        self.setModel(self.flatModel)
        #self.setView(self.itemView)
        self.itemView.expandAll()
        self._flatItemTree = {}
        self.initialExpand = True
        self.__nextCurrentIndex = None
        self.__currentText = ''
        self.itemView.currentItemChanged.connect(self.onCurrentItemChanged)
        self.itemView.itemActivated.connect(self.onItemActivated)
        self.itemView.closed.connect(self.hidePopup)
        #self.setItemDelegate(TreePopupDelegate(self))
#        print self.itemDelegate()
    
    def onCurrentItemChanged(self, cur, prev):
        self.setCurrentIndex(cur.flatIndex)
        #print "onCurrentItemChanged %s %s" % (cur.text(0), cur.flatIndex)
    
    def onItemActivated(self, item, col):
        print "onItemActivated %s %s" % (item.text(0), item.flatIndex)
    
    def value(self):
        return self.itemData(self.currentIndex(), Qt.UserRole)
    
    @pyqtSlot()
    def _setCurrentIndex(self):
        if self.__nextCurrentIndex is not None:
            self.setCurrentIndex(self.__nextCurrentIndex)
            #self.setEditText(QString.fromUtf8(self.__currentText))
        self.__nextCurrentIndex = None
    
    def setValue(self, value):
        for i in range(self.count()):
            if variant_to_pyobject(self.itemData(i)) == value:
                self.setCurrentIndex(i)
    
    def addItemFlat(self, depth, texts):
        
        self._flatItemTree[depth] = QTreeWidgetItem(texts)
        
        if depth == 0:
            self.itemView.addTopLevelItem(self._flatItemTree[depth])
            self.flatModel.append(self._flatItemTree[depth])
        else:
            newItem = QTreeWidgetItem(texts)
            self._flatItemTree[depth-1].addChild(newItem)
            self._flatItemTree[depth] = newItem
            self.flatModel.append(newItem)
            
    def keyPressEvent(self, event):
        return super(TreeComboBox, self).keyPressEvent(event)
#        if event.key() in (Qt.Key_Up, Qt.Key_Down):
#            return
#            item = self.itemView.currentItem()
#            if item is None:
#                item = self.itemView.topLevelItem(0)
#            if event.key() == Qt.Key_Up:
#                targetItem = self.itemView.itemAbove(item)
#                if targetItem is None:
#                    return
#                print "Key up pressed currentItem: %s" % targetItem.data(1,Qt.DisplayRole).toString()
#                self.itemView.setCurrentItem(targetItem)
#                return
#            if event.key() == Qt.Key_Down:
#                targetItem = self.itemView.itemBelow(item)
#                if targetItem is None:
#                    return
#                print "Key down pressed currentItem: %s" % targetItem.data(1,Qt.DisplayRole).toString()
#                self.itemView.setCurrentItem(targetItem)
#                return
                
                #self.setEditText(targetItem.data(0,Qt.DisplayRole).toString())
        
        if event.key() == Qt.Key_Space:
            self.showPopup()
            return
        
        return super(TreeComboBox, self).keyPressEvent(event)
    
    def showPopup(self):
        self.itemView.expandAll()
        self.itemView.move(self.parent().mapToGlobal(self.pos()))
        self.itemView.setMinimumWidth(self.width())
        self.itemView.setMaximumWidth(self.width())
        self.itemView.show()

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