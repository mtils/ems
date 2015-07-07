
from __future__ import print_function

import sys
import inspect
from collections import OrderedDict


class Args(object):

    def __init__(self, function, skipSelfAndCls=True):
        self._function = function
        self._skipSelfAndCls = skipSelfAndCls
        self._names = None
        self._argspec = None
        self._defaults = None

    def __iter__(self):
        return iter(self.names)

    def __contains__(self, key):
        return key in self.names

    @property
    def names(self):
        if self._names is not None:
            return self._names

        if self._shouldSkipFirst():
            self._names = self.argspec.args[1:]
        else:
            self._names = self.argspec.args

        return self._names

    @property
    def argspec(self):
        if self._argspec is None:
            self._argspec = inspect.getargspec(self._function)
        return self._argspec

    @property
    def skipSelfAndCls(self):
        return self._skipSelfAndCls

    @skipSelfAndCls.setter
    def skipSelfAndCls(self, skip):
        self._skipSelfAndCls = skip
        self._names = None

    @property
    def defaults(self):
        if self._defaults is None:
            self._defaults = dict(
                zip(
                    reversed(self.argspec.args),
                    reversed(self.argspec.defaults if self.argspec.defaults else ())
                )
            )
        return self._defaults

    def hasDefault(self, key):
        return key in self.defaults.keys()

    def isRequired(self, key):
        return not self.hasDefault(key)

    def default(self, key):
        return self.defaults[key]

    def _shouldSkipFirst(self):

        if not self.skipSelfAndCls:
            return False

        return inspect.ismethod(self._function)

    def buildKwargs(self):
        args = OrderedDict()
        args.varargs = None
        for key in self.names:
            args[key] = self.default(key) if self.hasDefault(key) else None

        if self.argspec.varargs:
            args.varargs = []
        return args

def classes(moduleName):
    moduleClasses = []
    for name, obj in inspect.getmembers(sys.modules[moduleName]):
        if inspect.isclass(obj):
            moduleClasses.append(obj)
    return moduleClasses

if __name__ == '__main__':

    def test(a, b, c=None):
        pass

    class Test(object):
        def test(self, a, b, c=None):
            pass
        @classmethod
        def classTest(cls, a, b, c=None):
            pass
        @staticmethod
        def staticTest(a, b, c=None):
            pass

    funcArgs = Args(test)
    for key in funcArgs:
        print('funcArgs.{0}'.format(key),':', funcArgs.default(key) if funcArgs.hasDefault(key) else 'mandatory')

    instanceArgs = Args(Test.test)
    for key in instanceArgs:
        print('instanceArgs.{0}'.format(key),':', instanceArgs.default(key) if instanceArgs.hasDefault(key) else 'mandatory')

    t = Test()

    instanceArgs = Args(t.test)
    for key in instanceArgs:
        print('objectArgs.{0}'.format(key),':', instanceArgs.default(key) if instanceArgs.hasDefault(key) else 'mandatory')

    classArgs = Args(Test.classTest)
    for key in classArgs:
        print('classArgs.{0}'.format(key),':', classArgs.default(key) if classArgs.hasDefault(key) else 'mandatory')

    staticArgs = Args(Test.classTest)
    for key in staticArgs:
        print('staticArgs.{0}'.format(key),':', staticArgs.default(key) if staticArgs.hasDefault(key) else 'mandatory')