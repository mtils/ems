'''
Created on 10.01.2011

@author: michi
'''
from PyQt4.QtGui import QItemDelegate
from PyQt4.QtCore import Qt

from ems import qt4

class GenericDelegate(QItemDelegate):

    def __init__(self, parent=None):
        super(GenericDelegate, self).__init__(parent)
        self.delegates = {}


    def insertColumnDelegate(self, column, delegate):
        delegate.setParent(self)
        self.delegates[column] = delegate


    def removeColumnDelegate(self, column):
        if column in self.delegates:
            del self.delegates[column]


    def paint(self, painter, option, index):
#        print "Ich zeischne"
        delegate = self.delegates.get(index.column())
        
        if delegate is not None:
            delegate.paint(painter, option, index)
        else:
            QItemDelegate.paint(self, painter, option, index)


    def createEditor(self, parent, option, index):
#        print "gDelegate.createEditor %s" % parent
        delegate = self.delegates.get(index.column())
        if delegate is not None:
            return delegate.createEditor(parent, option, index)
        else:
            return QItemDelegate.createEditor(self, parent, option,
                                              index)


    def setEditorData(self, editor, index):
#        print "gDelegate.setEditorData %s" % editor
        delegate = self.delegates.get(index.column())
        if delegate is not None:
            delegate.setEditorData(editor, index)
        else:
            QItemDelegate.setEditorData(self, editor, index)


    def setModelData(self, editor, model, index):
#        print "gDelegate.setModelData %s" % editor
        delegate = self.delegates.get(index.column())
        if delegate is not None:
            delegate.setModelData(editor, model, index)
        else:
            QItemDelegate.setModelData(self, editor, model, index)
