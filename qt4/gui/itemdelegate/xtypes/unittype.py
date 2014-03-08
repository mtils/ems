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
        return self.xType.value2String(self.xType.calc2View(value))

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
        viewVal = self.xType.calc2View(val)

        if viewVal == val:
            return super(UnitTypeDelegate, self).setEditorData(editor, index)

        if isinstance(editor, QLineEdit):
            viewVal = self.xType.calc2View(val)
            editor.setText(QString.fromUtf8(unicode(viewVal)))
        elif isinstance(editor, QSpinBox):
            editor.setValue(int(round(viewVal)))
        elif isinstance(editor, QDoubleSpinBox):
            editor.setValue(float(viewVal))

    def setModelData(self, editor, model, index):
        value = 0.0

        if isinstance(editor, QLineEdit):
            textValue = unicode(editor.text())
            if self.xType.pyType is int:
                value = QVariant(int(round(float(textValue))))
            elif self.xType.pyType is float:
                value = QVariant(round(float(textValue)))

        elif isinstance(editor, QAbstractButton):
            if isinstance(self.xType.itemType, BoolType):
                model.setData(index, QVariant(editor.isChecked()), Qt.EditRole)
                return None
            else:
                model.setData(index, self.getRadioButtonData(editor))
                return
        return XTypeDelegate.setModelData(self, editor, model, index)
