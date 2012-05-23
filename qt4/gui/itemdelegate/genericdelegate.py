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
    
    def _getDelegate(self, index):
        return self.delegates.get(index.column())
    
    def sizeHint(self, option, index):
        delegate = self._getDelegate(index)
        
        if delegate is not None:
            return delegate.sizeHint(option, index)
        else:
            return QStyledItemDelegate.sizeHint(self, option, index)
    
    def insertColumnDelegate(self, column, delegate):
        delegate.setParent(self)
        self.delegates[column] = delegate

    def removeColumnDelegate(self, column):
        if column in self.delegates:
            del self.delegates[column]

    def paint(self, painter, option, index):
        delegate = self._getDelegate(index)
        
        if delegate is not None:
            return delegate.paint(painter, option, index)
        else:
            return QStyledItemDelegate.paint(self, painter, option, index)


    def createEditor(self, parent, option, index):
        delegate = self._getDelegate(index)
        if delegate is not None:
            return delegate.createEditor(parent, option, index)
        else:
            return QStyledItemDelegate.createEditor(self, parent, option,
                                              index)


    def setEditorData(self, editor, index):
        if not index.isValid():
            return
        delegate = self._getDelegate(index)
        if delegate is not None:
            return delegate.setEditorData(editor, index)
        else:
            return QStyledItemDelegate.setEditorData(self, editor, index)


    def setModelData(self, editor, model, index):
        if not index.isValid():
            return
        delegate = self._getDelegate(index)
        if delegate is not None:
            return delegate.setModelData(editor, model, index)
        else:
            return QStyledItemDelegate.setModelData(self, editor, model, index)
