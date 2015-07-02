
from ems.typehint import accepts
from ems.patterns.factory import Factory
from ems.util import snake_case
from ems.inspection.util import Args

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