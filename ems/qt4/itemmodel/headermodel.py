
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, Qt, QVariant
from reflectable_mixin import ReflectableMixin

class HeaderModel(QAbstractItemModel, ReflectableMixin):
    """
    @brief This is a model which turn headerData into a name: value Model
           So its rowCount is the columnCount of its sourceModel.
           ColumnCount is always 2 (title, value)
           
    """
    
    
    def __init__(self, parent=None):
        QAbstractItemModel.__init__(self, parent)
        self._sourceModel = None
        self._headerDataRole = Qt.DisplayRole

    def direction(self):
        return ReflectableMixin.Vertical

    def headerDataRole(self):
        return self._headerDataRole

    def setHeaderDataRole(self, role):
        self._headerDataRole = role

    def sourceModel(self):
        """
        @brief The source
        
        :returns: QAbstractItemModel
        """
        return self._sourceModel

    def setSourceModel(self, model):
        """
        @brief Sets the source model
        @param: QAbstractItemModel model

        :returns: void
        """
        if isinstance(self._sourceModel, QAbstractItemModel):
            self._sourceModel.columnsInserted.disconnect(self._onColumnsInserted)
            self._sourceModel.columnsMoved.disconnect(self._onColumnsMoved)
            self._sourceModel.columnsRemoved.disconnect(self._onColumnsRemoved)
            self._sourceModel.dataChanged.disconnect(self._onDataChanged)
            self._sourceModel.headerDataChanged.disconnect(self._onHeaderDataChanged)
            self._sourceModel.layoutChanged.disconnect(self._onLayoutChanged)
            self._sourceModel.modelReset.disconnect(self._onModelReset)
            self._sourceModel.rowsInserted.disconnect(self._onRowsInserted)
            self._sourceModel.rowsMoved.disconnect(self._onRowsMoved)
            self._sourceModel.rowsRemoved.disconnect(self._onRowsRemoved)

        self._sourceModel = model

        self._sourceModel.columnsInserted.connect(self._onColumnsInserted)
        self._sourceModel.columnsMoved.connect(self._onColumnsMoved)
        self._sourceModel.columnsRemoved.connect(self._onColumnsRemoved)
        self._sourceModel.dataChanged.connect(self._onDataChanged)
        self._sourceModel.headerDataChanged.connect(self._onHeaderDataChanged)
        self._sourceModel.layoutChanged.connect(self._onLayoutChanged)
        self._sourceModel.modelReset.connect(self._onModelReset)
        self._sourceModel.rowsInserted.connect(self._onRowsInserted)
        self._sourceModel.rowsMoved.connect(self._onRowsMoved)
        self._sourceModel.rowsRemoved.connect(self._onRowsRemoved)

    def _onColumnsInserted(self, parent, start, end):
        self.reset()

    def _onColumnsMoved(self, sourceParent, sourceStart, sourceEnd,
                        destinationParent, destinationColumn):
        self.reset()

    def _onColumnsRemoved(self, parent, start, end):
        self.reset()

    def _onDataChanged(self, topLeft, bottomRight):
        self.reset()

    def _onHeaderDataChanged(self, orientation, first, last):
        self.reset()

    def _onLayoutChanged(self):
        self.reset()

    def _onModelReset(self):
        self.reset()

    def _onRowsInserted(self, parent, start, end):
        self.reset()

    def _onRowsMoved(self, sourceParent, sourceStart, sourceEnd,
                     destinationParent, destinationRow):
        self.reset()

    def _onRowsRemoved(self, parent, start, end):
        self.reset()

    def rowCount(self, parent=QModelIndex()):
        if self._sourceModel:
            return self._sourceModel.columnCount(parent)
        return 0

    def columnCount(self, parent=QModelIndex()):
        return 2

    def index(self, row, column, parent=QModelIndex()):
        return QAbstractItemModel.createIndex(self, row, column, parent)

    def parent(self, index):
        return QModelIndex()

    def data(self, index, role=Qt.DisplayRole):
        if self._sourceModel:
            col = index.column()
            if col == 0:
                return self._sourceModel.headerData(index.row(), Qt.Horizontal, self._headerDataRole)
            if col == 1:
                return self._sourceModel.data(self._sourceModel.index(0,index.row()), role)
        return QVariant()

    def rowOfName(self, name):
        if isinstance(self._sourceModel, ReflectableMixin):
            return self._sourceModel.columnOfName(name)
        return -1