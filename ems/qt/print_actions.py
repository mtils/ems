
from ems.qt import QtWidgets, QtCore, QtGui

QObject = QtCore.QObject
QAction = QtWidgets.QAction
QKeySequence = QtGui.QKeySequence
QIcon = QtGui.QIcon
ThemeIcon = QIcon.fromTheme
QApplication = QtWidgets.QApplication

class PrintActions(QObject):

    def __init__(self, parentWidget, resourcePath=':/edit'):
        super(PrintActions, self).__init__(parentWidget)
        self.resourcePath = resourcePath
        self.actions = []
        self._addActions(self.parent())


    def _addActions(self, parent):

        self.actionPrintPreview = QAction(
                ThemeIcon('document-print-preview', self._icon('print.png')),
                "PrintPre&view", parent, shortcut=QKeySequence.Print)

        self.actions.append(self.actionPrintPreview)


    def addToToolbar(self, toolbar):
        for action in self.actions:
            toolbar.addAction(action)

    def iconPath(self, fileName):
        return self.resourcePath + '/' + fileName

    def _icon(self, fileName):
        return QIcon(self.iconPath(fileName))