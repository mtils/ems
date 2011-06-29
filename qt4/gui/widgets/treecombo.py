'''
Created on 27.06.2011

@author: michi
'''
from PyQt4.QtCore import QVariant, Qt
from PyQt4.QtGui import QComboBox, QTreeWidget, QTreeWidgetItem

class CustomTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super(CustomTreeWidget, self).__init__(parent)
        

class TreeComboBox(QComboBox):
    def __init__(self, parent=None):
        super(TreeComboBox, self).__init__(parent)
        self.itemView = CustomTreeWidget()
        self.itemView.setColumnCount(1)
        self.itemView.setHeaderHidden(True)
        self.setModel(self.itemView.model())
        self.setView(self.itemView)
        self._flatItemTree = {}
    
    def addItemFlat(self, depth, texts):
        self._flatItemTree[depth] = QTreeWidgetItem(texts)
        if depth == 0:
            self.itemView.addTopLevelItem(self._flatItemTree[depth])
        else:
            newItem = QTreeWidgetItem(texts)
            self._flatItemTree[depth-1].addChild(newItem)
            self._flatItemTree[depth] = newItem
            
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Up, Qt.Key_Down):
            return
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