'''
Created on 10.01.2011

@author: michi
'''
from PyQt4.QtGui import QStyledItemDelegate
from PyQt4.QtCore import Qt

from ems import qt4

class GenericDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super(GenericDelegate, self).__init__(parent)
        self.delegates = {}
        self.rowDelegates = {}
        self.indexDelegates = {}

    def _getDelegate(self, index):
        indexId = "{0}|{1}".format(index.row(), index.column())
        try:
            return self.indexDelegates[indexId]
        except KeyError:
            return self.delegates[index.column()]

        raise KeyError()

    def sizeHint(self, option, index):
        try:
            return self._getDelegate(index).sizeHint(option, index)
        except KeyError:
            return QStyledItemDelegate.sizeHint(self, option, index)

    def insertColumnDelegate(self, column, delegate):
        delegate.setParent(self)
        self.delegates[column] = delegate

    def removeColumnDelegate(self, column):
        if column in self.delegates:
            del self.delegates[column]

    def insertIndexDelegate(self, index, delegate):
        indexId = "{0}|{1}".format(index.row(), index.column())
        self.indexDelegates[indexId] = delegate
        delegate.setParent(self)

    def removeIndexDelegate(self, index):
        del self.indexDelegates["{0}|{1}".format(index.row(), index.column())]

    def paint(self, painter, option, index):
        try:
            return self._getDelegate(index).paint(painter, option, index)
        except KeyError:
            return QStyledItemDelegate.paint(self, painter, option, index)

    def updateEditorGeometry(self, editor, option, index):
        try:
            return self._getDelegate(index).updateEditorGeometry(editor, option, index)
        except KeyError:
            return QStyledItemDelegate.updateEditorGeometry(self, editor, option, index)

    def createEditor(self, parent, option, index):
        try:
            return self._getDelegate(index).createEditor(parent, option, index)
        except KeyError:
            return QStyledItemDelegate.createEditor(self, parent, option,
                                              index)


    def setEditorData(self, editor, index):
        if not index.isValid():
            return
        try:
            return self._getDelegate(index).setEditorData(editor, index)
        except KeyError:
            return QStyledItemDelegate.setEditorData(self, editor, index)


    def setModelData(self, editor, model, index):
        if not index.isValid():
            return
        try:
            return self._getDelegate(index).setModelData(editor, model, index)
        except KeyError:
            return QStyledItemDelegate.setModelData(self, editor, model, index)
