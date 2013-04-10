'''
Created on 17.05.2011

@author: michi
'''

from __future__ import division
import platform
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ems.qt4.gui.widgets.graphical import ColorButton #@UnresolvedImport
from ems.qt4.gui.itemdelegate.iconview import IconViewDelegate #@UnresolvedImport

class IconNavi(QListView):
    def __init__(self, parent=None):
        QListView.__init__(self, parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewMode(QListView.IconMode)
        #self.setResizeMode(QListView.Adjust)
    def resizeEvent(self, event):
        #print event.size()
        QListView.resizeEvent(self, event)
        newSize = QSize(event.size().height(),event.size().height())
        #print newSize
        self.setGridSize(newSize)
        self.setIconSize(QSize(newSize.width(),newSize.height()-30))
        #print "viewport",self.viewport().size()

class IconNaviTest(QDialog):
    def __init__(self, parent=None):
        super(IconNaviTest, self).__init__(parent)
        self.setupUi()
        
    def setupUi(self):
        self.mainLayout = QVBoxLayout(self)
        self.setWindowTitle("Icon View Navis")
        self.resize(QSize(150,200))
        self.iconView = IconNavi(self)
        self.mainLayout.addWidget(self.iconView)
        self.model = QStandardItemModel(self)
        
        self.delegate = IconViewDelegate(self)
        self.iconView.setItemDelegate(self.delegate)
        
        item1 = QStandardItem('One One')
        item1.setData(QVariant(QIcon('/home/michi/System/Desktop/Icons/Coding/python-clear.png')), Qt.DecorationRole)
        self.model.setItem(0,0,item1)
        
        item2 = QStandardItem('One Two')
        item2.setData(QVariant(QIcon('/home/michi/System/Desktop/Icons/Coding/kdevelop-sg.png')), Qt.DecorationRole)
        self.model.setItem(1,0,item2)
        
        item3 = QStandardItem('One Three')
        item3.setData(QVariant(QIcon('/home/michi/System/Desktop/Icons/Coding/eclipse.png')), Qt.DecorationRole)
        self.model.setItem(2,0,item3)

        self.iconView.setIconSize(QSize(96,96))
        self.iconView.setModel(self.model)
        
        #self.iconView.setFlow(self.iconView.LeftToRight)
        self.iconView.setFlow(self.iconView.TopToBottom)
        
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    
    form = IconNaviTest()
    #form = RulerTest()

    
    form.show()
    app.exec_()