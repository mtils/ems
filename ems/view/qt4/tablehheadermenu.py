'''
Created on 10.01.2011

@author: michi
'''

from PyQt4.QtGui import QMenu, QAction
from PyQt4.QtCore import SIGNAL,QVariant

class TableHHeaderContextMenu(QMenu):
    def __init__(self, header, model,columnNamesTranslated = {}):
        super(TableHHeaderContextMenu, self).__init__(header)
        self.model = model
        self.ctxActions = []
        self.headerWidget = header
        self.columnNamesTranslated = columnNamesTranslated
        self.connect(header,
                     SIGNAL("customContextMenuRequested(QPoint)"),
                     self.displayMenu)
        self.inActionPopulation = False
        
    def displayMenu(self, point):
        
        self.addColumnDisplayActions()
        self.exec_(self.parent().mapToGlobal(point))
    
    def addColumnDisplayActions(self):
        index = 0
        self.inActionPopulation = True
        self.clear()
        self.ctxActions = []
        for possibleCol in self.model.queryBuilder.possibleColumns:
            colName = unicode(possibleCol)
            if self.columnNamesTranslated.has_key(colName):
                name = self.columnNamesTranslated[colName]
            else:
                name = colName
            action = QAction(name,self)
            action.setData(QVariant(index))
            action.setCheckable(True)
            
            self.connect(action, SIGNAL("toggled(bool)"),
                         self.on_actionX_toggled)
            for displayedCol in self.model.queryBuilder.currentColumnList:
                if unicode(possibleCol) == unicode(displayedCol):
                    action.setChecked(True)
                 
            self.addAction(action)
            self.ctxActions.append(action)
            index += 1
        self.inActionPopulation = False
    
    def on_actionX_toggled(self,state):
        if not self.inActionPopulation:
            columns = self.model.queryBuilder.possibleColumns
            enabledCols = []
            for action in self.ctxActions:
                if action.isChecked():
                    idx = action.data().toInt()[0]
                    enabledCols.append(columns[idx])
                    
            self.model.queryBuilder.setCurrentColumnList(enabledCols)