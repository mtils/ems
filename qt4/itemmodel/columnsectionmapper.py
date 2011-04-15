'''
Created on 24.03.2011

@author: michi
'''
from PyQt4.QtGui import QItemDelegate

from sqlalchemy import Table
from sqlalchemy.sql import Alias,Select

from ems import qt4

class ColumnSectionMapper(object):
    def __init__(self,alchemySelect=None, parent=None):
        self.__columnConfigs = []
        self.__columnConfigIdByName = {}
        self.__alchemySelect = alchemySelect
        self.__delegate = MapperDelegate(self,parent)
        pass
    
    def addColumn(self,columnName,translatedName=None, delegate=None):
        if self.__columnConfigIdByName.has_key(columnName):
            raise KeyError("Column %s already assigned" % columnName)
        index = len(self.__columnConfigs)
        self.__columnConfigs.append({'name':columnName,
                                     'translatedName':translatedName,
                                     'delegate':delegate})
        self.__columnConfigIdByName[columnName] = index
        
    @property
    def translatedColumnNames(self):
        names = {}
        for config in self.__columnConfigs:
            names[config['name']] = config['translatedName']
        
        return names
    
    def __extractTablesFormSelect(self,alchemySelect):
        tableDict = {}
        for fromCond in alchemySelect.locate_all_froms():
            if isinstance(fromCond, Table):
                tableDict[str(fromCond.name)] = fromCond
            elif isinstance(fromCond,Alias):
                if isinstance(fromCond.original,Table):
                    tableDict[str(fromCond.name)] = fromCond
        return tableDict
    
    def getDelegate(self):
        return self.__delegate
        
    def getColConfig(self, column):
        if isinstance(column, int):
            index = column
        else:
            index = self.__columnConfigIdByName[unicode(column)]
        return self.__columnConfigs[index]
    
    def getSelectColumns(self, alchemySelect=None):
        if alchemySelect is None:
            alchemySelect = self.__alchemySelect
        if not isinstance(alchemySelect, Select):
            raise TypeError("alchemySelect has to be instanceof sqlalchemy.select")
        tableDict = self.__extractTablesFormSelect(alchemySelect)
        columnList = []
        for config in self.__columnConfigs:
            tableName,colName = config['name'].split('.')
            if tableDict.has_key(tableName):
                columnList.append(tableDict[tableName].c[colName])
        return columnList

class MapperDelegate(QItemDelegate):

    def __init__(self, mapper, parent=None):
        super(MapperDelegate, self).__init__(parent)
        self.__mapper = mapper
        
    
    def getDelegate(self, index):
        colName = index.data(qt4.ColumnNameRole).toString()
        delegate = self.__mapper.getColConfig(colName)['delegate']
        return delegate
    
    
    def paint(self, painter, option, index):
        delegate = self.getDelegate(index)
        if delegate is not None:
            delegate.paint(painter, option, index)
        else:
            QItemDelegate.paint(self, painter, option, index)


    def createEditor(self, parent, option, index):
        delegate = self.getDelegate(index)
        if delegate is not None:
            return delegate.createEditor(parent, option, index)
        else:
            return QItemDelegate.createEditor(self, parent, option,
                                              index)


    def setEditorData(self, editor, index):
        delegate = self.getDelegate(index)
        if delegate is not None:
            delegate.setEditorData(editor, index)
        else:
            QItemDelegate.setEditorData(self, editor, index)


    def setModelData(self, editor, model, index):
        delegate = self.getDelegate(index)
        if delegate is not None:
            delegate.setModelData(editor, model, index)
        else:
            QItemDelegate.setModelData(self, editor, model, index)
