
from __future__ import print_function

from types import FunctionType, MethodType
import inspect

class _MethodDecoratorAdaptor(object):

    def __init__(self, decorator, func):
        self.decorator = decorator
        self.func = func

    def __call__(self, *args, **kwargs):
        f = self.decorator(self.func)(*args, **kwargs)
        #f.func_dict['typehinted'] = True
        #f.func_dict['typehint'] = self.decorator
        return f

    def __get__(self, instance, owner):
        f = self.decorator(self.func.__get__(instance, owner))
        #f.func_dict['typehinted'] = True
        #f.func_dict['typehint'] = self.decorator
        return f

def auto_adapt_to_methods(decorator):
    """Allows you to use the same decorator on methods and functions,
    hiding the self argument from the decorator."""
    def adapt(func):
        return _MethodDecoratorAdaptor(decorator, func)
    return adapt

class NonDefaultArg:
    pass

class MethodWrapper(object):

    def __init__(self, defInfo, types, kwtypes):
        self.defInfo = defInfo
        self.types = types
        self.kwtypes = kwtypes
        self._checkPassedTypes()

    def __call__(self, *args, **kwargs):

        for i, arg in enumerate(args):

            try:

                #print(self.defInfo['argnames'][i], "type:", type(arg), " defaults[{0}]:".format(i), self.defInfo['defaults'][i], "arg[{0}]:".format(i), arg)
                if isinstance(arg, self.types[i]):
                    continue



                if self.defInfo['defaults'][i] is NonDefaultArg or arg != self.defInfo['defaults'][i]:
                    msg_args = (i, self.defInfo['argnames'][i], self.defInfo['name'], self.types[i], arg.__class__)
                    raise TypeError("Argument #{0}:{1} of {2}() has to be instanceof {3}, not {4}".format(*msg_args))

            except IndexError: # Happens when not all args are hinted
                pass

        return self.defInfo['function'](*args, **kwargs)

    def _checkPassedTypes(self):
        if self.types and self.kwtypes:
            raise SyntaxError("accepts accept only args or kwargs, not both")
        if self.kwtypes:
                raise NotImplementedError("kwargs currently not supported")


def buildDefInfo(func):

    argnames, varargs, keywords, defaults = inspect.getargspec(func)
    offset = 1 if inspect.ismethod(func) else 0

    if defaults:
        defaultsList = [NonDefaultArg] * (len(argnames) - len(defaults)) + list(defaults)
    else:
        defaultsList = [NonDefaultArg] * len(argnames)

    argnames = argnames[offset:]
    defaultsList = defaultsList[offset:]

    return {
        'function': func,
        'name': func.__name__,
        'argnames': argnames,
        'defaults': defaultsList
    }

def accepts(*types, **kwtypes):
    @auto_adapt_to_methods
    def wrapper(func):
        return MethodWrapper(buildDefInfo(func), types, kwtypes)
    return wrapper

if __name__ == '__main__':

    @accepts(float, float)
    def add(a,b,c=None):
        return a + b

    class Calc(object):
        @accepts(float, float)
        def add(self, a, b, c=None):
            return a + b

        @accepts(float, float)
        @staticmethod
        def add_static(a, b, c=None):
            return a + b

        @accepts(float, float)
        @classmethod
        def add_class(cls, a, b, c=None):
            return a + b

        @accepts(float, (float,int), float, float)
        def add_default(self, a, b, c=None, d=None):
            return a + b

    print('add(3,4):',add(3.0,4.0), type(add))
    c = Calc()
    print('c.add(3,4):',c.add(3.0,4.0), type(Calc.add), type(c.add))
    print('Calc.add_static(3,4):',Calc.add_static(3.0,4.0), type(Calc.add_static), type(c.add_static))
    print('Calc.add_class(3,4):',Calc.add_class(3.0,4.0), type(Calc.add_class), type(c.add_class))
    print('Calc.add_default(3,4):',c.add_default(3.0,4, None))
