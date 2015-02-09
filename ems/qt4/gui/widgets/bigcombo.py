'''
Created on 28.06.2011

@author: michi
'''

from PyQt4.QtCore import QVariant, Qt, QStringList, SIGNAL, SLOT, QAbstractItemModel, QModelIndex, QAbstractListModel, QPoint, pyqtSignal
from PyQt4.QtGui import QComboBox, QTreeWidget, QTreeWidgetItem, QCompleter,\
QStringListModel, QListView

from ems.qt4.gui.itemdelegate.htmldelegate import HtmlDelegate #@UnresolvedImport
from ems.qt4.itemmodel.sa.representative_model import RepresentativeModel
class TestModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(TestModel, self).__init__(parent)
        self._rowCount = 100
        self.stringList = []
        self._currentList = []
        
        for i in range(self._rowCount):
            self.stringList.append("a%s" % (i+64000))
            self._currentList.append("a%s" % (i+64000))
            
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()
        if role in (Qt.DisplayRole, Qt.EditRole):
            #print index.row()
            value = self._currentList[index.row()]
            if isinstance(value, basestring):
                return QVariant(value)
            return QVariant(value)
        
        return QVariant()
    
    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column)
    
    def parent(self, index):
        return QModelIndex()
    
    def rowCount(self, index=QModelIndex()):
        return len(self._currentList)
    
    def columnCount(self, index=QModelIndex()):
        return 1
    
    def match(self, start, role, value, hits=1, matchFlags=Qt.MatchStartsWith|Qt.MatchWrap):
        criteria = unicode(value.toString())
        self.beginResetModel()
        self._currentList = []
        indexHits = []
        i=0
        for s in self.stringList:
            if s.startswith(criteria):
                #print "Matches: %s" % s
                self._currentList.append(s)
                indexHits.append(self.index(i,0))
                i += 1
            else:
                pass
                #print "Not matches: %s" % s
        #self.reset()
        self.endResetModel()
        return indexHits
    
class PopupListView(QListView):
    
    currentIndexChanged = pyqtSignal(QModelIndex)
    
    def __init__(self, parent=None):
        super(PopupListView, self).__init__(parent)
        self.setFrameStyle(self.Plain)
        self.setItemDelegate(HtmlDelegate(self))
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            super(PopupListView, self).keyPressEvent(event)
            self.hide()
            return
        if event.key() in (Qt.Key_Up, Qt.Key_Down):
            result = super(PopupListView, self).keyPressEvent(event)
            self.currentIndexChanged.emit(self.currentIndex())
            return result
        
        if event.key() == Qt.Key_Escape:
            self.hide()
            return
        self.parent().keyPressEvent(event, True)
    
    def mousePressEvent(self, event):
        result = super(PopupListView, self).mousePressEvent(event)
        self.currentIndexChanged.emit(self.currentIndex())
        self.hide()
        return result
    
#    def reset(self):
#        print "PopupListView.reset() called"
#        print "self.model().rowCount() = %s" % self.model().rowCount()
#        #super(PopupListView, self).reset()
    
    

class BigComboBox(QComboBox):
    def __init__(self, model, parent=None):
        super(BigComboBox, self).__init__(parent)
        self.setEditable(True)
        
        self.itemView = PopupListView(self)
        self.itemView.setWindowFlags(self.itemView.windowFlags() | Qt.Popup)
        if isinstance(model, RepresentativeModel):
            model.returnHtml = True
        self.itemView.setModel(model)
        self.connect(self, SIGNAL("editTextChanged(QString)"),
                     self.onEditTextChanged)
        
        self.connect(self.itemView,
                     SIGNAL("currentIndexChanged(QModelIndex)"),
                     self.onCurrentIndexChanged)
        #print self.completer().setCompletionMode(self.completer().InlineCompletion)
    
    def keyPressEvent(self, event, fromListView=False):
        result = super(BigComboBox, self).keyPressEvent(event)
        #if fromListView:
        index = self.itemView.model().index(0,0)
        if event.key() not in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab):
            matchResult = self.itemView.model().match(index, Qt.DisplayRole, QVariant(self.currentText()))
#        print "keyPressEvent %s" % matchResult
        return result
            
    def onEditTextChanged(self, index):
        #print "onEditTextChanged itemText: %s" % (self.itemText(self.currentIndex()))
        if self.itemView.isHidden():
            self.showPopup()
        
    
    def showPopup(self):
        self.itemView.resize(self.width(), 200)
        self.itemView.move(self.mapToGlobal(QPoint(0,self.height())))
        self.itemView.show()
    
    def hidePopup(self):
        self.itemView.hide()
        super(BigComboBox, self).hidePopup()
    
    def onCurrentIndexChanged(self, index):
        text = self.itemView.model().data(index, Qt.EditRole).toString()
        self.setEditText(text)
    
    def value(self):
        index = self.itemView.currentIndex()
        return self.itemView.model().data(index, Qt.UserRole)
    
    

if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import QApplication, QDialog, QHBoxLayout
    
    app = QApplication(sys.argv)
    dlg = QDialog()
    dlg.setLayout(QHBoxLayout(dlg))
    dlg.setMinimumWidth(300)
    dlg.combo = BigComboBox(TestModel(), dlg)
    dlg.layout().addWidget(dlg.combo)
    
    dlg.exec_()
    
    
    
    sys.exit(app.exec_())