
from ems.validation.validator import Validator, ValidationError

class RequiredValidator(Validator):

    def validate(self, key, value, params={}, allData={}):

        if value is None:
            raise ValidationError


class BetweenValidator(Validator):

    supportedParams = ('min', 'max')

    def validate(self, key, value, params={}, allData={}):

        if value is None:
            raise ValidationError

        value = float(value)

        if value < params['min'] or value > params['max']:
            raise ValidationError