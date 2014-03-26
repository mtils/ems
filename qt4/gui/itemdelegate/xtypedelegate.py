'''
Created on 04.03.2012

@author: michi
'''
#from datetime import 
from PyQt4.QtCore import Qt, QString, QSize
from PyQt4.QtGui import QStyledItemDelegate, QStyleOptionViewItemV4,\
    QApplication, QStyle
    
from ems.qt4.util import variant_to_pyobject

class XTypeDelegate(QStyledItemDelegate):
    def __init__(self, xType, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.xType = xType
        self._lastValue = ''
        self.textAlignment = Qt.AlignLeft | Qt.AlignVCenter

    def getString(self, value):
        if value is None:
            return ""
        return self.xType.value2String(value)

    def configureEditor(self, widget, xType):
        widget.setAlignment(self.textAlignment)

    def paint(self, painter, option, index):
        value = variant_to_pyobject(index.data())
        self._lastValue = value
 
        options = QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)
        options.displayAlignment = self.textAlignment
        
        style = QApplication.style() if options.widget is None \
            else options.widget.style()
        
        try:
            string = self.getString(value)
        except TypeError:
            string = ''
        options.text = QString.fromUtf8(string)
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)
        return None
        
        
        return super(XTypeDelegate, self).paint(painter, option, index)
    
    def sizeHint(self, option, index):
        value = variant_to_pyobject(index.data())
        if isinstance(value,(int,float)):
            options = QStyleOptionViewItemV4(option)
            self.initStyleOption(options, index)
            options.displayAlignment = Qt.AlignRight | Qt.AlignVCenter
            options.text = QString.fromUtf8(self.getString(value))
            width = options.fontMetrics.width(options.text) + 6
            return QSize(width, options.rect.height())
        return QStyledItemDelegate.sizeHint(self, option, index)