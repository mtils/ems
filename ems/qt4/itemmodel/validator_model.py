
from PyQt4.QtCore import pyqtSignal, Qt, QVariant, QString

from ems.typehint import accepts
from ems.validation.abstract import ValidationError
from ems.qt4 import ValidationStateRole, ValidationMessageRole, ColumnNameRole
from ems.qt4.util import variant_to_pyobject as py, cast_to_variant as variant
from ems.qt4.itemmodel.editable_proxymodel import EditableProxyModel

class ValidatorModel(EditableProxyModel):

    rulesChanged = pyqtSignal(dict)

    def __init__(self, validator=None, rules=None, parent=None):
        super(EditableProxyModel, self).__init__(parent)
        self._invalidData = {}
        self._validator = None
        self._rules = {}
        self._messages = {}

        if validator is not None:
            self.setValidator(validator)

        if rules is not None:
            self.setRules(rules)

    def data(self, proxyIndex, role=Qt.DisplayRole):

        if role not in (ValidationStateRole, ValidationMessageRole,
                        Qt.EditRole, Qt.DisplayRole):
            return super(ValidatorModel, self).data(proxyIndex, role)

        row = proxyIndex.row()
        column = proxyIndex.column()

        if role == ValidationStateRole:
            return variant(self.columnState(row, column))

        if role == ValidationMessageRole:
            return self.columnMessageVariant(row, column)

        try:
            return self._invalidData[row][column]
        except KeyError:
            return super(ValidatorModel, self).data(proxyIndex, role)

    def setData(self, index, value, role=Qt.EditRole):

        if role != Qt.EditRole:
            return super(ValidatorModel, self).setData(index, value, role)

        data = self._validationData(index, value)

        try:

            self.validator.validate(data, self._rules)

            result = super(ValidatorModel, self).setData(index, value)

            if result:
                self._flushInvalidData(index)
            return result

        except ValidationError as e:
            self._updateInvalidData(data, index, e.messages())
            return True

    def getValidator(self):
        return self._validator

    def setValidator(self, validator):
        self._validator = validator

    validator = property(getValidator, setValidator)

    def getRules(self):
        return self._rules

    def setRules(self, rules):
        if self._rules == rules:
            return
        self._rules = rules
        self.rulesChanged.emit(self._rules)

    rules = property(getRules, setRules)

    def __getitem__(self, row):

        data = {}

        for col in range(self.columnCount()):
            index = self.index(row, col)
            colName = py(index.data(ColumnNameRole))

            data[colName] = py(index.data(Qt.EditRole))

        return data

    def _validationData(self, changedIndex, value):

        row = changedIndex.row()
        data = self[row]

        if row in self._invalidData:
            for column in self._invalidData[row]:
                columnName = py(self.index(row, column).data(ColumnNameRole))
                data[columnName] = py(self._invalidData[row][column])

        changedColName = py(changedIndex.data(ColumnNameRole))
        data[changedColName] = py(value)

        return data

    def _updateInvalidData(self, data, changedIndex, messages):

        row = changedIndex.row()

        # Clear all messages of this row and rewrite em
        self._messages[row] = {}

        for key in messages:
            column = self.columnOfName(key)
            message = QString.fromUtf8(u"\n".join(messages[key]))
            self._messages[row][column] = variant(message)


        # Put ALL data into the temporary invalidData Store
        self._invalidData[row] = {}

        for key in data:
            column = self.columnOfName(key)
            self._invalidData[row][column] = variant(data[key])

    def _flushInvalidData(self, changedIndex):

        row = changedIndex.row()

        if not row in self._invalidData:
            self._clearInvalidData(row)
            return

        for column in self._invalidData[row]:
            if column == changedIndex.column():
                continue
            index = self.index(row, column)
            super(ValidatorModel, self).setData(index, self._invalidData[row][column])

        self._clearInvalidData(row)

    def _clearInvalidData(self, row):
        try:
            del self._invalidData[row]
        except KeyError:
            pass
        try:
            del self._messages[row]
        except KeyError:
            pass

    def columnState(self, row, column):
        if row not in self._messages:
            return True

        if column not in self._messages[row]:
            return True

        return False

    def columnMessageVariant(self, row, column):
        if row not in self._messages:
            return QVariant()

        if column not in self._messages[row]:
            return QVariant()

        return self._messages[row][column]

    def columnMessage(self, row, column):
        return self.columnMessageVariant().toString()