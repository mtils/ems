
from __future__ import print_function

from ems.qt import QtWidgets, QtCore, QtGui
from ems.qt.tool_widgets.color_select import ColorSelect


QDialog = QtWidgets.QDialog
QLabel = QtWidgets.QLabel
QFormLayout = QtWidgets.QFormLayout

dialog = QDialog()
dialog.setLayout(QFormLayout())

dialog.label = QLabel('Select a color:', parent=dialog)
dialog.select = ColorSelect(dialog)

dialog.layout().addRow(dialog.label, dialog.select)

dialog.resize(800,600)
dialog.exec_()
