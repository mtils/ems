
import unittest

from ems.validation.validator import Registry, Validator, RuleValidator
from ems.validation.validator import SimpleMessageProvider, ValidationError
from ems.patterns.factory import DummyFactory

class RegistryTest(unittest.TestCase):

    def test_name_returns_snake_cased_name(self):
        registry = self.newRegistry()

        self.assertEquals('exists', registry.validatorName(ExistsValidator))
        self.assertEquals('does_not_exist', registry.validatorName(DoesNotExistValidator))

    def test_name_works_with_instances_and_types(self):
        registry = self.newRegistry()

        self.assertEquals('exists', registry.validatorName(ExistsValidator))
        self.assertEquals('does_not_exist', registry.validatorName(DoesNotExistValidator))

        existsInstance = ExistsValidator()
        doesNotExistInstance = DoesNotExistValidator()

        self.assertEquals('exists', registry.validatorName(existsInstance))
        self.assertEquals('does_not_exist', registry.validatorName(doesNotExistInstance))

    def test_add_and_contains_validator(self):

        registry = self.newRegistry()

        registry += ExistsValidator
        registry += DoesNotExistValidator

        self.assertTrue(ExistsValidator in registry)
        self.assertTrue(DoesNotExistValidator in registry)
        self.assertTrue('exists' in registry)
        self.assertTrue('does_not_exist' in registry)

        self.assertEquals(2, len(registry))

    def test_iter_acts_as_dict(self):

        registry = self.newRegistry()

        registry += ExistsValidator
        registry += DoesNotExistValidator

        resultClasses = {
            'exists' : ExistsValidator,
            'does_not_exist': DoesNotExistValidator
        }

        for name in registry:
            self.assertIs(resultClasses[name], registry[name])


    def test_call_creates_validator(self):

        registry = self.newRegistry()

        registry += ExistsValidator
        registry += DoesNotExistValidator

        self.assertIsInstance(registry('exists'), ExistsValidator)
        self.assertIsInstance(registry('does_not_exist'), DoesNotExistValidator)

    def test_always_returns_same_instance(self):

        registry = self.newRegistry()

        registry += ExistsValidator
        registry += DoesNotExistValidator

        existsInstance = registry('exists')
        doesNotExistInstance = registry('does_not_exist')

        self.assertIs(existsInstance, registry('exists'))
        self.assertIs(doesNotExistInstance, registry('does_not_exist'))

    def test_magic_overload_of_getattribute(self):

        registry = self.newRegistry()

        registry += ExistsValidator
        registry += DoesNotExistValidator
        registry += MinMaxValidator

        self.assertFalse(registry.exists('bar'))
        self.assertTrue(registry.exists('foo'))

        self.assertTrue(registry.does_not_exist('bar', {}))
        self.assertFalse(registry.does_not_exist('foo', {}))

        self.assertTrue(registry.min_max(2, 1, 3))
        self.assertFalse(registry.min_max(2, 3, 15))

    def test_buildArgs_returns_correct_params(self):

        registry = self.newRegistry()

        registry += ExistsValidator
        registry += DoesNotExistValidator
        registry += MinMaxValidator

        existsArgs = registry.buildArgs('exists')
        self.assertEquals(['value'], existsArgs.keys())
        self.assertIs(None, existsArgs['value'])

        doesNotExistArgs = registry.buildArgs('does_not_exist')

        self.assertEquals(['value','data'], doesNotExistArgs.keys())
        self.assertIs(None, doesNotExistArgs['value'])
        self.assertEquals({}, doesNotExistArgs['data'])

        minMaxArgs = registry.buildArgs('min_max')

        self.assertEquals(['value','min_', 'max_'], minMaxArgs.keys())

        self.assertIs(None, minMaxArgs['value'])
        self.assertIs(None, minMaxArgs['min_'])
        self.assertIs(None, minMaxArgs['max_'])

    def newRegistry(self, factory=None):
        factory = factory if factory is not None else DummyFactory()
        return Registry(factory)

class RuleValidatorTest(unittest.TestCase):


    def test_parse_rulechain_parses_to_list(self):

        validator = self.newRuleValidator()

        rule = 'exists'
        rule2 = 'exists|numeric|min:3'
        rule3 = ['exact','between:1,5','not:43']

        self.assertEquals(['exists'], validator.parseRuleChain(rule))
        self.assertEquals(['exists','numeric','min:3'], validator.parseRuleChain(rule2))
        self.assertEquals(rule3, validator.parseRuleChain(rule3))

    def test_splitIntoNameAndParams_always_return_tuple(self):

        validator = self.newRuleValidator()

        rule = 'exists'
        rule3 = ['exact','between:1,5','not:43']

        self.assertEquals(('exists', []), validator.splitIntoNameAndParams(rule))

        self.assertEquals(('exact', []), validator.splitIntoNameAndParams(rule3[0]))

        self.assertEquals(('between', ['1','5']), validator.splitIntoNameAndParams(rule3[1]))

        self.assertEquals(('not', ['43']), validator.splitIntoNameAndParams(rule3[2]))

    def test_rule_parsing(self):

        validator = self.newRuleValidator()

        rules = {
            'agb_confirmed': 'accepted',
            'age'          : 'numeric|between:18,132',
            'birthday'     : 'pastdate',
            'category_id'  : 'numeric|exists:categories,id'
        }

        parsed = {
            'agb_confirmed': [('accepted',[])],
            'age'          : [('numeric',[]),('between',['18','132'])],
            'birthday'     : [('pastdate',[])],
            'category_id'  : [('numeric',[]),('exists',['categories','id'])]
        }

        self.assertEquals(parsed, validator.parseRules(rules))
        self.assertEquals(parsed, validator.parseRules(parsed))


    def test_passing_validation(self):

        registry = self.newRegistry()

        registry += ExistsValidator
        registry += DoesNotExistValidator
        registry += MinMaxValidator
        registry += NumericValidator

        validator = self.newRuleValidator(registry)

        rules = {
            'name'  : 'exists',
            'street': 'does_not_exist',
            'age'   : 'numeric|min_max:18,132'
        }

        data = {
            'name' : 'foo',
            'street': 'bar',
            'age' : '35'
        }

        self.assertTrue(validator.validate(data, rules))

    def test_failing_validation_raises_error(self):

        registry = self.newRegistry()

        registry += ExistsValidator
        registry += DoesNotExistValidator
        registry += MinMaxValidator
        registry += NumericValidator

        validator = self.newRuleValidator(registry)

        rules = {
            'name'  : 'exists',
            'street': 'does_not_exist',
            'age'   : 'numeric|min_max:18,132'
        }

        data = {
            'name' : 'foi',
            'street': 'foo',
            'age' : 'Hans'
        }

        self.assertRaises(ValidationError, validator.validate, data, rules)

        try:
            validator.validate(data, rules)
        except ValidationError as e:
            messages = e.messages()

        tpls = self.newMessageProvider().messages

        self.assertEquals(messages['name'], [tpls['exists']])
        self.assertEquals(messages['street'], [tpls['does_not_exist']])
        self.assertEquals(messages['age'], [tpls['numeric'],tpls['min_max']])

    def newRuleValidator(self, registry=None, messageProvider=None):

        registry = registry if registry is not None else self.newRegistry()
        messageProvider = messageProvider if messageProvider is not None else self.newMessageProvider()

        return RuleValidator(registry, messageProvider)

    def newRegistry(self, factory=None):
        factory = factory if factory is not None else DummyFactory()
        return Registry(factory)

    def newMessageProvider(self):

        messages = {
            'exists': 'The value has to be foo',
            'does_not_exist': 'The value shouldt be foo',
            'min_max': 'The value is not in allowed range',
            'numeric': 'The value has to be numeric'
        }

        return SimpleMessageProvider(messages)

class ExistsValidator(Validator):

    def validate(self, value):
        return value == 'foo'

class DoesNotExistValidator(Validator):

    def validate(self, value, data={}):
        return value != 'foo'

class MinMaxValidator(Validator):

    def validate(self, value, min_, max_):


        try:
            value = float(value)
        except ValueError:
            return False

        min_ = float(min_)
        max_ = float(max_)

        if value < min_:
            return False
        if value > max_:
            return False
        return True

class NumericValidator(Validator):

    def validate(self, value):

        try:
            floatValue = float(value)
            return True
        except ValueError:
            return False

if __name__ == '__main__':
    unittest.main()