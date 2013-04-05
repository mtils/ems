#coding=utf-8
'''
Created on 24.03.2013

@author: michi
'''
from PyQt4.QtCore import QObject, QAbstractItemModel, QRegExp, QStringList
from PyQt4.QtGui import QCompleter, QSortFilterProxyModel

class FuzzyCompleter(QCompleter):

    StartsWith = 1
    Contains = 2
    Regex = 3

    def __init__(self, model=None, parent=None):
        '''void FuzzyCompleter.__init__(QAbstractItemModel model = None, QObject parent = None)'''
        if parent is None and isinstance(model, QObject) and not isinstance(model, QAbstractItemModel):
            QCompleter.__init__(self, model)
        else:
            QCompleter.__init__(self, parent)

        self.localCompletionPrefix = ''

        self._filtering = FuzzyCompleter.StartsWith
        self._sortFilterProxyModel = QSortFilterProxyModel(self)

        if isinstance(model, QAbstractItemModel):
            self.setModel(model)

    def filtering(self):
        '''int FuzzyCompleter.filtering()'''
        return self._filtering

    def setFiltering(self, filtering):
        '''FuzzyCompleter FuzzyCompleter.setFiltering(int filtering)'''
        if self._filtering == filtering:
            return self
        sourceModel = self.sourceModel()
        self._filtering = filtering
        self.setSourceModel(sourceModel)
        self.setCompletionPrefix(self.completionPrefix())
        return self

    def sourceModel(self):
        '''QAbstractItemModel FuzzyCompleter.sourceModel()'''
        if self._filtering != FuzzyCompleter.StartsWith:
            return self._sortFilterProxyModel.sourceModel()
        return QCompleter.model(self)

    def setSourceModel(self, sourceModel):
        '''FuzzyCompleter FuzzyCompleter.setSourceModel(QAbstractItemModel sourceModel)'''
        if self._filtering != FuzzyCompleter.StartsWith:
            self._sortFilterProxyModel.setSourceModel(sourceModel)
            if sourceModel.parent() is self:
                sourceModel.setParent(self._sortFilterProxyModel)
            self.setModel(self._sortFilterProxyModel)
        elif sourceModel.parent() is self._sortFilterProxyModel:
            sourceModel.setParent(self)
            self.setModel(sourceModel)
        return self

    def splitPath(self, path):
        '''QStringList FuzzyCompleter.splitPath(QString path)'''
        if self._filtering == FuzzyCompleter.StartsWith:
            paths = QCompleter.splitPath(self, path)
        elif self._filtering == FuzzyCompleter.Contains:
            self._updateSortFilterProxyModel();
            self._sortFilterProxyModel.setFilterWildcard(path)
            paths = QStringList();
        elif self._filtering == FuzzyCompleter.Regex:
            regex = QRegExp(QRegExp.escape(path))
            regex.setCaseSensitivity(self.caseSensitivity())
            self._sortFilterProxyModel.setFilterRegExp(regex)
            paths = QStringList()
        return paths
    
    def _updateSortFilterProxyModel(self):
        '''void FuzzyCompleter._updateSortFilterProxyModel()'''
        self._sortFilterProxyModel.setFilterCaseSensitivity(self.caseSensitivity())
        self._sortFilterProxyModel.setFilterKeyColumn(self.completionColumn())