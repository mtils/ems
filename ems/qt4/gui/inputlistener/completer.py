'''
Created on 28.04.2012

@author: michi
'''

from PyQt4.QtCore import Qt, QObject, QModelIndex, pyqtSignal
from PyQt4.QtGui import QCompleter, QAbstractProxyModel, QLineEdit, QComboBox

from ems.qt4.util import hassig

class CompleterListener(QObject):

    activated = pyqtSignal(QModelIndex)
    highlighted = pyqtSignal(QModelIndex)

    def __init__(self, completer=None):
        self._completer = None
        self.lastIndex = None
        QObject.__init__(self, completer)
        if completer is not None:
            self.setCompleter(completer)
    
    def completer(self):
        return self._completer
    
    def setCompleter(self, completer):
        if not isinstance(completer, QCompleter):
            raise ValueError("setCompleter needs a QCompleter")

        if isinstance(self._completer, QCompleter):
            if hassig(self._completer,'activatedIndex'):
                self._completer.activatedIndex.disconnect(self._onCompleterActivated)
            else:
                self._completer.activated[QModelIndex].disconnect(self._onCompleterActivated)
            if hassig(self._completer,'highlightedIndex'):
                self._completer.highlightedIndex.disconnect(self._onCompleterHighlighted)
            else:
                self._completer.highlighted[QModelIndex].disconnect(self._onCompleterHighlighted)

        self._completer = completer
        
        
        if hassig(self._completer,'activatedIndex'):
            self._completer.activatedIndex.connect(self._onCompleterActivated)
        else:
            self._completer.activated[QModelIndex].connect(self._onCompleterActivated)
        if hassig(self._completer,'highlightedIndex'):
            self._completer.highlightedIndex.connect(self._onCompleterHighlighted)
        else:
            self._completer.highlighted[QModelIndex].connect(self._onCompleterHighlighted)

        widget = self._completer.widget()
        if isinstance(widget, QLineEdit):
            widget.textEdited.connect(self._onTextChanged)
        if isinstance(widget, QComboBox):
            if widget.isEditable():
                widget.lineEdit().textEdited.connect(self._onTextChanged)
    
    def _onCompleterActivated(self, index):
        model = index.model()
        if isinstance(model, QAbstractProxyModel):
            srcIndex = model.mapToSource(index)
            self.activated.emit(srcIndex)
            self.lastIndex = srcIndex
        else:
            self.activated.emit(index)
            self.lastIndex = index
    
    def _onCompleterHighlighted(self, index):
        model = index.model()
        if isinstance(model, QAbstractProxyModel):
            srcIndex = model.mapToSource(index)
            self.activated.emit(srcIndex)
            self.lastIndex = srcIndex
        else:
            self.activated.emit(index)
            self.lastIndex = index
    
    def _onTextChanged(self, newText):
        self.lastIndex = None