
from __future__ import print_function

import sys

from ems.qt import QtWidgets, QtCore, QtGui
from ems.qt.tool_widgets.image_select import ImageSelect


QDialog = QtWidgets.QDialog
QLabel = QtWidgets.QLabel
QFormLayout = QtWidgets.QFormLayout

dialog = QDialog()
dialog.setLayout(QFormLayout())

dialog.label = QLabel('Select an image:', parent=dialog)
dialog.select = ImageSelect(dialog)

dialog.layout().addRow(dialog.label, dialog.select)

dialog.resize(800,600)
sys.exit(dialog.exec_())
