

from abc import ABCMeta, abstractmethod

from ems.util import snake_case


class Validator(object):

    __metaclass__ = ABCMeta

    baseLangKey = 'validation'

    @abstractmethod
    def validate(self, key, value, params={}, allData={}):
        raise NotImplementedError()

    @property
    def langKey(self):
        classKey = snake_case(self.__class__.__name__)[0:-10] # cut _validator
        return u".".join((self.baseLangKey, classKey))


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


class DictValidator(Validator):

    def __init__(self):
        self._validators = {}

    def validate(self, key, data, params={}, allData={}):

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
