
import json
import os.path

from ems.app import Bootstrapper, absolute_path
from ems.inspection.util import classes
from ems.validation.abstract import Validator, MessageProvider
from ems.validation.registry import Registry
from ems.validation.rule_validator import RuleValidator, SimpleMessageProvider
from ems.validation.validators.base import *
from ems.validation.validators.filesystem import *

class AppPathNormalizer(PathNormalizer):

    def normalize(self, path):
        return absolute_path(path)

class ValidationBootstrapper(Bootstrapper):

    validatorModules = set([
        'ems.validation.validators.base',
        'ems.validation.validators.filesystem',
    ])

    messagesFile = os.path.join('resources','lang','de','validation.json')

    def bootstrap(self, app):
        self.app = app
        app.share(Registry, self.createRegistry)
        app.share(MessageProvider, self.createMessageProvider)
        app.share(PathNormalizer, self.createPathNormalizer)

    def createRegistry(self):
        registry = Registry(self.app)
        self.addValidatorClasses(registry)
        return registry

    def createPathNormalizer(self):
        return AppPathNormalizer()

    def addValidatorClasses(self, registry):
        for module in self.validatorModules:
            for cls in self.findModuleValidatorClasses(module):
                registry += cls

    def createMessageProvider(self):

        with open(self.messagesFilePath()) as jsonFile:
            messages = json.load(jsonFile)

        return SimpleMessageProvider(messages)

    def messagesFilePath(self):
        return os.path.join(self.app.appPath, self.messagesFile)

    @classmethod
    def findModuleValidatorClasses(cls, moduleName):

        validatorClasses = []

        for clazz in classes(moduleName):
            if issubclass(clazz, Validator):
                validatorClasses.append(clazz)

        return validatorClasses
