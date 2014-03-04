
from PyQt4.QtCore import QModelIndex, Qt, QVariant, QAbstractItemModel
from PyQt4.QtGui import QAbstractProxyModel

from ems import qt4
from ems.qt4.util import variant_to_pyobject
from ems.qt4.itemmodel.editable_proxymodel import EditableProxyModel


class RepresentativeProxyModel(QAbstractProxyModel):

    def __init__(self, parent=None):
        super(RepresentativeProxyModel, self).__init__(parent)
        self._sourceColumn = -1
        self._count = 0

    def columnCount(self, parentIndex=QModelIndex()):
        return 1

    def rowCount(self, parentIndex=QModelIndex()):
        return self.sourceModel().rowCount()

    def parent(self, *args, **kwargs):
        return QModelIndex()

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, proxyIndex, role):
        if role in (Qt.DisplayRole, Qt.EditRole, Qt.UserRole):

            if proxyIndex.column() == 0:
                if self._sourceColumn != -1:
                    srcRole = Qt.EditRole
                    srcColumn = self._sourceColumn
                else:
                    srcRole = qt4.RowObjectRole
                    srcColumn = 0

                objVariant = self.sourceModel().index(proxyIndex.row(),
                                                      srcColumn).data(srcRole)

                obj = variant_to_pyobject(objVariant)
                if obj:
                    if role == Qt.UserRole:
                        return QVariant(obj.id)
                    else:# Display or Edit
                        #print "returning",self._count,  obj.__ormDecorator__().getReprasentiveString(obj)
                        self._count += 1
                        return QVariant(obj.__ormDecorator__().getReprasentiveString(obj))

        return super(RepresentativeProxyModel, self).data(proxyIndex, role)

    def sourceColumn(self):
        return self._sourceColumn

    def setSourceColumn(self, column):
        if self._sourceColumn == column:
            return
        self.beginResetModel()
        self._sourceColumn = column
        self.endResetModel()

    def index(self, row, col, parentIndex=QModelIndex()):
        return self.createIndex(row, col, parentIndex)

    def mapToSource(self, proxyIndex):
        return QModelIndex()
        return self.sourceModel().createIndex(proxyIndex.row(), proxyIndex.column())

    def mapFromSource(self, sourceIndex):
        if sourceIndex.column() == 0:
            return self.index(sourceIndex.row(),0)
        return QModelIndex()

    def onSourceModelDataChanged(self, topLeft, bottomRight):
        self.dataChanged.emit(self.index(topLeft.row(),0), self.index(bottomRight.row(), 0))

    def signal2ResetTranslator(self, unused1=None, unused2=None, unused3=None):
        self.reset()

    def setSourceModel(self, srcModel):
        if isinstance(self.sourceModel(), QAbstractItemModel):
            self.sourceModel().disconnect(self.onSourceModelDataChanged)
        srcModel.dataChanged.connect(self.onSourceModelDataChanged)
        srcModel.modelReset.connect(self.reset)
        srcModel.columnsInserted.connect(self.signal2ResetTranslator)
        srcModel.columnsMoved.connect(self.signal2ResetTranslator)
        srcModel.columnsRemoved.connect(self.signal2ResetTranslator)
        srcModel.rowsInserted.connect(self.signal2ResetTranslator)
        srcModel.rowsMoved.connect(self.signal2ResetTranslator)
        srcModel.rowsRemoved.connect(self.signal2ResetTranslator)
        QAbstractProxyModel.setSourceModel(self, srcModel)