

from ems.typehint import accepts
from ems.validation.validator import AbstractRuleValidator
from ems.qt4 import validationStateRole, validationMessageRole
from ems.qt4.itemmodel.editable_proxymodel import EditableProxyModel

class ValidatorModel(EditableProxyModel):


    def __init__(self, validator=None, parent=None):
        super(EditableProxyModel, self).__init__(parent)
        self._invalidData = {}
        self._validator = None

        if validator is not None:
            self.setValidator(validator)

    def getValidator(self):
        return self._validator

    @accepts(AbstractRuleValidator)
    def setValidator(self, validator):
        self._validator = validator

    validator = property(getValidator, setValidator)

    