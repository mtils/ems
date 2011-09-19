'''
Created on 19.09.2011

@author: michi
'''
from PyQt4.QtCore import QString
from PyQt4.QtGui import QStyledItemDelegate, QWidget, QStyleOptionViewItemV4, \
    QApplication, QStyle 

from ems import qt4
from ems.qt4.util import variant_to_pyobject

class MapperDelegate(QStyledItemDelegate):
    def __init__(self, strategy, ormObj, propertyName, parent=None):
        super(MapperDelegate, self).__init__(parent)
        self.strategy = strategy
        self.ormObj = ormObj
        self.propertyName = propertyName
    
    def createEditor(self, parent, option, index):
        columnName = variant_to_pyobject(index.data(qt4.ColumnNameRole))
        widget = self.strategy.getWidget(self.ormObj, columnName, parent)
        if isinstance(widget, QWidget):
            return widget
        return super(MapperDelegate, self).createEditor(parent, option, index)
    
#    def setEditorData(self, editor, index):
#        print "MapperDelegate.setEditorData %s" % variant_to_pyobject(index.data())
#        return QStyledItemDelegate.setEditorData(self, editor, index)
#    
#    def setModelData(self, editor, model, index):
#        print "MapperDelegate.setModelData %s" % variant_to_pyobject(index.data())
#        return QStyledItemDelegate.setModelData(self, editor, model, index)
    
    def paint(self, painter, option, index):
        value = variant_to_pyobject(index.data())
        if hasattr(value.__class__,'__ormDecorator__'):
            return self._paintOrmDecoratedObj(painter, option, index, value)
        return QStyledItemDelegate.paint(self, painter, option, index)
    
    def _paintOrmDecoratedObj(self, painter, option, index, value):
        string = value.__class__.__ormDecorator__().getReprasentiveString(value)
        
        options = QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)
        
        style = QApplication.style() if options.widget is None \
            else options.widget.style()
            
        options.text = QString.fromUtf8(string)
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)
        