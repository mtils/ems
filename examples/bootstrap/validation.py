
from ems.app import Bootstrapper
from ems.validation.validator import AbstractRuleValidator
from ems.validation.validator import RuleValidator
from ems.validation.validator import Registry
from ems.validation.validators.base import RequiredValidator
from ems.validation.validators.base import BetweenValidator

class ValidationBootstrapper(Bootstrapper):

    def bootstrap(self, app):
        self.app = app
        app.bind(Registry, self.createRegistry)

    def createRegistry(self):

        registry = Registry(self.app)
        
        
        