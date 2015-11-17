
from abc import ABCMeta, abstractmethod

from six import add_metaclass

@add_metaclass(ABCMeta)
class Repository():

    @abstractmethod
    def get(self, id_):
        pass

    @abstractmethod
    def all(self):
        pass

    @abstractmethod
    def new(self, attributes):
        pass

    @abstractmethod
    def store(self, attributes):
        pass

    @abstractmethod
    def update(self, model, changedAttributes):
        pass

    @abstractmethod
    def delete(self, model):
        pass

