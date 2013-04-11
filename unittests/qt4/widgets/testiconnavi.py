'''
Created on 17.05.2011

@author: michi
'''

from __future__ import division
import platform
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ems.qt4.util import variant_to_pyobject
from ems.qt4.gui.widgets.graphical import ColorButton #@UnresolvedImport
from ems.qt4.gui.itemdelegate.iconview import IconViewDelegate #@UnresolvedImport
import icons

class IconNavi(QListView):
    def __init__(self, parent=None):
        QListView.__init__(self, parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewMode(QListView.IconMode)
        self.setAutoScroll(False)
        #self.setItemDelegate(IconViewDelegate(self))
        self.setSpacing(0)
        self.setUniformItemSizes(True)
        
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))

    def resizeEvent_(self, event):
        #print event.size()
        QListView.resizeEvent(self, event)
        newSize = QSize(event.size().height(),event.size().height())
        #print newSize
        self.setGridSize(newSize)
        if self.itemDelegate().drawText:
            iconSize = QSize()
            self.setIconSize(QSize(newSize.width(),newSize.height()))
        #print self.itemDelegate().calculateTextSize()
        print self.sizeHintForColumn(0)
    
    def setModel(self, model):
        if isinstance(self.model(), QAbstractItemModel):
            self.model().rowsRemoved.disconnect(self._onModelChanges)
            self.model().rowsMoved.disconnect(self._onModelChanges)
            self.model().layoutChanged.disconnect(self._onModelChanges)
            self.model().rowsInserted.disconnect(self._onModelChanges)
            self.model().layoutChanged.disconnect(self._onModelChanges)
            self.model().modelReset.disconnect(self._onModelChanges)

        QListView.setModel(self, model)
        
        self.model().rowsRemoved.connect(self._onModelChanges)
        self.model().rowsMoved.connect(self._onModelChanges)
        self.model().layoutChanged.connect(self._onModelChanges)
        self.model().rowsInserted.connect(self._onModelChanges)
        self.model().layoutChanged.connect(self._onModelChanges)
        self.model().modelReset.connect(self._onModelChanges)

    def sizeHint(self):
        s = QSize()

        maxLength = 0
        maxLengthRow = 0
        for i in range(self.model().rowCount()):
            displayText = variant_to_pyobject(self.model().index(i,0).data(Qt.DisplayRole))
            if isinstance(displayText, basestring):
                length = len(displayText)
                if length > maxLength:
                    maxLength = length
                    maxLengthRow = i
        itemSizeHint = self.sizeHintForIndex(self.model().index(maxLengthRow,0))
        s.setHeight(itemSizeHint.height()+self.frameWidth()*2)
        s.setWidth(itemSizeHint.width()*self.model().rowCount()+self.frameWidth()*2)
        return s

    def scrollContentsBy(self, dx, dy):
        return
    
    def setIconSize(self, newSize):
        QListView.setIconSize(self, newSize)
        self.updateGeometryByContents()
    
    def _onModelChanges(self, unused1=None, unused2=None):
        self.updateGeometryByContents()

    def updateGeometryByContents(self):
        if self.isVisible():
            self.resize(self.sizeHint())
            self.updateGeometry()


class IconNaviTest(QDialog):
    
    availableIcons = (":/icons/accessories-calculator.png",
        ":/icons/akonadi.png",
        ":/icons/kdevelop.png",
        ":/icons/kplato.png",
        ":/icons/kwalletmanager.png",
        ":/icons/preferences-system-bluetooth.png",
        ":/icons/qelectrotech.png",
        ":/icons/quassel.png",
        ":/icons/google.png",
        ":/icons/google-chrome-icon-250px.png",
        ":/icons/tools-media-optical-copy.png",
        ":/icons/mysql2.png",
        ":/icons/python-clear.png",
        ":/icons/subversion_ai.png",
        ":/icons/eclipse.png"
    )
    def __init__(self, parent=None):
        super(IconNaviTest, self).__init__(parent)
        self.setupUi()
        
    def setupUi(self):
        self.mainLayout = QVBoxLayout(self)
        self.setWindowTitle("Icon View Navis")
        self.resize(QSize(800,200))
        self.iconView = IconNavi(self)
        self.mainLayout.addWidget(self.iconView)
        self.model = QStandardItemModel(self)

        self.addRow()
        self.addRow()
        self.addRow()

        self.iconView.setIconSize(QSize(48,48))
        self.iconView.setModel(self.model)
        
        #self.iconView.itemDelegate().drawText = False
        
        #self.iconView.setFlow(self.iconView.LeftToRight)
        self.iconView.setFlow(self.iconView.TopToBottom)
        
        
        self.inputsGroup = QGroupBox(self)
        #self.mainLayout.addWidget(self.inputsGroup)
        self.mainLayout.insertWidget(0, self.inputsGroup)
        
        self.inputsLayout = QFormLayout(self.inputsGroup)
        
        self.iconSizeInput = QSpinBox(self)
        self.iconSizeInput.setMinimum(16)
        self.iconSizeInput.setMaximum(256)
        self.iconSizeInput.setSingleStep(16)
        self.iconSizeInput.setValue(self.iconView.iconSize().width())
        self.inputsLayout.addRow(QLabel('IconSize'), self.iconSizeInput)
        self.iconSizeInput.valueChanged.connect(self.onIconSizeChanged)
        
        self.itemTextInput = QLineEdit(self)
        self.inputsLayout.addRow(QLabel('Label'),self.itemTextInput)
        self.addButton = QPushButton('Add Item',self)
        self.inputsLayout.addRow(QLabel(''), self.addButton)
        self.addButton.clicked.connect(self.onAddButtonClicked)
        
        self.removeButton = QPushButton('Remove Item',self)
        self.inputsLayout.addRow(QLabel(''), self.removeButton)
        self.removeButton.clicked.connect(self.onRemoveButtonClicked)
    
    def addRow(self, text=None):
        if len(self.availableIcons) <= self.model.rowCount():
            return
        nextIndex = self.model.rowCount()
        if not text:
            text = QString("Item #{0}".format(nextIndex))
        usedIcons = []
        for i in range(nextIndex):
            iconPath = variant_to_pyobject(self.model.index(i,0).data(Qt.UserRole))
            if iconPath:
                usedIcons.append(unicode(iconPath))
        newIconPath = ''
        for iconPath in self.availableIcons:
            if iconPath not in usedIcons:
                newIconPath = iconPath
                break
        if not newIconPath:
            return

        item = QStandardItem(text)
        item.setData(QVariant(QIcon(newIconPath)), Qt.DecorationRole)
        item.setData(QVariant(QString(newIconPath)), Qt.UserRole)
        self.model.setItem(nextIndex,0,item)

    def onIconSizeChanged(self, newSize):
        self.iconView.setIconSize(QSize(newSize, newSize))
    
    def onAddButtonClicked(self):
        if len(self.availableIcons) <= self.model.rowCount():
            return
        self.addRow(self.itemTextInput.text())
    
    def onRemoveButtonClicked(self):
        if self.model.rowCount() < 2:
            return
        self.model.removeRow(self.model.rowCount()-1)
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    
    form = IconNaviTest()
    #form = RulerTest()

    
    form.show()
    app.exec_()