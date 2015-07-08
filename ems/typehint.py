
from __future__ import print_function

class _MethodDecoratorAdaptor(object):

    def __init__(self, decorator, func):
        self.decorator = decorator
        self.func = func

    def __call__(self, *args, **kwargs):
        f = self.decorator(self.func)(*args, **kwargs)
        f.func_dict['typehinted'] = True
        f.func_dict['typehint'] = self.decorator
        return f

    def __get__(self, instance, owner):
        f = self.decorator(self.func.__get__(instance, owner))
        f.func_dict['typehinted'] = True
        f.func_dict['typehint'] = self.decorator
        return f

def auto_adapt_to_methods(decorator):
    """Allows you to use the same decorator on methods and functions,
    hiding the self argument from the decorator."""
    def adapt(func):
        return _MethodDecoratorAdaptor(decorator, func)
    return adapt

class NonDefaultArg:
    pass

def accepts(*types, **kwtypes):
    @auto_adapt_to_methods
    def wrapper(func):
        def wrapped(*args, **kwargs):
            if types and kwtypes:
                raise SyntaxError("accepts accept only args or kwargs, not both")

            if kwtypes:
                raise NotImplementedError("kwargs currently not supported")

            if hasattr(func, 'im_func'):
                is_method = True
                fdef = func.im_func
                argnames = fdef.func_code.co_varnames[1:]
            else:
                is_method = False
                fdef = func
                argnames = fdef.func_code.co_varnames[:]

            if fdef.func_defaults:
                defaults = [NonDefaultArg] * (len(argnames) - len(fdef.func_defaults)) + list(fdef.func_defaults)
            else:
                defaults = [NonDefaultArg] * len(argnames)

            for i,arg in enumerate(args):
                try:
                    if not isinstance(arg, types[i]):
                        if defaults[i] is NonDefaultArg or arg != defaults[i]:
                            msg_args = (i, argnames[i],fdef.func_name, types[i], arg.__class__)
                            raise TypeError("Argument #{0}:{1} of {2}() has to be instanceof {3}, not {4}".format(*msg_args))

                except IndexError: # Happens when not all args are hinted
                    pass

            return func(*args, **kwargs)

        wrapped.func_dict['types'] = types
        wrapped.func_dict['kwtypes'] = kwtypes

        return wrapped

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

    print('add(3,4):',add(3.0,4.0))
    c = Calc()
    print('c.add(3,4):',c.add(3.0,4.0))
    print('Calc.add_static(3,4):',Calc.add_static(3.0,4.0))
    print('Calc.add_class(3,4):',Calc.add_class(3.0,4.0))
    print('Calc.add_default(3,4):',c.add_default(3.0,4, None))