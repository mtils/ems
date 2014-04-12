#coding=utf-8
'''
Created on 24.03.2013

@author: michi
'''
from PyQt4.QtCore import QObject, QAbstractItemModel, QRegExp, QStringList, \
    pyqtSignal, QModelIndex, Qt
from PyQt4.QtGui import QCompleter, QSortFilterProxyModel

from ems.qt4.util import variant_to_pyobject

class FuzzyCompleter(QCompleter):

    StartsWith = 1
    Contains = 2
    Regex = 3
    
    activatedIndex = pyqtSignal(QModelIndex)
    highlightedIndex = pyqtSignal(QModelIndex)
    
    activationRole = Qt.EditRole

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

        self.activated[QModelIndex].connect(self._onBaseCompleterActivated)
        self.highlighted[QModelIndex].connect(self._onBaseCompleterHighlighted)

    def _onBaseCompleterActivated(self, modelIndex):
        if self._filtering == self.StartsWith:
            self.activatedIndex.emit(modelIndex)
        realIndex = self._sortFilterProxyModel.mapToSource(self._sortFilterProxyModel.index(modelIndex.row(), modelIndex.column()))
        self.activatedIndex.emit(realIndex)

    def _onBaseCompleterHighlighted(self, modelIndex):
        if self._filtering == self.StartsWith:
            self.highlightedIndex.emit(modelIndex)
        realIndex = self._sortFilterProxyModel.mapToSource(self._sortFilterProxyModel.index(modelIndex.row(), modelIndex.column()))
        self.highlightedIndex.emit(realIndex)

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
            try:
                if sourceModel.parent() is self:
                    sourceModel.setParent(self._sortFilterProxyModel)
                self.setModel(self._sortFilterProxyModel)
            except TypeError:
                pass

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

    def pathFromIndex(self, index):
        return variant_to_pyobject(index.data(self.activationRole))
