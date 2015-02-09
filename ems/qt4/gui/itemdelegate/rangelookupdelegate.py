'''
Created on 10.01.2011

@author: michi
'''
from PyQt4.QtGui import QStyledItemDelegate,QStyleOptionViewItemV4,\
    QApplication, QStyle, QComboBox
from PyQt4.QtCore import Qt, QString, QVariant

from ems import qt4
from ems.qt4.util import variant_to_pyobject

class RangeLookupDelegate(QStyledItemDelegate):

    START = 0
    END = 1
    LABEL = 2
    DEFAULT_VALUE = 3
    
    def __init__(self, fallbackString="", parent=None):
        super(RangeLookupDelegate, self).__init__(parent)
        self._ranges = []
        self.textAlignment = Qt.AlignCenter | Qt.AlignVCenter
        self.fallbackString = fallbackString
    
    def addRange(self, start, end, label, defaultValue=None):
        self._ranges.append({RangeLookupDelegate.START: start,
                             RangeLookupDelegate.END: end,
                             RangeLookupDelegate.LABEL: label,
                             RangeLookupDelegate.DEFAULT_VALUE: defaultValue})
    
    def sizeHint(self, option, index):
        return QStyledItemDelegate.sizeHint(self, option, index)
    
    def getStringOfValue(self, value):
        if isinstance(value, (int, float)):
            for range_ in self._ranges:
                if value >= range_[RangeLookupDelegate.START] and value <= range_[RangeLookupDelegate.END]:
                    return range_[RangeLookupDelegate.LABEL]
        return self.fallbackString
    
    def paint(self, painter, option, index):
        value = variant_to_pyobject(index.data())
        string = self.getStringOfValue(value)
            
        options = QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)
        options.displayAlignment = self.textAlignment
        
        style = QApplication.style() if options.widget is None \
            else options.widget.style()
        
        
        options.text = string
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)
        return None
        


    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        
        for range_ in self._ranges:
            if range_[RangeLookupDelegate.DEFAULT_VALUE] is not None:
                defaultValue = range_[RangeLookupDelegate.DEFAULT_VALUE]
            else:
                defaultValue = range_[RangeLookupDelegate.START] + (range_[RangeLookupDelegate.END] - range_[RangeLookupDelegate.START] / 2.0)
                 
            combo.addItem(range_[RangeLookupDelegate.LABEL],
                          userData=QVariant(defaultValue))
        return combo


    def setEditorData(self, editor, index):
        string = self.getStringOfValue(variant_to_pyobject(index.data()))
        for i in range(editor.count()):
            if editor.itemText(i) == string:
                editor.setCurrentIndex(i)
        


    def setModelData(self, editor, model, index):
        value = editor.itemData(editor.currentIndex())
        model.setData(index, value)
        
