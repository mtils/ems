
from __future__ import print_function

#from ems.qt4.gui.widgets.richtext.baseeditor import BaseEditor

from ems.qt import QtWidgets, QtGui, QtCore

from ems.qt.richtext.inline_edit_graphicsitem import TextItem
from ems.qt.richtext.char_format_actions import CharFormatActions
from ems.qt.layout.toolbararea import ToolBarArea
from ems.qt.graphics.tool import GraphicsToolDispatcher
from ems.qt.graphics.text_tool import TextTool

QAction = QtWidgets.QAction
pyqtSignal = QtCore.pyqtSignal
QGraphicsView = QtWidgets.QGraphicsView
QGraphicsScene = QtWidgets.QGraphicsScene
QWidget = QtWidgets.QWidget
QVBoxLayout = QtWidgets.QVBoxLayout
QToolBar = QtWidgets.QToolBar

QPointF = QtCore.QPointF

class GraphicsView(QGraphicsView):

    emptyAreaClicked = pyqtSignal(QPointF)

    def mousePressEvent(self, event):
        super(GraphicsView, self).mousePressEvent(event)

        if self.itemAt(event.pos()):
            return

        scenePoint = self.mapToScene(event.pos())
        self.emptyAreaClicked.emit(scenePoint)


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
scene = QGraphicsScene()
scene.setSceneRect(0, 0, PageSize[0], PageSize[1])
scene.selectionChanged.connect(dialog.tools._onSceneSelectionChanged)
view.setScene(scene)
dialog.tools.setScene(scene)

view.emptyAreaClicked.connect(dialog.tools.handleEmptyAreaClick)

#textItem = TextItem('Hallo', QPointF(15.0,15.0), view.scene() )

textTool.currentCharFormatChanged.connect(dialog.charFormatActions.signals.updateCharFormatWithoutDiffs)
dialog.charFormatActions.signals.charFormatDiffChanged.connect(textTool.mergeFormatOnWordOrSelection)

dialog.show()
