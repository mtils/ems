
from abc import ABCMeta, abstractmethod

from six import add_metaclass

from ems.event.hook import EventHookProperty

@add_metaclass(ABCMeta)
class Repository(object):

    getting = EventHookProperty()
    """
    This event is fired before a model is retrieved via get
    signature: getting(id)
    """

    got = EventHookProperty()
    """
    This event is fired after a model is retrieved via get
    signature: got(model)
    """

    instantiating = EventHookProperty()
    """
    This event is fired before a new model is instantiated
    signature: instantiating(attributes)
    """

    instantiated = EventHookProperty()
    """
    This is event is fired after a new model was instantiated
    signature: instantiated(model)
    """

    filling = EventHookProperty()
    """
    This is event is fired before a model was filled with the new attributes
    signature: filling(model, newAttributes)
    """

    filled = EventHookProperty()
    """
    This is event is fired after a model was filled with the new attributes
    signature: filled(model, newAttributes)
    """

    storing = EventHookProperty()
    """
    This event is fired before a model is going to be stored
    signature: storing(attributes, model=None)
    """

    stored = EventHookProperty()
    """
    This event is fired after a model was stored
    signature: stored(model, attributes)
    """

    updating = EventHookProperty()
    """
    This event is fired before a model gets updated (and filled)
    signature: updating(model, changedAttributes)
    """

    updated = EventHookProperty()
    """
    This event is fired after a model gets updated
    signature: updated(model, changedAttributes)
    """

    deleting = EventHookProperty()
    """
    This event gets fired before a model gets deleted
    signature: deleting(model)
    """

    deleted = EventHookProperty()
    """
    This event gets fired after a model was deleted
    signature: deleted(model)
    """

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

    def fill(self, model, attributes):
        """
        Fill the model with attributes
        :returns: the filled model
        """
        self.filling.fire(model, attributes)
        for key in self._cleanAttributes(attributes):
            setattr(model, key, attributes[key])
        self.filled.fire(model, attributes)
        return model

    def _cleanAttributes(self, attributes):
        return attributes
