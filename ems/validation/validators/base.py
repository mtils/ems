
import re, socket

from ems.validation.abstract import Validator

class RequiredValidator(Validator):

    def validate(self, value):

        if value is None:
            return False

        if isinstance(value, basestring):
            return bool(value.strip())

        return bool(value)

class FilledValidator(Validator):

    def validate(self, value, key, data):
        return key in data

class SameValidator(Validator):

    def validate(self, value, otherKey, data):

        try:
            return value == data[otherKey]
        except KeyError:
            return False


class ConfirmedValidator(Validator):

    def __init__(self, sameValidator=None):
        self.same = SameValidator() if sameValidator is None else sameValidator

    def validate(self, value, key, data):
        return self.same.validate(value, '{0}_confirmation'.format(key), data)

class DifferentValidator(Validator):

    def validate(self, value, otherKey, data):

        try:
            return value != data[otherKey]
        except KeyError:
            return True

class AcceptedValidator(Validator):

    def __init__(self):
        self.required = RequiredValidator()

    def validate(self, value):

        if not self.required.validate(value):
            return False

        trueValues = ('yes', 'on', '1', 1, True, 'true', 1.0)

        return value in trueValues

class DictValidator(Validator):

    def validate(self, value):
        return hasattr(value, '__getitem__')

class BoolValidator(Validator):

    def validate(self, value):
        acceptable = [True, False, 0, 1, '0', '1']
        return value in acceptable

class IntegerValidator(Validator):

    def validate(self, value):

        try:
            num = int(value)
            return True
        except ValueError:
            return False

class NumericValidator(Validator):

    def validate(self, value):

        try:
            num = float(value)
            return True
        except (ValueError, TypeError):
            return False

class StringValidator(Validator):

    def validate(self, value):
        return isinstance(value, basestring)


class DigitsValidator(Validator):

    def __init__(self):
        self.numeric = NumericValidator()

    def validate(self, value, digits):

        if not self.numeric.validate(value):
            return False

        return len(str(value)) == int(digits)

        try:
            num = float(value)
            return True
        except ValueError:
            return False

class SizeValidator(Validator):

    def validate(self, value, size):
        size = int(size)
        return len(value) == size

class BetweenValidator(Validator):

    def validate(self, value, min_, max_):

        if value is None:
            return False

        min_ = float(min_)
        max_ = float(max_)

        try:
            value = float(value)
        except ValueError:
            return False

        return ((value >= min_) and (value <= max_))

class MinValidator(Validator):

    def validate(self, value, min_):

        if value is None:
            return False

        min_ = float(min_)

        try:
            value = float(value)
        except (ValueError, TypeError):
            try:
                value = len(value)
            except (ValueError, TypeError):
                return False

        return value >= min_

class MaxValidator(Validator):

    def validate(self, value, max_):

        if value is None:
            return False

        max_ = float(max_)

        try:
            value = float(value)
        except (ValueError, TypeError):
            try:
                value = len(value)
            except (ValueError, TypeError):
                return False

        return value <= max_

class InValidator(Validator):

    def validate(self, value, *args):
        return value in args

class NotInValidator(Validator):

    def __init__(self):
        self.inValidator = InValidator()

    def validate(self, value, *args):
        return not self.inValidator.validate(value, *args)

class IpValidator(Validator):

    def validate(self, value):

        try:
            socket.inet_aton(value)
            return True
        except socket.error:
            return False

class EmailValidator(Validator):

    def validate(self, value):
        return re.match("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$", value)

class UrlValidator(Validator):

    def __init__(self):
        self.regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    def validate(self, value):
        return self.regex.match(value)

