#coding=utf-8
'''
Created on 10.01.2011

@author: michi
'''

from PyQt4.QtGui import QMenu, QAction
from PyQt4.QtCore import SIGNAL,QVariant

from ems.qt4.gui.widgets.listview.dragdroplists import DragDropLists #@UnresolvedImport

class TableHHeaderContextMenu(QMenu):
    
    maxInlineColumns = 5
    
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
        self._columnSelectionWidget = None
        
    def displayMenu(self, point):
        #print "Isch werde aufgerufen"
        self.clear()
        if len(self.model.possibleColumns) <= self.maxInlineColumns:
            self.addCheckableColumns()
        else:
            self.addColumnDisplayActions()
        self.exec_(self.parent().mapToGlobal(point))
    
    def addColumnDisplayActions(self):
        action = QAction(self.trUtf8(u"Spalten auswählen"), self)
        self.connect(action, SIGNAL("triggered(bool)"),
                     self.displayColumnSelection)
        self.addAction(action)
    
    def displayColumnSelection(self, triggered=True):
        #print "Isch bin dran"
        self._columnSelectionWidget = DragDropLists.toDialog(srcWidgetMode=DragDropLists.Tree,
                                   srcWidgetIsReadOnly=True,
                                   parent = self.parent().window())
        self._columnSelectionWidget.setWindowTitle(self.trUtf8(u"Spalten auswählen"))
        depth = 0
        for col in self.model.possibleColumns:
            depth = len(col.split('.')) - 1
            name = self.model.getPropertyFriendlyName(col)
            self._columnSelectionWidget.form.addSrcEntry(text=name,
                                                         userData=col,
                                                         depth=depth)
        
        for col in self.model.columns:
            name = self.model.getPropertyFriendlyName(col)
            self._columnSelectionWidget.form.addTrgEntry(name, col)
        self._columnSelectionWidget.form.srcInput.expandAll()
        
        applyButton = self._columnSelectionWidget.\
            buttonBox.button(self._columnSelectionWidget.buttonBox.Apply)
        self.connect(applyButton, SIGNAL("clicked()"), self.onColumnSelectionChanged)
        
        
        self._columnSelectionWidget.show()
    
    def onColumnSelectionChanged(self, button=None):
        choosedUserData = self._columnSelectionWidget.form.getChoosedUserData()
        columns = []
        for data in choosedUserData:
            columns.append(unicode(data.toString()))
        
        self.model.columns = columns
        
    def addCheckableColumns(self):
        index = 0
        self.inActionPopulation = True
        self.clear()
        self.ctxActions = []
        for possibleCol in self.model.possibleColumns:
            colName = unicode(possibleCol)
#            if self.columnNamesTranslated.has_key(colName):
#                name = self.columnNamesTranslated[colName]
#            else:
            name = colName
            action = QAction(name,self)
            action.setData(QVariant(index))
            action.setCheckable(True)
            
            self.connect(action, SIGNAL("toggled(bool)"),
                         self.on_actionX_toggled)
            for displayedCol in self.model.columns:
                if unicode(possibleCol) == unicode(displayedCol):
                    action.setChecked(True)
                 
            self.addAction(action)
            self.ctxActions.append(action)
            index += 1
        self.inActionPopulation = False
    
    def on_actionX_toggled(self,state):
        if not self.inActionPopulation:
            columns = self.model.possibleColumns
            enabledCols = []
            for action in self.ctxActions:
                if action.isChecked():
                    idx = action.data().toInt()[0]
                    enabledCols.append(columns[idx])
            #print columns
            self.model.columns = enabledCols