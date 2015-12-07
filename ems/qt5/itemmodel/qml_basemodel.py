
from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, QAbstractTableModel
from PyQt5.QtQml import QJSValue
#from PyQt5.QtCore import QString, QVariant

from ems.qt.identifiers import ItemData, RoleOffset

class QmlTableModel(QAbstractTableModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._roleNames = None

    def roleNames(self):

        if self._roleNames is not None:
            return self._roleNames

        self._roleNames = {}

        for column in range(self.columnCount()):
            targetRole = RoleOffset + column
            columnName = self._nameOfColumn(column)
            columnName = columnName if columnName != 'id' else 'ID'
            self._roleNames[targetRole] = bytearray(columnName, encoding='ascii')

        return self._roleNames

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

    @pyqtSlot(int, "QJSValue")
    def insert(self, row, jsValue):

        data = jsValue if isinstance(jsValue, dict) else jsValue.toVariant()
        roleNames = self.roleNames()

        self.insertRows(row, 1)

        if data is None:
            return

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
        try:
            return [role for role, value in roleNames.items() if value.decode() == name][0]
        except IndexError:
            raise KeyError("cannot find roleOfName {0}".format(name))