
from __future__ import print_function

from collections import OrderedDict

from PyQt4.QtCore import Qt, QModelIndex, QVariant, QAbstractItemModel, QString
from PyQt4.QtCore import pyqtSignal

from ems import qt4
from ems.qt4.util import cast_to_variant, variant_to_pyobject

class OrderedDictModel(QAbstractItemModel):

    """
    @brief A Model which behaves exactly like an OrderedDict and emits all changes
           via standard model signals.
           The layout is keys -> headerData(), values -> data()

    """

    _pyData = OrderedDict()
    editable = True

    def __init__(self, srcData=None, parent=None):
        """
        @brief Takes all supported args from OrderedDict or an OrderedDict itself

        :returns: None
        """
        super(OrderedDictModel, self).__init__(parent)

        if isinstance(srcData, OrderedDict):
            self._pyData = srcData

        elif srcData is None:
            self._pyData = OrderedDict()

        else:
            self._pyData = OrderedDict(srcData)

    def rowCount(self, parent=QModelIndex()):
        """
        @brief Returns the amount of rows. 0 if empty, 1 if filled

        :returns: int
        """
        return 1 if len(self._pyData) else 0

    def columnCount(self, parent=QModelIndex()):
        """
        @brief Returns the length of columns (the amount of keys)

        :returns: int
        """
        return len(self._pyData)

    def index(self, row, column, parent=QModelIndex()):
        """
        @brief Returns the index for passed position

        :returns: QModelIndex
        """
        return self.createIndex(row, column, object=0)

    def headerData(self, section, orientation, role):
        """
        @brief Returns the header Data for section section

        :returns: QVariant
        """

        if orientation == Qt.Horizontal and role in (Qt.DisplayRole, qt4.FieldTitleRole):
            return QVariant(self.keyOfColumn(section))

        return super(OrderedDictModel, self).headerData(section, orientation, role)

    def flags(self, index):
        """
        @brief Return the item flags. See self.editable, others are currently
               not supported

        :param index: the QModelIndex
        :type index: QModelIndex

        :returns: int
        """

        if self.editable:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled  | Qt.ItemIsEditable

        return super(OrderedDictModel, self).flags(index)

    def data(self, index, role=Qt.DisplayRole):
        """
        @brief Returns data by index

        :param index: The index you ask for
        :type index: QModelIndex
        :param role: Which kind of data?
        :type role: int

        :returns: QVariant
        """

        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()

        if role not in (Qt.DisplayRole, Qt.EditRole):
            return QVariant()

        try:
            key = self.keyOfColumn(index.column())

            return cast_to_variant(self._pyData[key])

        except IndexError:
            return QVariant()

    def setData(self, index, value, role=Qt.EditRole):

        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return False

        keyName = self.keyOfColumn(index.column())
        pyValue = variant_to_pyobject(value)

        if pyValue == self._pyData[keyName]:
            return False

        self._pyData[keyName] = pyValue
        self.dataChanged.emit(index, index)
        return True

    def keyOfColumn(self, column):
        return self._pyData.keys()[column]

    def columnOfKey(self, key):
        return self._pyData.keys().index(key)

    def setDict(self, dictObject):
        self.beginResetModel()

        self._pyData.clear()
        for key in dictObject:
            self._pyData[key] = dictObject[key]

        self.endResetModel()

    def parent(self, child):
        return QModelIndex()

    def __getitem__(self, key):
        return self._pyData[key]

    def __setitem__(self, key, value):

        if key in self._pyData:
            return self._overwrite(key, value)

        self._addKey(key, value)

    def __delitem__(self, key):

        col = self.columnOfKey(key)

        self.beginRemoveColumns(QModelIndex(), col, col)
        del self._pyData[key]
        self.endRemoveColumns()

    def _overwrite(self, key, value):

        if self._pyData[key] == value:
            return

        self._pyData[key] = value

        index = self.createIndex(0, self.columnOfKey(key))

        self.dataChanged.emit(index, index)

    def _addKey(self, key, value):

        self.beginInsertColumns(QModelIndex(),self.columnCount(), self.columnCount())

        self._pyData[key] = value

        self.endInsertColumns()

if __name__ == '__main__':

    import sys
    from PyQt4.QtCore import QObject, pyqtSignal
    from PyQt4.QtGui import *

    testDict = OrderedDict([
        ('first_name','John'),
        ('last_name','Doe'),
        ('age',35)
    ])

    class SignalPrinter(QObject):

        def printDataChanged(self, fromIndex, toIndex):
            print(u'Data Changed row:{0} column: {1} value:{2}'.format(fromIndex.row(),fromIndex.column(),variant_to_pyobject(fromIndex.data())))

    printer = SignalPrinter()
    model = OrderedDictModel()
    model.setDict(testDict)
    model.printer = SignalPrinter()

    model.dataChanged.connect(model.printer.printDataChanged)

    app = QApplication(sys.argv)
    win = QTableView()
    win.setModel(model)

    win.show()

    sys.exit(app.exec_())