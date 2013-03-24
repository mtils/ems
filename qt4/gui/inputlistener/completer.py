'''
Created on 28.04.2012

@author: michi
'''

from PyQt4.QtCore import Qt, QObject, QModelIndex, pyqtSignal
from PyQt4.QtGui import QCompleter, QAbstractProxyModel, QLineEdit, QComboBox


class CompleterListener(QObject):
    
    activated = pyqtSignal(QModelIndex)
    
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
            self._completer.activated[QModelIndex].disconnect(self._setCompleterIndex)
        self._completer = completer
        self._completer.activated[QModelIndex].connect(self._setCompleterIndex)
        widget = self._completer.widget()
        if isinstance(widget, QLineEdit):
            widget.textEdited.connect(self._onTextChanged)
        if isinstance(widget, QComboBox):
            if widget.isEditable():
                widget.lineEdit().textEdited.connect(self._onTextChanged)
    
    def _setCompleterIndex(self, index):
        model = index.model()
        if isinstance(model, QAbstractProxyModel):
            srcIndex = model.mapToSource(index)
            self.activated.emit(srcIndex)
            self.lastIndex = srcIndex
    
    def _onTextChanged(self, newText):
        self.lastIndex = None