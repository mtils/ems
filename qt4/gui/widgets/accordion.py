'''
Created on 28.07.2012

@author: michi
'''
from PyQt4.QtCore import Qt, QRect, QSize
from PyQt4.QtGui import QFrame, QWidget, QScrollArea, QVBoxLayout, QSizePolicy

class AccordionView(QWidget):
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi()
        self._model = None
        self._filterModels = {}
    
    def setupUi(self):
        #Main Layout
        self.mainLayout = QVBoxLayout() 
        self.setLayout(self.mainLayout)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setMargin(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        
        #Main ScrollArea
        self.scrollArea = QScrollArea(self)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        
        self.viewsContainer = QWidget()
        self.viewsContainer.setGeometry(QRect(0, 0, 100, 528))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.viewsContainer.sizePolicy().hasHeightForWidth())
        self.viewsContainer.setSizePolicy(sizePolicy)
        self.viewsContainer.setMinimumSize(QSize(100, 0))
        self.viewsContainer.setMaximumSize(QSize(100, 16777215))
    
    def model(self):
        return self._model
    
    def setModel(self, model, displayColumn = 0):
        pass
    
    def addGroup(self, title, filterColumn, filterCriteria):
        pass
        
        
        
        
        
        
        