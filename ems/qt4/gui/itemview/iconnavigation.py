from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ems.qt4.util import variant_to_pyobject
from ems.qt4.gui.widgets.graphical import ColorButton #@UnresolvedImport
from ems.qt4.gui.itemdelegate.iconview import IconViewDelegate #@UnresolvedImport

class IconNavigationView(QListView):
    def __init__(self, parent=None):
        QListView.__init__(self, parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewMode(QListView.IconMode)
        self.setAutoScroll(False)
        self.setItemDelegate(IconViewDelegate(self))
        self.setSpacing(0)
        self.setUniformItemSizes(True)
        self.setMovement(QListView.Static)
        #self.setTextElideMode(Qt.ElideNone)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))

    def setModel(self, model):
        if isinstance(self.model(), QAbstractItemModel):
            self.model().rowsRemoved.disconnect(self._onModelChanges)
            self.model().rowsMoved.disconnect(self._onModelChanges)
            self.model().layoutChanged.disconnect(self._onModelChanges)
            self.model().rowsInserted.disconnect(self._onModelChanges)
            self.model().layoutChanged.disconnect(self._onModelChanges)
            self.model().modelReset.disconnect(self._onModelChanges)

        QListView.setModel(self, model)

        self.model().rowsRemoved.connect(self._onModelChanges)
        self.model().rowsMoved.connect(self._onModelChanges)
        self.model().layoutChanged.connect(self._onModelChanges)
        self.model().rowsInserted.connect(self._onModelChanges)
        self.model().layoutChanged.connect(self._onModelChanges)
        self.model().modelReset.connect(self._onModelChanges)
        self.updateGeometryByContents()

    def sizeHint(self):
        if not self.model():
            width = self.iconSize().width()
            height = self.iconSize().width()
            if isinstance(self.itemDelegate(), IconViewDelegate):
                height = height + self.itemDelegate().calculateTextSize().height()
            return QSize(width, height)
            return QListView.sizeHint(self)
        s = QSize()
        maxLength = 0
        maxLengthRow = 0
        for i in range(self.model().rowCount()):
            displayText = variant_to_pyobject(self.model().index(i,0).data(Qt.DisplayRole))
            if isinstance(displayText, basestring):
                length = len(displayText)
                if length > maxLength:
                    maxLength = length
                    maxLengthRow = i
        itemSizeHint = self.sizeHintForIndex(self.model().index(maxLengthRow,0))
        s.setHeight(itemSizeHint.height()+self.frameWidth()*2)
        s.setWidth(itemSizeHint.width()*self.model().rowCount()+self.frameWidth()*2)
        return s

    def scrollContentsBy(self, dx, dy):
        return

    def setIconSize(self, newSize):
        QListView.setIconSize(self, newSize)
        self.updateGeometryByContents()

    def _onModelChanges(self, unused1=None, unused2=None):
        self.updateGeometryByContents()

    def updateGeometryByContents(self):
        #if self.isVisible():
        self.resize(self.sizeHint())
        self.updateGeometry()