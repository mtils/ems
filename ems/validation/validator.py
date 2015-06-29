

from abc import ABCMeta, abstractmethod

from ems.patterns.factory import Factory
from ems.util import snake_case, classproperty
from ems.inspection.util import Args
from ems.typehint import accepts


class Validator(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, value):
        raise NotImplementedError()

class ValidationError(Exception):

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

    __metaclass__ = ABCMeta

    @abstractmethod
    def buildMessage(self, validatorName, params, keynames):
        pass

class SimpleMessageProvider(MessageProvider):

    def __init__(self, messages=None):
        self.messages = messages if messages is not None else {}

    def buildMessage(self, validatorName, key, params, keynames):

        message = self.messages[validatorName]

        params['keyname'] = keynames[key] if key in keynames else key

        return message.format(params)

class Registry(object):

    @accepts(Factory)
    def __init__(self, validatorFactory):
        self._validatorFactory = validatorFactory
        self._validatorClasses = {}
        self._validators = {}
        self._validatorArgs = {}

    def __iadd__(self, validatorClass):
        self._validatorClasses[self.validatorName(validatorClass)] = validatorClass
        return self

    def __isub__(self, validatorClass):
        name = self.validatorName(validatorClass)
        if name in self._validatorClasses:
            del self._validatorClasses[name]
        return self

    def __getitem__(self, key):
        return self._validatorClasses[key]

    def __iter__(self):
        return iter(self._validatorClasses)

    def __len__(self):
        return len(self._validatorClasses)

    def __contains__(self, item):

        if isinstance(item, basestring):
            return item in self._validatorClasses

        cls = self._class(item)

        for name in self._validatorClasses:
            if self._validatorClasses[name] is cls:
                return True

        return False

    def __call__(self, name):

        if name in self._validators:
            return self._validators[name]

        self._validators[name] = self._validatorFactory.make(self._validatorClasses[name])

        return self._validators[name]

    def __getattr__(self, attribute):
        return self.__call__(attribute).validate

    def buildArgs(self, name):
        if not name in self._validatorArgs:
            self._validatorArgs[name] = Args(self._validatorClasses[name].validate)
        return self._validatorArgs[name].buildKwargs()

    def validatorName(self, validator):
        return snake_case(self._class(validator).__name__)[0:-10] # cut _validator

    def _class(self, validator):
        return validator if isinstance(validator, type) else validator.__class__

class AbstractRuleValidator(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, data, rules, keynames=None):
        raise NotImplementedError()

class RuleValidator(AbstractRuleValidator):

    @accepts(Registry, MessageProvider)
    def __init__(self, registry, messageProvider):
        self._validators = {}
        self._registry = registry
        self._messageProvider = messageProvider

    def validate(self, data, rules, keynames=None):

        keynames = {} if keynames is None else keynames

        parsedRules = self.parseRules(rules)

        messages = ValidationError()

        for key in parsedRules:
            for ruleName, ruleParams in parsedRules[key]:
                params = self.buildParams(key, data, ruleName, ruleParams)
                validator = self._registry(ruleName)

                if not validator.validate(**params):
                    message = self._messageProvider.buildMessage(ruleName, key, params, keynames)
                    messages.addMessage(key, message)


        if len(messages):
            raise messages

        return True


    def buildParams(self, dataKey, data, ruleName, ruleParams):

        args = self._registry.buildArgs(ruleName)

        paramIndex = 0

        params = {}

        for key in args.keys():

            if key == 'value':
                params[key] = data[dataKey]
            elif key == 'data':
                params[key] = data
            elif key == 'key':
                params[key] = dataKey
            else:
                params[key] = ruleParams[paramIndex]
                paramIndex += 1

        return params

    def parseRules(self, rules):

        parsed = {}

        for key in rules:

            parsed[key] = []
            ruleChain = self.parseRuleChain(rules[key])
            for rule in ruleChain:
                parsed[key].append(self.splitIntoNameAndParams(rule))

        return parsed

    def parseRuleChain(self, rule):
        if isinstance(rule, basestring):
            return rule.split('|')
        return rule

    def splitIntoNameAndParams(self, ruleChain):

        if isinstance(ruleChain, basestring):
            ruleChain = ruleChain.split(':')

        if len(ruleChain) == 1:
            return (ruleChain[0], [])

        if isinstance(ruleChain[1], basestring):
            return (ruleChain[0], ruleChain[1].split(','))

        return (ruleChain[0], ruleChain[1])
