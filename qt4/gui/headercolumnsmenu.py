from PyQt4.QtCore import SIGNAL,QVariant, Qt, QString
from PyQt4.QtGui import QMenu, QAction

from ems.qt4.util import variant_to_pyobject as py


class HeaderColumnsMenu(QMenu):

    def __init__(self, title=None, parent=None):

        if title is not None:
            super(HeaderColumnsMenu, self).__init__(title, parent)
        else:
            super(HeaderColumnsMenu, self).__init__(parent)

        self._header = None
        self._currentlyUpdating = False
        self._lastVisibleColumns = []
        self._refreshAfterModelReset = True
        self.triggered.connect(self._onActionTriggered)

    def header(self):
        return self._header

    def setHeader(self, header):
        self._header = header
        self._header.customContextMenuRequested.connect(self.displayMenu)

    def displayMenu(self, point):
        self._updateColumnStates()
        self.exec_(self._header.mapToGlobal(point))

    def _onActionTriggered(self, action):
        col = py(action.data())
        if isinstance(col, int) and col > -1:
            self._header.setSectionHidden(col, not action.isChecked())

    def _updateColumnStates(self):
        self.clear()
        self._lastVisibleColumns = []
        model = self._header.model()
        for col in range(self._header.count()):
            title = py(model.headerData(col, Qt.Horizontal, Qt.DisplayRole))
            action = QAction(QString.fromUtf8(title), self)
            action.setData(QVariant(col))
            action.setCheckable(True)
            if self._header.isSectionHidden(col):
                action.setChecked(False)
            else:
                action.setChecked(True)
                self._lastVisibleColumns.append(col)
            self.addAction(action)
