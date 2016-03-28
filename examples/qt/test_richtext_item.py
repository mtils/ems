
from __future__ import print_function

import os

#from ems.qt4.gui.widgets.richtext.baseeditor import BaseEditor

from ems.qt import QtWidgets, QtGui, QtCore

from ems.qt.richtext.inline_edit_graphicsitem import TextItem
from ems.qt.richtext.char_format_actions import CharFormatActions
from ems.qt.layout.toolbararea import ToolBarArea
from ems.qt.graphics.tool import GraphicsToolDispatcher
from ems.qt.graphics.text_tool import TextTool
from ems.qt.graphics.selection_rect import SelectionRect

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

QPointF = QtCore.QPointF

class GraphicsView(QGraphicsView):

    emptyAreaClicked = pyqtSignal(QPointF)

    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        #self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)

    def mousePressEvent(self, event):
        super(GraphicsView, self).mousePressEvent(event)

        if self.itemAt(event.pos()):
            return

        scenePoint = self.mapToScene(event.pos())
        self.emptyAreaClicked.emit(scenePoint)

class GraphicsScene(QGraphicsScene):

    focusItemChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(GraphicsScene, self).__init__(*args, **kwargs)
        self._currentFocusItem = None
        #self.selectionChanged.connect(self._onSelectionChanged)
        self._selectionRect = SelectionRect()

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

#resource = QResource()

resourcePath = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','ems','qt4','gui','widgets','icons.rcc'))
QResource.registerResource(resourcePath)

PageSize = (595, 842) # A4 in points

dialog = QWidget()

dialog.tools = GraphicsToolDispatcher(dialog)

textTool = TextTool()
dialog.tools.addTool(textTool)

dialog.charFormatActions = CharFormatActions(dialog)
dialog.setLayout(QVBoxLayout())
dialog.toolBars = ToolBarArea(dialog)
dialog.addToolBar = QToolBar()
dialog.textToolbar = QToolBar()

#dialog.toolbarArea = QToolBar(dialog)
dialog.layout().addWidget(dialog.toolBars)

for action in dialog.tools.actions:
    dialog.addToolBar.addAction(action)

dialog.charFormatActions.addToToolbar(dialog.textToolbar, addWidgets=False)

dialog.toolBars.addToolBar(dialog.addToolBar)
dialog.toolBars.addToolBarBreak()
dialog.toolBars.addToolBar(dialog.textToolbar)


view = GraphicsView()
dialog.layout().addWidget(view)
scene = GraphicsScene()
scene.setSceneRect(0, 0, PageSize[0], PageSize[1])
scene.focusItemChanged.connect(dialog.tools.updateFocusItem)
view.setScene(scene)
dialog.tools.setScene(scene)

view.emptyAreaClicked.connect(dialog.tools.addItemAt)

#textItem = TextItem('Hallo', QPointF(15.0,15.0), view.scene() )

textTool.currentCharFormatChanged.connect(dialog.charFormatActions.signals.updateCharFormatWithoutDiffs)
dialog.charFormatActions.signals.charFormatDiffChanged.connect(textTool.mergeFormatOnWordOrSelection)

dialog.show()
