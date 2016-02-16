
from ems.typehint import accepts
from ems.resource.repository import Repository

class DictAttributeRepository(Repository):

    @accepts(Repository)
    def __init__(self, sourceRepo, sourceAttribute='data'):
        self._sourceRepo = sourceRepo
        self.sourceAttribute = sourceAttribute

    def get(self, id_):
        """
        Return an object by its id

        :returns: dict
        """
        model = self._sourceRepo.get(id_)
        data = getattr(model, self.sourceAttribute)
        data['ID'] = id_
        return data

    def new(self, attributes=None):
        """
        Instantiate an object

        :returns: object
        """
        model = self._sourceRepo.new()

        data = getattr(model, self.sourceAttribute)
        for key in attributes:
            data[key] = attributes[key]

        return data

    def store(self, attributes, obj=None):
        """
        Store a new object. Create on if non passed, if one passed store the
        passed one

        :returns: object
        """
        if obj:
            raise TypeError("Obj has to be None")

        sourceAttributes = {self.sourceAttribute:self.new(attributes)}

        if 'ID' not in sourceAttributes:
            raise KeyError("attributes have to contain ")

        model = self._sourceRepo.store(sourceAttributes)
        return getattr(model, self.sourceAttribute)

    def update(self, model, changedAttributes):
        """
        Update model by changedAttributes and save it

        :returns: object
        """
        pass