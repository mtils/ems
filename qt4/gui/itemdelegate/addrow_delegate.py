'''
Created on 24.05.2012

@author: michi
'''

from PyQt4.QtCore import QSize, Qt
from PyQt4.QtGui import QStyledItemDelegate, QApplication, QStyle, \
    QStyleOptionButton, QIcon
from ems.qt4.util import variant_to_pyobject

class AddRowDelegate(QStyledItemDelegate):
    
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        
    def paint(self, painter, option, index):
        options = QStyleOptionButton()
        options.rect = option.rect
        options.state = QStyle.State_Enabled
        pixmap = variant_to_pyobject(index.data(Qt.DecorationRole))
        options.icon = QIcon(pixmap)
        
        QApplication.style().drawControl(QStyle.CE_PushButton, options, painter)
    
    def sizeHint_(self, option, index):
#        options = QStyleOptionViewItemV4(option)
#        self.initStyleOption(options, index)
        return QSize(50, 50)