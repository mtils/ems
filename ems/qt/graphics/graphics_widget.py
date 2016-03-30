
from ems.typehint import accepts
from ems.qt import QtWidgets, QtGui, QtCore
from ems.qt.graphics.tool import GraphicsToolDispatcher
from ems.qt.graphics.text_tool import TextTool
from ems.qt.edit_actions import EditActions
from ems.qt.richtext.char_format_actions import CharFormatActions
from ems.qt.richtext.block_format_actions import BlockFormatActions
from ems.qt.layout.toolbararea import ToolBarArea
from ems.qt.graphics.graphics_view import GraphicsView
from ems.qt.graphics.graphics_scene import GraphicsScene
from ems.qt.tool_widgets.one_of_a_list_slider import OneOfAListSlider
from ems.qt.graphics.page_item import PageItem

Qt = QtCore.Qt
QWidget = QtWidgets.QWidget
QVBoxLayout = QtWidgets.QVBoxLayout
QToolBar = QtWidgets.QToolBar
QSlider = QtWidgets.QSlider
QAction = QtWidgets.QAction

class GraphicsWidget(QWidget):

    def __init__(self, parent=None):
        super(GraphicsWidget, self).__init__(parent)
        self._zoomSteps = (50,75,100,150,200,300,500)
        self._pageSize = (595, 842) # A4 in points
        self._setUpUi()
        self._setUpTools()
        self._addToolsToToolbars()
        self._connectTools()
        self._setupPageFormat()

    def _setUpUi(self):
        self.setLayout(QVBoxLayout())
        self.toolBars = ToolBarArea(self)
        self.addToolBar = QToolBar()
        self.textToolbar = QToolBar()
        self.layout().addWidget(self.toolBars)
        self.view = GraphicsView()
        self.layout().addWidget(self.view)
        self._zoomSlider = self._createZoomSlider(self, self._zoomSteps)
        self._zoomSlider.listValueChanged.connect(self.view.setZoom)
        self.layout().addWidget(self._zoomSlider)
        self.scene = GraphicsScene()
        self.view.setScene(self.scene)
        self.scene.setSceneRect(0, 0, self._pageSize[0], self._pageSize[1])



    def _setUpTools(self):
        self.tools = GraphicsToolDispatcher(self)
        self.tools.setScene(self.scene)
        self.textTool = TextTool()
        self.tools.addTool(self.textTool)
        self.editActions = EditActions(self)
        self.charFormatActions = CharFormatActions(self)
        self.blockFormatActions = BlockFormatActions(self)

        self.scene.focusItemChanged.connect(self.tools.updateFocusItem)
        self.view.emptyAreaClicked.connect(self.tools.addItemAt)


    def _addToolsToToolbars(self):
        self.editActions.addToToolbar(self.addToolBar)
        self.addToolBar.addSeparator()
        for action in self.tools.actions:
            self.addToolBar.addAction(action)
        self.charFormatActions.addToToolbar(self.textToolbar, addActions=False)
        self.charFormatActions.addToToolbar(self.textToolbar, addWidgets=False)
        self.blockFormatActions.addToToolbar(self.textToolbar, addWidgets=False)
        self.toolBars.addToolBar(self.addToolBar)
        self.toolBars.addToolBarBreak()
        self.toolBars.addToolBar(self.textToolbar)

    def _createZoomSlider(self, parent, zoomSteps):
        zoomSlider = OneOfAListSlider(parent)
        zoomSlider.setValueList(zoomSteps)
        zoomSlider.setListValue(100)
        zoomSlider.setOrientation(Qt.Horizontal)
        zoomSlider.setTickInterval(1)
        zoomSlider.setTickPosition(QSlider.TicksBothSides)
        return zoomSlider

    def _connectTools(self):
        self.textTool.currentCharFormatChanged.connect(self.charFormatActions.signals.updateCharFormatWithoutDiffs)
        self.textTool.currentBlockFormatChanged.connect(self.blockFormatActions.signals.setBlockFormat)
        self.textTool.undoAvailable.connect(self.editActions.actionUndo.setEnabled)
        self.textTool.redoAvailable.connect(self.editActions.actionRedo.setEnabled)
        self.textTool.copyAvailable.connect(self.editActions.actionCopy.setEnabled)
        self.textTool.copyAvailable.connect(self.editActions.actionCut.setEnabled)
        self.editActions.actionUndo.triggered.connect(self.textTool.undo)
        self.editActions.actionRedo.triggered.connect(self.textTool.redo)
        self.editActions.actionCopy.triggered.connect(self.textTool.copy)
        self.editActions.actionCut.triggered.connect(self.textTool.cut)
        self.editActions.actionPaste.triggered.connect(self.textTool.paste)

        self.charFormatActions.signals.charFormatDiffChanged.connect(self.textTool.mergeFormatOnWordOrSelection)
        self.blockFormatActions.signals.blockFormatModified.connect(self.textTool.setBlockFormatOnCurrentBlock)

    def _setupPageFormat(self):
        page = PageItem()
        self.scene.addItem(page)