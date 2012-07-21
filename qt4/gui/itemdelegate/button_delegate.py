'''
Created on 24.05.2012

@author: michi
'''

from PyQt4.QtCore import QSize, Qt
from PyQt4.QtGui import QStyledItemDelegate, QApplication, QStyle, \
    QStyleOptionButton, QIcon
from ems.qt4.util import variant_to_pyobject

class ButtonDelegate(QStyledItemDelegate):
    
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.icon = None
        self.showText = False
        self.iconSize = QSize(64, 64)
        
    def paint(self, painter, option, index):
        options = QStyleOptionButton()
        options.rect = option.rect
        options.state = QStyle.State_Enabled
        if self.icon:
            options.icon = self.icon
            options.features = QStyleOptionButton.DefaultButton
            
        if self.showText:
            options.text = variant_to_pyobject(index.data())
            
            
        QApplication.style().drawControl(QStyle.CE_PushButtonBevel, options, painter)
        QApplication.style().drawItemPixmap(painter, options.rect,
                                            Qt.AlignCenter | Qt.AlignVCenter,
                                            options.icon.pixmap(self.iconSize.width(),
                                                                self.iconSize.height()))
        
        
#        QApplication.style().drawControl(QStyle.CE_ItemViewItem, options, painter)
    
    def sizeHint(self, option, index):
#        options = QStyleOptionViewItemV4(option)
#        self.initStyleOption(options, index)
        return QSize(50, 50)