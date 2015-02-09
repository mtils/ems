'''
Created on 19.09.2011

@author: michi
'''
import locale
from datetime import datetime
from PyQt4.QtCore import QString, QSize, Qt
from PyQt4.QtGui import QStyledItemDelegate, QWidget, QStyleOptionViewItemV4, \
    QApplication, QStyle, QFontMetrics

from ems import qt4
from ems.qt4.util import variant_to_pyobject

class MapperDelegate(QStyledItemDelegate):

    def __init__(self, mapper, propertyName, parent=None):
        super(MapperDelegate, self).__init__(parent)
        self.mapper = mapper
        self.propertyName = propertyName

    def createEditor(self, parent, option, index):
        columnName = variant_to_pyobject(index.data(qt4.ColumnNameRole))
        widget = self.mapper.getWidget(columnName, parent)
        if isinstance(widget, QWidget):
            return widget
        return super(MapperDelegate, self).createEditor(parent, option, index)

    def sizeHint(self, option, index):
        value = variant_to_pyobject(index.data())
        if hasattr(value.__class__,'__ormDecorator__'):
            newOption = QStyleOptionViewItemV4()
            self.initStyleOption(newOption, index)
            text = self.getString(value)
            size = QSize(option.fontMetrics.width(text), option.fontMetrics.height())
            return size

        return QStyledItemDelegate.sizeHint(self, option, index)

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
        options = QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)

        style = QApplication.style() if options.widget is None \
            else options.widget.style()

        options.text = self.getString(value)
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

    def getString(self, ormObject):
        if hasattr(ormObject.__class__,'__ormDecorator__'):
            string = ormObject.__class__.__ormDecorator__().getReprasentiveString(ormObject)
            return QString.fromUtf8(unicode(string))
        if isinstance(ormObject, datetime):
            return "{0:%d.%m.%Y %H:%M}".format(ormObject)
        return unicode(ormObject)