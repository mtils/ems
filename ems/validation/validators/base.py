
from ems.validation.validator import Validator, ValidationError

class RequiredValidator(Validator):

    def validate(self, key, value, params={}, allData={}):

        if value is None:
            raise ValidationError