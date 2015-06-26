
from __future__ import print_function

class Facade(type):

    _roots = {}

    def __getattribute__(cls, method):

        if method == 'facade_root':
            return Facade._roots[cls]

        if method in ('__metaclass__','__forcetype__'):
            return type.__getattribute__(cls, method)

        try:
            return getattr(Facade._roots[cls], method)
        except KeyError:
            return type.__getattribute__(cls, method)

        raise AttributeError("Method {0} not found".format(method))

    @property
    def facade_root(cls):
        return Facade._roots[cls]

    @facade_root.setter
    def facade_root(cls, root):
        if hasattr(cls,'__forcetype__') and \
            not isinstance(root, cls.__forcetype__):
            raise TypeError("Facade Root of {0} has to be instanceof {1}".format(cls, cls.__forcetype__))
        Facade._roots[cls] = root

if __name__ == '__main__':

    class SimpleAccessToService:
        __metaclass__ = Facade

        @classmethod
        def test(cls, word):
            return 'SimpleAccessToService.test({0}) called'.format(word)

    class Service:
        def test(self, word):
            return 'Service.test({0}) called'.format(word)

    class ForcedTypeFacade:

        __metaclass__ = Facade

        __forcetype__ = Service


    print(SimpleAccessToService.test('foo'))

    print('Assigning Service')

    SimpleAccessToService.facade_root = Service()

    print(SimpleAccessToService.test('foo'))

    try:
        ForcedTypeFacade.facade_root = SimpleAccessToService()
    except TypeError, e:
        print('Assigning false type throws error: {0}'.format(e))

    ForcedTypeFacade.facade_root = Service()
