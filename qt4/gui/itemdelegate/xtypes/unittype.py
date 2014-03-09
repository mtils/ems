'''
Created on 04.03.2012

@author: michi
'''
from PyQt4.QtCore import QString, Qt, QVariant
from PyQt4.QtGui import QSpinBox, QDoubleSpinBox, QLineEdit

from ems.qt4.util import variant_to_pyobject as py
from ems.xtype.base import UnitType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypedelegate import XTypeDelegate #@UnresolvedImport

class UnitTypeDelegate(XTypeDelegate):

    def __init__(self, xType, parent=None):
        XTypeDelegate.__init__(self, xType, parent)
        self.textAlignment = Qt.AlignRight | Qt.AlignVCenter

    def getString(self, value):
        if value is None:
            return ""
        return self.xType.value2String(self.xType.modelToView(value))

    def createEditor(self, parent, option, index):
        if self.xType.pyType == float:
            widget = QDoubleSpinBox(parent)
            if self.xType.decimalsCount:
                widget.setDecimals(self.xType.decimalsCount)
        elif self.xType.pyType == int:
            widget = QSpinBox(parent)
        else:
            return XTypeDelegate.createEditor(self, parent, option, index)

        self.configureEditor(widget, self.xType)

        return widget

    def configureEditor(self, widget, xType):
        XTypeDelegate.configureEditor(self, widget, xType)
        widget.setSuffix(QString.fromUtf8(self.xType.strSuffix))
        widget.setPrefix(QString.fromUtf8(self.xType.strPrefix))
        widget.setMinimum(self.xType.minValue)
        widget.setMaximum(self.xType.maxValue)
        if self.xType.pyType == float and self.xType.decimalsCount is not None:
            widget.setDecimals(self.xType.decimalsCount)

    def setEditorData(self, editor, index):

        val = py(index.data(Qt.EditRole))
        viewVal = self.xType.modelToView(val)

        if viewVal == val:
            return super(UnitTypeDelegate, self).setEditorData(editor, index)

        if isinstance(editor, QLineEdit):
            viewVal = self.xType.modelToView(val)
            editor.setText(QString.fromUtf8(unicode(viewVal)))
        elif isinstance(editor, QSpinBox):
            editor.setValue(int(round(viewVal)))
        elif isinstance(editor, QDoubleSpinBox):
            editor.setValue(float(viewVal))

    def setModelData(self, editor, model, index):
        value = None

        if isinstance(editor, QLineEdit):
            textValue = unicode(editor.text())
            if self.xType.pyType is int:
                value = QVariant(int(round(float(textValue))))
            elif self.xType.pyType is float:
                value = QVariant(float(textValue))
            if value is None:
                raise ValueError("Couldnt cast value {0} to model".format(textValue))

        elif isinstance(editor, (QSpinBox, QDoubleSpinBox)):
            value = editor.value()

        else:
            raise NotImplementedError("Couldnt retrieve value from unknown widget {0}".format(editor))

        model.setData(index, QVariant(self.xType.viewToModel(value) ), Qt.EditRole)
        return
        return XTypeDelegate.setModelData(self, editor, model, index)
