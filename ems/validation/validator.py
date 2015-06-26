

from abc import ABCMeta, abstractmethod

from ems.util import snake_case, classproperty
from ems.inspection.util import Args


class Validator(object):

    __metaclass__ = ABCMeta

    baseLangKey = 'validation'

    @abstractmethod
    def validate(self, value):
        raise NotImplementedError()

    @property
    def langKey(self):
        return u".".join((self.baseLangKey, self.name))

    def _createError(self, message, params):
        error = ValidationError()

    @property
    def name(self):
        return snake_case(self.__class__.__name__)[0:-10] # cut _validator


class ValidationError(Exception):

    def __init__(self, messages=None, key=None, message=None):

        super(ValidationError, self).__init__('')

        if isinstance(messages, dict):
            self._messages = messages
        elif isinstance(messages, basestring):
            self._messages = {0:messages}
        elif isinstance(messages, list):
            self._messages = {0:u'\n'.join(messages)}

    @property
    def messages(self):
        return self._messages.values()

    @property
    def messageDict(self):
        return self._messages

    def message(self, fieldName):
        try:
            return self._messages[fieldName]
        except KeyError:
            return ''

    def hasMessage(self, fieldName):
        return fieldName in self._messages


class RuleValidator(object):

    def __init__(self, registry):
        self._validators = {}
        self._registry = registry

    def validate(self, data, rules={}):

        for key in rules:
            self._validateRule(rules, key, data)

        for fieldName in self._validators:

            validator = self._validators[fieldName]

            messages = {}

            try:
                value = None if not fieldName in data else data[fieldName]
                validator.validate(data[fieldName])
            except ValidationError as e:
                messages[fieldName] = e.messages

            if len(messages):
                raise ValidationError(messages)

    def addValidator(self, fieldName, validator):
        if not fieldName in self._validators:
            self._validators[fieldName] = []
        self._validators[fieldName].append(validator)

    def _validateRule(self, rules, key, data):
        #if not key
        pass

    @classproperty
    @classmethod
    def supportedParams(self):
        return self._validators.keys()

class Registry(object):

    def __init__(self):
        self._validatorClasses = {}
        self._validators = {}
        self._validatorArgs = {}

    def __iadd__(self, validator):
        self._validatorClasses[validator.name] = validator
        return self

    def __isub__(self, validator):
        if validator.name in self._validatorClasses:
            del self._validatorClasses[validator.name]
        return self

    def __iter__(self):
        yield self._validatorClasses

    def __len__(self):
        return len(self._validatorClasses)

    def __contains__(self, item):

        if not isinstance(item, Validator):
            return item in self._validatorClasses

        for validator in self._validatorClasses:
            if validator is item:
                return True

        return False

    def __call__(self, name):

        if name in self._validators:
            return self._validators[name]

        self._validators[name] = self._validatorClasses[name]()

        return self._validators[name]

    def buildArgs(self, name):
        if not name in self._validatorArgs:
            self._validatorArgs[name] = Args(self._validatorClasses[name].validate)
        return self._validatorArgs[name].buildKwargs()