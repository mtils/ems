#coding=utf8
'''
Created on 27.03.2011

@author: michi
'''
from PyQt4.QtGui import QWidget,QDialog, QListWidget, QListView, \
    QStackedWidget, QHBoxLayout, QListWidgetItem, QVBoxLayout, QSizePolicy,\
    QIcon,QDialogButtonBox, QFontMetricsF
from PyQt4.QtCore import QSize, Qt, pyqtSlot, SIGNAL, SLOT, pyqtSignal

class ListFormContainer(QWidget):
    aboutToClose = pyqtSignal()
    def __init__(self, parent=None, **kwargs):
        super(ListFormContainer, self).__init__(parent)
        self._iconSize = None
        self._processKwArgs(kwargs)
        self._kwargs = kwargs
        #init icon view on right
        self.contentsWidget = QListWidget()
        self.contentsWidget.setViewMode(QListView.IconMode)
        self.setIconSize(QSize(64,64))
        self.contentsWidget.setMovement(QListView.Static)
        self.contentsWidget.setFlow(QListView.TopToBottom)
        self.contentsWidget.setUniformItemSizes(True)
        self.contentsWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.contentsWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.contentsWidget.setWrapping(False)
        self.contentsWidget.setSpacing(0)

        #pagesWidget
        self.pagesWidget = QStackedWidget()

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.contentsWidget)
        mainLayout.addWidget(self.pagesWidget,1)
        mainLayout.setStretch(0,1)
        self.setLayout(mainLayout)
        
        self.contentsWidget.currentItemChanged.connect(self.changePage)
    
    def setIconSize(self, size):
        if self._iconSize != size:
            self._iconSize = size
            self.contentsWidget.setFixedWidth(2 * self._iconSize.width())
            self.contentsWidget.setIconSize(self._iconSize)
            self.contentsWidget.setGridSize(QSize(self.contentsWidget.width(),
                                                  self._iconSize.width()+20))
    
    def _processKwArgs(self, args):
        if args.has_key('windowTitle'):
            self.setWindowTitle(args['windowTitle'])
        if args.has_key('windowIcon'):
            self.setWindowIcon(args['windowIcon'])
        if args.has_key('iconSize'):
            self._iconSize = args['iconSize']
    
    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def changePage(self, current, previous):
        if not current:
            current = previous
        self.pagesWidget.setCurrentIndex(self.contentsWidget.row(current))
    
    def addPage(self, pageWidget, item=None):
        self.pagesWidget.addWidget(pageWidget)
        if item is None:
            item = QListWidgetItem(self.contentsWidget)
            item.setIcon(pageWidget.windowIcon())
            item.setText(pageWidget.windowTitle())
        elif isinstance(item, QIcon):
            icon = item
            item = QListWidgetItem(self.contentsWidget)
            item.setText(pageWidget.windowTitle())
            item.setIcon(icon)

        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.contentsWidget.addItem(item)
        itemWidth = self.contentsWidget.contentsRect().width()
        fm = QFontMetricsF(item.font())
        itemHeight = fm.boundingRect("9").height() + 4
        item.setSizeHint(QSize(itemWidth,self._iconSize.height() + itemHeight))

    @pyqtSlot()
    def accept(self):
        for idx in range(self.pagesWidget.count()):
            page = self.pagesWidget.widget(idx)
            if hasattr(page, 'accept') and callable(page.accept):
                page.accept()
        self.aboutToClose.emit()
        self.close()
    
    @pyqtSlot()
    def reject(self):
        for idx in range(self.pagesWidget.count()):
            page = self.pagesWidget.widget(idx)
            if hasattr(page, 'reject') and callable(page.reject):
                page.reject()
        self.aboutToClose.emit()
        self.close()
    
    def showEvent(self, event):
        currentRow = 0
        if self._kwargs.has_key('callPage'):
            currentRow = self._kwargs['callPage']
        self.contentsWidget.setCurrentRow(currentRow)
        super(ListFormContainer, self).showEvent(event)
    
    @staticmethod
    def toDialog(parent=None, invokeClass=None, acceptText=u"OK", 
                 rejectText=u"Abbrechen", **kwargs):
        
        dialog = QDialog(parent)
        if invokeClass is None:
            widget = ListFormContainer(dialog,**kwargs)
        else:
            widget = invokeClass(dialog,**kwargs)
        dialog.setWindowTitle(widget.windowTitle())
        dialog.setWindowIcon(widget.windowIcon())
        dialogLayout = QVBoxLayout()
        dialogLayout.addWidget(widget)
        dialog.setLayout(dialogLayout)
        widget.dialog = dialog
        dialog.container = widget
        dialog.buttonBox = QDialogButtonBox(dialog)
        dialog.buttonBox.setOrientation(Qt.Horizontal)
        dialog.buttonBox.addButton(dialog.trUtf8(acceptText),
                                   QDialogButtonBox.AcceptRole)
        dialog.buttonBox.addButton(dialog.trUtf8(rejectText),
                                   QDialogButtonBox.RejectRole)
        dialog.buttonBox.connect(dialog.buttonBox,
                                     SIGNAL("accepted()"),
                                     widget,
                                     SLOT("accept()"))
        dialog.buttonBox.connect(dialog.buttonBox,
                                     SIGNAL("rejected()"),
                                     widget,
                                     SLOT("reject()"))
        dialog.connect(widget, SIGNAL("aboutToClose()"),SLOT('close()'))
        dialogLayout.addWidget(dialog.buttonBox)
        return dialog