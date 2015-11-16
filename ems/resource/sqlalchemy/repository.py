
from ems.resource.repository import Repository

class OrmRepository(Repository):

    def __init__(self, ormClass, session):
        self.ormClass = ormClass
        self._session = session

    def get(self, id_):
        return self._session

    def new(self, attributes):
        instance = self.ormClass()
        self._fill(instance)
        return instance

    def store(self, attributes):
        instance = self.new(attributes)
        self.session.add(instance)
        self.session.commit()
        return instance

    def update(self, model, changedAttributes):
        self._fill(model, changedAttributes)
        self.session.add(model)
        self.session.commit()
        return model

    def delete(self, model):
        self.session.delete(model)

    def _fill(self, ormObject, attributes):
        for key in attributes:
            setattr(ormObject, key, attributes[key])