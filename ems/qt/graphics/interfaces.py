

from abc import ABCMeta, abstractmethod

from six import add_metaclass

@add_metaclass(ABCMeta)
class Finalizer(object):
    '''
    A Finalizer makes something with the scene before it gets finally printed or previewed
    '''
    @abstractmethod
    def toFinalized(self, scene):
        pass

    @abstractmethod
    def toEditable(self, scene):
        pass

