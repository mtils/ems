
from ems.typehint import accepts
from ems.qt.event_hook_proxy import SignalEventHookProxy
from ems.qt import QtWidgets, QtGui, QtCore, QtPrintSupport
from ems.qt.graphics.graphics_scene import GraphicsScene, BackgroundCorrector
from ems.qt.graphics.graphics_widget import GraphicsWidget
from ems.qt.graphics.storage.interfaces import SceneStorageManager
from ems.qt.graphics.tool import GraphicsTool
from ems.qt.graphics.tool import GraphicsToolDispatcher
from ems.qt.graphics.text_tool import TextTool
from ems.qt.graphics.pixmap_tool import PixmapTool
from ems.qt.graphics.interfaces import Finalizer
from ems.qt.graphics.page_item import PageItemHider, PageItem

Qt = QtCore.Qt
QObject = QtCore.QObject
QRectF = QtCore.QRectF
pyqtProperty = QtCore.pyqtProperty
pyqtSlot = QtCore.pyqtSlot
QWidget = QtWidgets.QWidget
QVBoxLayout = QtWidgets.QVBoxLayout
QToolBar = QtWidgets.QToolBar
QSlider = QtWidgets.QSlider
QAction = QtWidgets.QAction
QKeySequence = QtGui.QKeySequence
QPrintPreviewDialog = QtPrintSupport.QPrintPreviewDialog
QPainter = QtGui.QPainter

class SceneManager(QObject):

    def __init__(self, parent=None, storageManager=None):
        super(SceneManager, self).__init__(parent)
        self._scene = None
        self._widget = None
        self._tools = None
        self._storageManager = None
        self._importStorageManager = None
        self._loadAction = None
        self._saveAction = None
        self._importAction = None
        self._exportAction = None
        self._actions = []
        self._finalizers = [BackgroundCorrector(), PageItemHider()]
        if storageManager:
            self.setStorageManager(storageManager)

    def actions(self):
        if not self._actions:
            self._populateActions()
        return self._actions

    def getScene(self):
        if not self._scene:
            self._scene = GraphicsScene()
            self._scene.deleteRequested.connect(self.deleteIfWanted)
        return self._scene

    scene = pyqtProperty(GraphicsScene, getScene)

    def getWidget(self):
        if not self._widget:
            self._widget = GraphicsWidget(scene=self.scene, tools=self.tools)
            self._addActionsToWidget(self._widget)
            self._widget.printPreviewRequested.connect(self.showPrintPreviewDialog)
        return self._widget

    widget = pyqtProperty(GraphicsWidget, getWidget)

    def getTools(self):
        if not self._tools:
            self._tools = self._createTools()
        return self._tools

    tools = pyqtProperty(GraphicsTool, getTools)

    def load(self, *args):
        if self._storageManager:
            return self._storageManager.load()

    def save(self, *args):
        if self._storageManager:
            return self._storageManager.save()

    def importScene(self, *args):
        if self._importStorageManager:
            return self._importStorageManager.load()

    def exportScene(self, *args):
        if self._importStorageManager:
            return self._importStorageManager.save()

    def getStorageManager(self):
        return self._storageManager

    @pyqtSlot(SceneStorageManager)
    def setStorageManager(self, storageManager):
        self._storageManager = storageManager
        self._storageManager.setScene(self.scene)
        self._storageManager.setTools(self.tools)

    storageManager = pyqtProperty(SceneStorageManager, getStorageManager, setStorageManager)

    def getImportStorageManager(self):
        return self._importStorageManager

    def setImportStorageManager(self, storageManager):
        self._importStorageManager = storageManager
        self._importStorageManager.setScene(self.scene)
        self._importStorageManager.setTools(self.tools)

    importStorageManager = pyqtProperty(SceneStorageManager, getImportStorageManager, setImportStorageManager)

    @property
    def loadAction(self):
        if self._loadAction:
            return self._loadAction

        self._loadAction = QAction('Load', self.getWidget(), shortcut = QKeySequence.Open)
        self._loadAction.triggered.connect(self.load)
        return self._loadAction

    @property
    def saveAction(self):
        if self._saveAction:
            return self._saveAction
        self._saveAction = QAction('Save', self.getWidget(), shortcut = QKeySequence.Save)
        self._saveAction.triggered.connect(self.save)
        return self._saveAction

    @property
    def importAction(self):
        if self._importAction:
            return self._importAction
        self._importAction = QAction('Import', self.getWidget())
        self._importAction.triggered.connect(self.importScene)
        return self._importAction

    @property
    def exportAction(self):
        if self._exportAction:
            return self._exportAction
        self._exportAction = QAction('Export', self.getWidget())
        self._exportAction.triggered.connect(self.exportScene)
        return self._exportAction

    def printScene(self, printer, painter=None):
        painter = painter if isinstance(painter, QPainter) else QPainter(printer)
        for finalizer in self._finalizers:
            finalizer.toFinalized(self.scene)
        pageItem = self._findPageItem()
        if pageItem:
            self.scene.render(painter, QRectF(), pageItem.boundingRect())
        else:
            self.scene.render(painter)

        for finalizer in self._finalizers:
            finalizer.toEditable(self.scene)

    def showPrintPreviewDialog(self):
        margin = 30
        parent = self.getWidget()
        self.printPrvDlg = QPrintPreviewDialog(parent)
        self.printPrvDlg.setWindowTitle(u'Druckvorschau')
        self.printPrvDlg.paintRequested.connect(self.printScene)
        self.printPrvDlg.resize(parent.width()-margin, parent.height()-margin)
        self.printPrvDlg.show()

    def deleteIfWanted(self):
        items = self.scene.selectedItems()
        if not len(items):
            return

        for item in items:
            self.scene.removeItem(item)

    @accepts(Finalizer)
    def addFinalizer(self, finalizer):
        self._finalizers.append(finalizer)

    def hasFinalizer(self, finalizer):
        return finalizer in self._finalizers

    def finalizer(self, cls):
        for finalizer in self._finalizers:
            if isinstance(finalizer, cls):
                return finalizer

    def _createTools(self):
        tools = GraphicsToolDispatcher(self)
        tools.setScene(self.scene)
        textTool = TextTool()
        tools.addTool(textTool)
        pixmapTool = PixmapTool()
        tools.addTool(pixmapTool)
        return tools

    def _populateActions(self):
        if self._actions:
            return
        self._actions.append(self.loadAction)
        self._actions.append(self.saveAction)
        self._actions.append(self.importAction)
        self._actions.append(self.exportAction)

    def _addActionsToWidget(self, widget):
        for action in self.actions():
            widget.addAction(action)

    def _findPageItem(self):
        for item in self.scene.items():
            if isinstance(item, PageItem):
                return item