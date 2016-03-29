
from __future__ import print_function

import os

from ems.qt import QtWidgets, QtGui, QtCore

from ems.qt.richtext.inline_edit_graphicsitem import TextItem
from ems.qt.richtext.char_format_actions import CharFormatActions
from ems.qt.richtext.block_format_actions import BlockFormatActions
from ems.qt.layout.toolbararea import ToolBarArea
from ems.qt.graphics.tool import GraphicsToolDispatcher
from ems.qt.graphics.text_tool import TextTool
from ems.qt.graphics.selection_rect import SelectionRect
from ems.qt.graphics.page_item import PageItem
from ems.qt.tool_widgets.one_of_a_list_slider import OneOfAListSlider
from ems.qt.edit_actions import EditActions
from ems.qt.graphics.graphics_view import GraphicsView
from ems.qt.graphics.graphics_scene import GraphicsScene

QAction = QtWidgets.QAction
pyqtSignal = QtCore.pyqtSignal
Qt = QtCore.Qt
QGraphicsView = QtWidgets.QGraphicsView
QGraphicsScene = QtWidgets.QGraphicsScene
QWidget = QtWidgets.QWidget
QVBoxLayout = QtWidgets.QVBoxLayout
QToolBar = QtWidgets.QToolBar
QResource = QtCore.QResource
QPainter = QtGui.QPainter
QColor = QtGui.QColor
QSlider = QtWidgets.QSlider
QPointF = QtCore.QPointF
QTransform = QtGui.QTransform

resourcePath = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','ems','qt4','gui','widgets','icons.rcc'))
QResource.registerResource(resourcePath)

PageSize = (595, 842) # A4 in points

dialog = QWidget()

dialog.tools = GraphicsToolDispatcher(dialog)

textTool = TextTool()
dialog.tools.addTool(textTool)

dialog.editActions = EditActions(dialog)
dialog.charFormatActions = CharFormatActions(dialog)
dialog.blockFormatActions = BlockFormatActions(dialog)

dialog.setLayout(QVBoxLayout())
dialog.toolBars = ToolBarArea(dialog)
dialog.addToolBar = QToolBar()
dialog.textToolbar = QToolBar()
#dialog.textWidgetToolbar = QToolBar()

#dialog.toolbarArea = QToolBar(dialog)
dialog.layout().addWidget(dialog.toolBars)

dialog.editActions.addToToolbar(dialog.addToolBar)
dialog.addToolBar.addSeparator()

for action in dialog.tools.actions:
    dialog.addToolBar.addAction(action)

dialog.charFormatActions.addToToolbar(dialog.textToolbar, addActions=False)
dialog.charFormatActions.addToToolbar(dialog.textToolbar, addWidgets=False)
dialog.blockFormatActions.addToToolbar(dialog.textToolbar, addWidgets=False)

dialog.toolBars.addToolBar(dialog.addToolBar)
dialog.toolBars.addToolBarBreak()
dialog.toolBars.addToolBar(dialog.textToolbar)
#dialog.toolBars.addToolBarBreak()
#dialog.toolBars.addToolBar(dialog.textWidgetToolbar)


zoomSteps = (50,75,100,150,200,300,500)

view = GraphicsView()
dialog.layout().addWidget(view)
dialog.zoomSlider = OneOfAListSlider(dialog)
dialog.zoomSlider.setValueList(zoomSteps)
dialog.zoomSlider.setListValue(100)
dialog.zoomSlider.setOrientation(Qt.Horizontal)
dialog.zoomSlider.setTickInterval(1)
dialog.zoomSlider.setTickPosition(QSlider.TicksBothSides)
dialog.zoomSlider.listValueChanged.connect(view.setZoom)
dialog.layout().addWidget(dialog.zoomSlider)
scene = GraphicsScene()
scene.setSceneRect(0, 0, PageSize[0], PageSize[1])
scene.focusItemChanged.connect(dialog.tools.updateFocusItem)
view.setScene(scene)
dialog.tools.setScene(scene)

view.emptyAreaClicked.connect(dialog.tools.addItemAt)

page = PageItem()
scene.addItem(page)

#textItem = TextItem('Hallo', QPointF(15.0,15.0), view.scene() )

textTool.currentCharFormatChanged.connect(dialog.charFormatActions.signals.updateCharFormatWithoutDiffs)
textTool.currentBlockFormatChanged.connect(dialog.blockFormatActions.signals.setBlockFormat)
textTool.undoAvailable.connect(dialog.editActions.actionUndo.setEnabled)
textTool.redoAvailable.connect(dialog.editActions.actionRedo.setEnabled)
textTool.copyAvailable.connect(dialog.editActions.actionCopy.setEnabled)
textTool.copyAvailable.connect(dialog.editActions.actionCut.setEnabled)
dialog.editActions.actionUndo.triggered.connect(textTool.undo)
dialog.editActions.actionRedo.triggered.connect(textTool.redo)
dialog.editActions.actionCopy.triggered.connect(textTool.copy)
dialog.editActions.actionCut.triggered.connect(textTool.cut)
dialog.editActions.actionPaste.triggered.connect(textTool.paste)

dialog.charFormatActions.signals.charFormatDiffChanged.connect(textTool.mergeFormatOnWordOrSelection)
dialog.blockFormatActions.signals.blockFormatModified.connect(textTool.setBlockFormatOnCurrentBlock)
dialog.show()
