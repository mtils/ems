
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

    def getOrNew(self, id_):
        """
        Return an object by its id or create one with the passed id_
        The datastore has to support manual setting of ids  to make this
        work
        :returns: object
        """
        model = self.get(id_)

        if model:
            return model

        model = self.new()

        model.id = id_
        return model

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

