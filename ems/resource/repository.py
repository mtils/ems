
from abc import ABCMeta, abstractmethod

from six import add_metaclass

@add_metaclass(ABCMeta)
class Repository():

    @abstractmethod
    def get(self, id_):
        """
        Return an object by its id

        :returns: object
        """
        pass

    @abstractmethod
    def new(self, attributes=None):
        """
        Instantiate an object

        :returns: object
        """
        pass

    @abstractmethod
    def store(self, attributes, obj=None):
        """
        Store a new object. Create on if non passed, if one passed store the
        passed one

        :returns: object
        """
        pass

    @abstractmethod
    def update(self, model, changedAttributes):
        """
        Update model by changedAttributes and save it

        :returns: object
        """
        pass

    @abstractmethod
    def delete(self, model):
        """
        Delete the passed model

        :returns: object
        """
        pass

