
from __future__ import print_function

#from ems.qt4.gui.widgets.richtext.baseeditor import BaseEditor

from ems.qt import QtWidgets, QtGui, QtCore

from ems.qt.richtext.inline_edit_graphicsitem import TextItem
from ems.qt.richtext.char_format_actions import CharFormatActions

QGraphicsView = QtWidgets.QGraphicsView
QGraphicsScene = QtWidgets.QGraphicsScene
QWidget = QtWidgets.QWidget
QVBoxLayout = QtWidgets.QVBoxLayout
QToolBar = QtWidgets.QToolBar

QPointF = QtCore.QPointF

PageSize = (595, 842) # A4 in points

dialog = QWidget()
dialog.charFormatActions = CharFormatActions(dialog)
dialog.setLayout(QVBoxLayout())
dialog.textToolbar = QToolBar(dialog)

#dialog.toolbarArea = QToolBar(dialog)
dialog.layout().addWidget(dialog.textToolbar)

dialog.charFormatActions.addToToolbar(dialog.textToolbar, addWidgets=False)


view = QGraphicsView()
dialog.layout().addWidget(view)
scene = QGraphicsScene()
scene.setSceneRect(0, 0, PageSize[0], PageSize[1])
view.setScene(scene)

textItem = TextItem('Hallo', QPointF(15.0,15.0), view.scene() )

textItem.currentCharFormatChanged.connect(dialog.charFormatActions.signals.updateCharFormatWithoutDiffs)
dialog.charFormatActions.signals.charFormatDiffChanged.connect(textItem.mergeFormatOnWordOrSelection)

dialog.show()
