
from __future__ import print_function

import os

#from ems.qt4.gui.widgets.richtext.baseeditor import BaseEditor

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

class GraphicsView(QGraphicsView):

    emptyAreaClicked = pyqtSignal(QPointF)

    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        #self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)

    def mousePressEvent(self, event):
        super(GraphicsView, self).mousePressEvent(event)

        clickedItem = self.itemAt(event.pos())

        if clickedItem and not isinstance(clickedItem, PageItem):
            return

        scenePoint = self.mapToScene(event.pos())
        self.emptyAreaClicked.emit(scenePoint)

    def setZoom(self, percent):
        transform = QTransform()
        scale = percent/100.0
        transform.scale(scale, scale)
        self.setTransform(transform)

class GraphicsScene(QGraphicsScene):

    focusItemChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(GraphicsScene, self).__init__(*args, **kwargs)
        self._currentFocusItem = None
        #self.selectionChanged.connect(self._onSelectionChanged)
        self._selectionRect = SelectionRect()
        self.setBackgroundBrush(QColor(187,187,187))

    def setFocusItem(self, item, reason=Qt.OtherFocusReason):
        super(GraphicsScene, self).setFocusItem(item, reason)

    def mouseReleaseEvent(self, event):
        super(GraphicsScene, self).mouseReleaseEvent(event)
        focusItem = self.focusItem()
        if self._currentFocusItem is focusItem:
            return
        self._currentFocusItem = focusItem
        self.focusItemChanged.emit()

    def _onSelectionChanged(self):
        items = self.selectedItems()
        if len(items) != 1:
            self._selectionRect.setVisible(False)
            return
        self._selectionRect.setTarget(items[0])
        self._selectionRect.setVisible(True)
        #self.addItem(self._selectionRect)
        print('selectionChanged', self.selectedItems())

class ZoomSlider(QSlider):
    pass

#resource = QResource()

resourcePath = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','ems','qt4','gui','widgets','icons.rcc'))
QResource.registerResource(resourcePath)

PageSize = (595, 842) # A4 in points

dialog = QWidget()

dialog.tools = GraphicsToolDispatcher(dialog)

textTool = TextTool()
dialog.tools.addTool(textTool)

dialog.charFormatActions = CharFormatActions(dialog)
dialog.blockFormatActions = BlockFormatActions(dialog)

dialog.setLayout(QVBoxLayout())
dialog.toolBars = ToolBarArea(dialog)
dialog.addToolBar = QToolBar()
dialog.textToolbar = QToolBar()
#dialog.textWidgetToolbar = QToolBar()

#dialog.toolbarArea = QToolBar(dialog)
dialog.layout().addWidget(dialog.toolBars)

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
dialog.charFormatActions.signals.charFormatDiffChanged.connect(textTool.mergeFormatOnWordOrSelection)
dialog.blockFormatActions.signals.blockFormatModified.connect(textTool.setBlockFormatOnCurrentBlock)
dialog.show()
