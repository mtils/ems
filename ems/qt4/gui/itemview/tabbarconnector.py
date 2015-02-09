'''
Created on 29.08.2012

@author: michi
'''
import logging

from PyQt4.QtCore import QObject, QAbstractItemModel, QAbstractListModel, \
    pyqtSignal, QVariant, Qt, QString
from PyQt4.QtGui import QTabBar, QIcon
from ems.qt4.util import variant_to_pyobject

class TabBarConnector(QObject):
    
    modelColumnChanged = pyqtSignal(int)
    currentTabDataChanged = pyqtSignal(QVariant)
    
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self._model = None
        self._tabBar = None
        self._modelColumn = 0
        self._tabDataColumn = None
    
    def modelColumn(self):
        return self._modelColumn
    
    def setModelColumn(self, column, initialConnect=True):
        if column == self._modelColumn:
            return
        if not isinstance(column, int):
            raise TypeError("modelColumn has to be instance of int")
        self._modelColumn = column
    
    def tabDataColumn(self):
        return self._tabDataColumn
    
    def setTabDataColumn(self, column):
        self._tabDataColumn = column
    
    def tabBar(self):
        return self._tabBar
    
    def setTabBar(self, tabBar, initialConnect=True):
        if self._tabBar is tabBar:
            return
        
        if not isinstance(tabBar, QTabBar):
            raise TypeError("tabBar has to be instance of QTabBar")
        self._tabBar = tabBar
        
    
    def model(self):
        return self._model
    
    def setModel(self, model, initialConnect=True):
        if self._model is model:
            return
        
        if not isinstance(model, QAbstractItemModel):
            raise TypeError("model has to be instance of QAbstractItemModel")
        self._model = model
        
        self._model.dataChanged.connect(self.onDataChanged)
        self._model.modelReset.connect(self.onModelReset)
        self._model.rowsInserted.connect(self.onRowsInserted)
        self._model.rowsMoved.connect(self.onRowsMoved)
        self._model.rowsRemoved.connect(self.onRowsRemoved)
    
    def connectModel2TabBar(self, model=None, tabBar=None):
        if model is None:
            if self._model is None:
                raise TypeError("No model assigned. Pass a model or set one by setModel()")
        else:
            self.setModel(model, False)
        
        if tabBar is None:
            if self._tabBar is None:
                raise TypeError("No tabbar assigned. Pass a QTabBar or set one by setTabBar()")
        else:
            self.setTabBar(tabBar, False)
        
        self.onModelReset()
        
        
    
    def onDataChanged(self, topLeft, bottomRight):
        for row in range(topLeft.row(), bottomRight.row()+1):
            for col in range(topLeft.column(), bottomRight.column()+1):
                if col == self._modelColumn:
                    self._updateTabText(row)
                    self._updateTabToolTip(row)
                if col == self._tabDataColumn:
                    self._updateTabData(row)
                if col == self._model.enabledFlagColumn():
                    self._updateTabEnabledState(row)
    
    def onModelReset(self):
        for i in range(self._tabBar.count()):
            self._tabBar.removeTab(i)
            
        for row in range(self._model.rowCount()):
            title = variant_to_pyobject(self._model.index(row,
                                                          self._modelColumn).
                                        data(Qt.DisplayRole))
            icon = variant_to_pyobject(self._model.index(row,
                                                          self._modelColumn).
                                        data(Qt.DecorationRole))
            if isinstance(icon, QIcon):
                self._tabBar.addTab(icon, QString.fromUtf8(title))
            else:
                self._tabBar.addTab(QString.fromUtf8(title))
            
            self._updateTabEnabledState(row)
            self._updateTabToolTip(row)
            self._updateTabData(row)
            
    def _updateTabEnabledState(self, row):
        flags = self._model.flags(self._model.index(row, self._modelColumn))
        self._tabBar.setTabEnabled(row, bool(int(flags) & int(Qt.ItemIsEnabled)))
    
    def _updateTabText(self, row):
        title = variant_to_pyobject(self._model.index(row,
                                                          self._modelColumn).
                                        data(Qt.DisplayRole))
        self._tabBar.setTabText(QString.fromUtf8(title))
    
    def _updateTabToolTip(self, row):
        toolTip = variant_to_pyobject(self._model.index(row, self._modelColumn)
                                      .data(Qt.ToolTipRole))
        if toolTip:
            self._tabBar.setTabToolTip(row, QString.fromUtf8(toolTip))
    
    def _updateTabData(self, row):
        if self._tabDataColumn is not None:
            tabData = self._model.index(row, self._tabDataColumn).data(Qt.DisplayRole)
            if tabData:
                self._tabBar.setTabData(row, tabData)
    
    def onRowsInserted(self, parent, start, end):
        pass
    
    def onRowsMoved(self, sourceParent, sourceStart, sourceEnd, destinationParent,
                  destinationRow):
        logging.getLogger(__name__).debug("onRowsMoved")
    
    def onRowsRemoved(self, parent, start, end):
        logging.getLogger(__name__).debug("onRowsRemoved")
        
        