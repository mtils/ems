'''
Created on 24.07.2011

@author: michi
'''
import logging

from PyQt4.QtCore import SIGNAL, SLOT, pyqtSignal, pyqtSlot, QString, Qt
from PyQt4.QtGui import QWidget, QDialog, QDialogButtonBox, QVBoxLayout, \
    QAbstractButton, QHBoxLayout, QFormLayout, QGridLayout, QApplication

from ems.qt4.util import hassig

class DialogableWidget(QWidget):
    
    
    _isDialog = False
    acceptButton = None
    rejectButton = None
    _result = QDialog.Rejected
    _isDone = False
    
    accepted = pyqtSignal()
    rejected = pyqtSignal()
    windowTitleChanged = pyqtSignal(QString)
    
    @pyqtSlot(QString)
    def setAcceptButtonText(self, text):
        if isinstance(self.acceptButton, QAbstractButton):
            self.acceptButton.setText(text)
        else:
            logging.getLogger(__name__).debug(type(self.acceptButton))
    
    @pyqtSlot(QString)
    def setRejectButtonText(self, text):
        if isinstance(self.rejectButton, QAbstractButton):
            self.rejectButton.setText(text)
            
    def exec_(self):
        raise NotImplementedError("Don't know how to implement exec_")
        self.setWindowModality(Qt.WindowModal)
        self.show()
        while QApplication.instance().processEvents():
            pass
        return self._result
    
    def _dialogInitFinished(self):
        pass
        
    
    @pyqtSlot()
    def accept(self):
        self.accepted.emit()
    
    @pyqtSlot()
    def reject(self):
        self.rejected.emit()
    
    @classmethod
    def toDialog(cls, *args, **kwargs):
        dlg = cls.__new__(cls, *args, **kwargs)
        dlg._isDialog = True
        dlg.__init__(*args, **kwargs)
        
        dlg.setWindowFlags(dlg.windowFlags() | Qt.Dialog)

        dlg.buttonBox = DialogableWidget._addButtonBox2Dialog(dlg)
        
        dlg.buttonBox.setStandardButtons(QDialogButtonBox.Apply |\
                                         QDialogButtonBox.Cancel)
        dlg.acceptButton = dlg.buttonBox.button(QDialogButtonBox.Apply)
        dlg.rejectButton = dlg.buttonBox.button(QDialogButtonBox.Cancel)
        
        if hassig(dlg,'validationChanged'):
            dlg.connect(dlg, SIGNAL('validationChanged(bool)'),
                        dlg.acceptButton, SLOT("setEnabled(bool)"))

        dlg.connect(dlg.acceptButton, SIGNAL('clicked()'),
                    dlg, SLOT('accept()'))
        
        dlg.connect(dlg.rejectButton, SIGNAL('clicked()'),
                    dlg, SLOT('reject()'))
        dlg._dialogInitFinished()

        return dlg
    
    def morphToDialog(self):

        self._isDialog = True
        self.setWindowFlags(self.windowFlags() | Qt.Dialog)
        self.buttonBox = DialogableWidget._addButtonBox2Dialog(self)
    
    def windowTitle(self):
        return QWidget.windowTitle(self)
    
    def setWindowTitle(self, title):
        if self.windowTitle() != title:
            QWidget.setWindowTitle(self, title)
            self.windowTitleChanged.emit(title)
    
    @staticmethod
    def _addButtonBox2Dialog(dlg):
        layout = dlg.layout()
        if layout is None:
            raise TypeError("The Widget needs a layout to assign the buttons")
        if isinstance(layout, QVBoxLayout):
            dlg.buttonBox = QDialogButtonBox(Qt.Horizontal)
            layout.addWidget(dlg.buttonBox)
            
        if isinstance(layout, QGridLayout):
            dlg.buttonBox = QDialogButtonBox(Qt.Horizontal)
            layout.addWidget(dlg.buttonBox, layout.rowCount(), 0,
                             1, layout.columnCount())
        
        if isinstance(layout, QFormLayout):
            dlg.buttonBox = QDialogButtonBox(Qt.Horizontal)
            layout.addRow(dlg.buttonBox)
        
        if isinstance(layout, QHBoxLayout):
            dlg.buttonBox = QDialogButtonBox(Qt.Vertical)
            layout.addWidget(dlg.buttonBox)
        
        return dlg.buttonBox
        
        #dlg.form = 

def to_dialog(widget):

    widget._isDialog = True

    widget.setWindowFlags(widget.windowFlags() | Qt.Dialog)

    widget.buttonBox = DialogableWidget._addButtonBox2Dialog(widget)

    widget.buttonBox.setStandardButtons(QDialogButtonBox.Apply |\
                                        QDialogButtonBox.Cancel)
    widget.acceptButton = widget.buttonBox.button(QDialogButtonBox.Apply)
    widget.rejectButton = widget.buttonBox.button(QDialogButtonBox.Cancel)

    if hassig(widget,'validationChanged'):
        widget.connect(widget, SIGNAL('validationChanged(bool)'),
                    widget.acceptButton, SLOT("setEnabled(bool)"))

    widget.connect(widget.acceptButton, SIGNAL('clicked()'),
                widget, SLOT('accept()'))
    
    widget.connect(widget.rejectButton, SIGNAL('clicked()'),
                widget, SLOT('reject()'))
    widget._dialogInitFinished()

    return widget