

from copy import copy
from collections import OrderedDict
from abc import ABCMeta, abstractmethod

from ems.patterns.factory import Factory
from ems.util import snake_case, classproperty
from ems.inspection.util import Args
from ems.typehint import accepts
from ems.validation.abstract import ValidationError, MessageProvider
from ems.validation.abstract import RuleValidator as AbstractRuleValidator
from ems.validation.registry import Registry

class SimpleMessageProvider(MessageProvider):

    def __init__(self, messages=None):
        self.messages = messages if messages is not None else {}

    def buildMessage(self, validatorName, key, params, keynames):

        params['keyname'] = keynames[key] if key in keynames else key

        return self.message(validatorName, params).format(**params)

    def message(self, validatorName, params):

        typedKey = u"{0}.{1}".format(validatorName, self.typeSubKey(params['value']))

        if typedKey in self.messages:
            return self.messages[typedKey]

        try:
            return self.messages[validatorName]
        except KeyError:
            try:
                return self.messages['default']
            except KeyError:
                return 'This value is invalid'

    def typeSubKey(self, value):

        if isinstance(value, basestring):
            return 'string'
        if isinstance(value, (int,float)):
            return 'numeric'
        if hasattr(value, '__getitem__'):
            return 'collection'

        return ''

class RuleValidator(AbstractRuleValidator):

    requiredValidators = ['required']

    @accepts(Registry, MessageProvider)
    def __init__(self, registry, messageProvider):
        self._registry = registry
        self._messageProvider = messageProvider

    def validate(self, data, rules, keynames=None):

        keynames = {} if keynames is None else keynames

        parsedRules = self.parseRules(rules)

        messages = ValidationError()

        for key in parsedRules:

            ruleNames = [ruleName[0] for ruleName in parsedRules[key]]

            for ruleName, ruleParams in parsedRules[key]:

                isRequiredRule = self._isRequiredRule(ruleName)

                params = self.buildParams(key, data, ruleName, ruleParams)

                # If a rule is not required and value is empty, skip it
                if not isRequiredRule and self._isEmpty(params['value']):
                    continue

                validator = self._registry(ruleName)

                if '*args' in params:
                    varargs = params['*args']
                    del params['*args']
                    allParams = params.values() + varargs
                    if validator.validate(*allParams):
                        continue
                else:
                    if validator.validate(**params):
                        continue

                message = self._messageProvider.buildMessage(ruleName, key, params, keynames)
                messages.addMessage(key, message)

                # If a required rule fails, all others will be skipped
                if isRequiredRule:
                    break


        if len(messages):
            raise messages

        return True


    def buildParams(self, dataKey, data, ruleName, ruleParams):

        args = self._registry.buildArgs(ruleName)

        paramIndex = 0

        params = OrderedDict()

        for key in args.keys():

            if key == 'value':
                params[key] = data[dataKey]
            elif key == 'data':
                params[key] = data
            elif key == 'key':
                params[key] = dataKey
            else:
                try:
                    params[key] = ruleParams[paramIndex]
                    paramIndex += 1
                except IndexError:
                    pass

        if args.varargs is not None:
            params['*args'] = ruleParams

        return params

    def parseRules(self, rules):

        parsed = {}

        for key in rules:

            parsed[key] = []
            ruleChain = self.parseRuleChain(rules[key])

            requiredRules = []
            notRequiredRules = []

            for rule in ruleChain:
                ruleNameAndParams = self.splitIntoNameAndParams(rule)

                if self._isRequiredRule(ruleNameAndParams[0]):
                    requiredRules.append(ruleNameAndParams)
                else:
                    notRequiredRules.append(ruleNameAndParams)

            parsed[key] = requiredRules + notRequiredRules

        return parsed

    def parseRuleChain(self, rule):

        return rule.split('|') if isinstance(rule, basestring) else copy(rule)

        if isinstance(rule, basestring):
            return rule.split('|')
        return rule

    def _isRequiredRule(self, ruleName):
        return ruleName in self.requiredValidators

    def splitIntoNameAndParams(self, ruleChain):

        if isinstance(ruleChain, basestring):
            ruleChain = ruleChain.split(':')

        if len(ruleChain) == 1:
            return (ruleChain[0], [])

        if isinstance(ruleChain[1], basestring):
            return (ruleChain[0], ruleChain[1].split(','))

        return (ruleChain[0], ruleChain[1])

    def _isEmpty(self, value):

        if value is None:
            return True

        if isinstance(value, basestring) and (value.strip() == ''):
            return True

        if hasattr(value, '__len__') and len(value) == 0:
            return True

        return False