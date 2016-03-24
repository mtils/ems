
from ems.qt import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt
QWidget = QtWidgets.QWidget
QHBoxLayout = QtWidgets.QHBoxLayout
QVBoxLayout = QtWidgets.QVBoxLayout
QSpacerItem = QtWidgets.QSpacerItem
QSizePolicy = QtWidgets.QSizePolicy
QIcon = QtGui.QIcon
QApplication = QtWidgets.QApplication
QToolBar = QtWidgets.QToolBar
QAction = QtWidgets.QAction
QActionGroup = QtWidgets.QActionGroup
QKeySequence = QtGui.QKeySequence
QFont = QtGui.QFont
QPixmap = QtGui.QPixmap
QMessageBox = QtWidgets.QMessageBox
QComboBox = QtWidgets.QComboBox
QFontComboBox = QtWidgets.QFontComboBox
QFontDatabase = QtGui.QFontDatabase
QTextListFormat = QtGui.QTextListFormat
QTextBlockFormat = QtGui.QTextBlockFormat
QColorDialog = QtWidgets.QColorDialog
QTextCursor = QtGui.QTextCursor


class ToolBarArea(QWidget):

    def __init__(self, parent=None):
        super(ToolBarArea, self).__init__(parent)
        self._toolBars = []
        self._currentToolBarRow = 0
        self._toolBarContainers = []
        self._setupLayout()

    def addToolBar(self, toolBar):
        toolBar.setParent(self)
        self._lastRowWidget().layout().addWidget(toolBar)

    def addToolBarBreak(self):
        self._addToolBarRow()

    def _lastRowWidget(self):
        if not self.layout().count():
            self._addToolBarRow()
        last = self.layout().count() - 1
        return self.layout().itemAt(last).widget()

    def _setupLayout(self):
        self.setLayout(QVBoxLayout(self))
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0,0,0,0)

    def _addToolBarRow(self):
        self.layout().addWidget(self._createToolBarRow())

    def _createToolBarRow(self):
        rowWidget = QWidget(self)
        rowWidget.setLayout(QHBoxLayout(rowWidget))
        rowWidget.layout().setSpacing(0)
        rowWidget.layout().setContentsMargins(0,0,0,0)
        #spacerItem = QSpacerItem(10, 5, QSizePolicy.Expanding)
        #rowWidget.layout().addSpacerItem(spacerItem)
        return rowWidget