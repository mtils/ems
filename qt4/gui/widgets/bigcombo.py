'''
Created on 28.06.2011

@author: michi
'''

from PyQt4.QtCore import QVariant, Qt, QStringList
from PyQt4.QtGui import QComboBox, QTreeWidget, QTreeWidgetItem, QCompleter,\
QStringListModel

class BigComboBox(QComboBox):
    def __init__(self, parent=None):
        super(BigComboBox, self).__init__(parent)
        self.setEditable(True)
        l = QStringList()
        for s in ['Oma','Opa','Papa']:
            l.append(s)
        #self.sModel = QStringListModel(l, self)
        completer = QCompleter(l)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompleter(completer)

if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import QApplication, QDialog, QHBoxLayout
    
    app = QApplication(sys.argv)
    dlg = QDialog()
    dlg.setLayout(QHBoxLayout(dlg))
    dlg.setMinimumWidth(300)
    dlg.combo = BigComboBox(dlg)
    dlg.layout().addWidget(dlg.combo)
    
    dlg.exec_()
    
    
    
    app.exec_()