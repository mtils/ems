'''
Created on 24.05.2012

@author: michi
'''

from PyQt4.QtCore import QSize, Qt
from PyQt4.QtGui import QStyledItemDelegate, QApplication, QStyle, \
    QStyleOptionButton, QIcon
from ems.qt4.util import variant_to_pyobject
from ems.qt4.itemmodel.addrow_proxymodel import AddRowProxyModel #@UnresolvedImport

class AddRowDelegate(QStyledItemDelegate):
    
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.addIcon = None
        self.removeIcon = None
        self.addText = None
        self.removeText = None
        
    def paint(self, painter, option, index):
        options = QStyleOptionButton()
        options.rect = option.rect
        options.state = QStyle.State_Enabled
        if self.addIcon and self.removeIcon:
            action = variant_to_pyobject(index.data(Qt.UserRole))
            if action == AddRowProxyModel.ADD:
                options.icon = self.addIcon
            if action == AddRowProxyModel.REMOVE:
                options.icon = self.removeIcon
            options.text = ""
            options.features = QStyleOptionButton.DefaultButton
        if self.addText is not None and self.removeText is not None:
            if action == AddRowProxyModel.ADD:
                options.text = self.addText
            if action == AddRowProxyModel.REMOVE:
                options.text = self.removeText 
        
        QApplication.style().drawControl(QStyle.CE_PushButtonBevel, options, painter)
        QApplication.style().drawItemPixmap(painter, options.rect,
                                            Qt.AlignCenter | Qt.AlignVCenter,
                                            options.icon.pixmap(48,48))
    
    def sizeHint_(self, option, index):
#        options = QStyleOptionViewItemV4(option)
#        self.initStyleOption(options, index)
        return QSize(50, 50)