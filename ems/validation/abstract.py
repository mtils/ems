
from abc import ABCMeta, abstractmethod


class Validator(object):
    """
    A Validator is the smallest unit of validation. A Validator validates one
    value or compares it to another value. 
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, value):
        """
        Validate value and return true or false. Dont throw exceptions if the
        value is invalid. If you need more parameters just add them to this
        method

        :returns: The validation result
        :rtype: bool
        """
        raise NotImplementedError()

class ValidationError(Exception):
    """
    A ValidationError is thrown by RuleValidators and ResourceValidators. It
    contains the messages.
    """

    def __init__(self, messages=None, key=None, message=None):

        super(ValidationError, self).__init__('')

        self._messages = messages if messages is not None else {}

    def messages(self, key=None):
        if key is None:
            return self._messages
        return self._messages[key]

    def message(self, key):
        try:
            return self._messages[key]
        except KeyError:
            return ''

    def hasMessage(self, key):
        return key in self._messages

    def addMessage(self, key, message):
        if key not in self._messages:
            self._messages[key] = []
        self._messages[key].append(message)

    def __len__(self):
        return len(self._messages)


class MessageProvider(object):
    """
    A MessageProvider creates the validation messages for a given error. The
    Validator does not have to know how to build its messages. It just have to
    return true or false
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def buildMessage(self, validatorName, params, keynames):
        """
        Build the message for validator with name validatorName (e.g. required)
        params will be all params passed to the validate() method of this
        validator. The validator args are inspected and can then be used in
        messages (translations)

        :rtype: str
        :returns: The parsed message
        """
        pass

class RuleValidator(object):
    """
    A RuleValidator is a helper class to easily validate dicts of data. You can
    pass a dict of rules like this:

    rules = {
        'name': 'required|min:3|max:255',
        'age':  'numeric|min:1|max:125'
    }

    and validate a dict of data against this rules. As a rule of thumb you
    only need only one RuleValidator in your application because all data is passed
    threw its validate method

    In opposite to Validator this class throws a ValidationError if validation
    fails
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, data, rules, keynames=None):
        """
        Validate data against rules. For better readability you can pass a dict
        of keynames to translate the keyname in error messages into a readable
        one
        THROW a ValidationException if validation fails

        :rtype: bool
        :returns: Always true
        :raises: ValidationError
        """
        raise NotImplementedError()

def ResourceValidator(object):
    """
    A resource validator validates the data you want to assign to a
    resource (model). The resource validator must throw an exception on
    failure.

    :returns: bool
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, data, resource=None):
        """
        A resource validator validates the data you want to assign to a
        resource (model). The resource validator must throw an exception on
        failure. The return type should be true.
        If resource is None, the validate() method assumes the model will be
        created, if one is passed it assumes it exists and this is an update
        operation.

        :rtype: bool
        :returns: Always true
        :raises: ValidationError
        """
        pass