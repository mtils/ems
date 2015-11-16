
from abc import ABCMeta, abstractmethod

class Repository(metaclass=ABCMeta):

    @abstractmethod
    def get(self, id_):
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