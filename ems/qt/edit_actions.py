
from ems.qt import QtWidgets, QtCore, QtGui

QObject = QtCore.QObject
QAction = QtWidgets.QAction
QKeySequence = QtGui.QKeySequence
QIcon = QtGui.QIcon
ThemeIcon = QIcon.fromTheme
QApplication = QtWidgets.QApplication

class EditActions(QObject):

    def __init__(self, parentWidget, resourcePath=':/edit'):
        super(EditActions, self).__init__(parentWidget)
        self.resourcePath = resourcePath
        self.actions = []
        self._addActions(self.parent())


    def _addActions(self, parent):

        self.actionUndo = QAction(
                ThemeIcon('edit-undo', QIcon(self.iconPath('undo.png'))),
                "&Undo", parent, shortcut=QKeySequence.Undo)

        self.actions.append(self.actionUndo)


        self.actionRedo = QAction(
                ThemeIcon('edit-redo', QIcon(self.iconPath('redo.png'))),
                "&Redo", self, priority=QAction.LowPriority,
                shortcut=QKeySequence.Redo)

        self.actions.append(self.actionRedo)


        self.actionCut = QAction(
                ThemeIcon('edit-cut', QIcon(self.iconPath('scissors.png'))),
                "Cu&t", self, priority=QAction.LowPriority,
                shortcut=QKeySequence.Cut)

        self.actions.append(self.actionCut)

        self.actionCopy = QAction(
                ThemeIcon('edit-copy', QIcon(self.iconPath('copy.png'))),
                "&Copy", self, priority=QAction.LowPriority,
                shortcut=QKeySequence.Copy)

        self.actions.append(self.actionCopy)

        self.actionPaste = QAction(
                ThemeIcon('edit-paste', QIcon(self.iconPath('clipboard.png'))),
                "&Paste", self, priority=QAction.LowPriority,
                shortcut=QKeySequence.Paste,
                enabled=(len(QApplication.clipboard().text()) != 0))

        self.actions.append(self.actionPaste)

    def addToToolbar(self, toolbar):
        for action in self.actions:
            toolbar.addAction(action)

    def iconPath(self, fileName):
        return self.resourcePath + '/' + fileName