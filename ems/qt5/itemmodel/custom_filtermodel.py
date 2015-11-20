
from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtCore import Qt, QModelIndex, pyqtSlot, QByteArray, pyqtProperty


class SortFilterProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rowFilter = None
        self._columnFilter = None

    def roleNames(self):
        if not self.sourceModel():
            return {}

        return self.sourceModel().roleNames()

    @pyqtSlot(int, result='QVariantMap')
    def get(self, row):

        res = {}

        roleNames = self.roleNames()

        for targetRole in roleNames:
            roleName = roleNames[targetRole]
            res[roleName.decode()] = self.index(row, 0).data(targetRole)

        return res

    @pyqtSlot(int, "QJSValue")
    def set(self, row, jsValue):
        data = jsValue.toVariant()

        roleNames = self.roleNames()

        for key in data:
            try:
                targetRole = self._roleOfName(key)
                self.setData(self.index(row, 0), data[key], targetRole)
            except IndexError:
                pass

        self.submit()

    @pyqtSlot(int, 'QString', 'QVariant')
    def setProperty(self, row, roleName, value):
        targetRole = self._roleOfName(roleName)
        self.setData(self.index(row, 0), value, targetRole)

    @pyqtSlot("QJSValue")
    def append(self, jsValue):
        return self.insert(self.rowCount(), jsValue)
        data = jsValue.toVariant()

        roleNames = self.roleNames()

        nextRow = self.rowCount()

        self.insertRows(nextRow, 1)

        for key in data:
            try:
                targetRole = self._roleOfName(key)
                self.setData(self.index(nextRow, 0), data[key], targetRole)
            except IndexError:
                pass

    @pyqtSlot(int, "QJSValue")
    def insert(self, row, jsValue):

        data = jsValue.toVariant()

        roleNames = self.roleNames()

        self.insertRows(row, 1)

        for key in data:
            try:
                targetRole = self._roleOfName(key)
                self.setData(self.index(row, 0), data[key], targetRole)
            except IndexError:
                pass

    @pyqtSlot(int, int)
    def remove(self, row, count):
        self.removeRows(row, count)

    @pyqtProperty(int)
    def count(self):
        return self.rowCount()

    def _roleOfName(self, name):
        roleNames = self.roleNames()
        return [role for role, value in roleNames.items() if value.decode() == name][0]