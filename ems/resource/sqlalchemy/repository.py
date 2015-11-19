
from sqlalchemy.orm.session import object_session

from ems.resource.repository import Repository

class OrmRepository(Repository):

    def __init__(self, ormClass, session):
        self.ormClass = ormClass
        self._session = session

    def get(self, id_):
        return self._session.query(self.ormClass).get(id_)

    def all(self):
        return self._session.query(self.ormClass).all()

    def new(self, attributes=None):
        instance = self.ormClass()
        attributes = attributes if attributes is not None else {}
        self._fill(instance, attributes)
        return instance

    def store(self, attributes, obj=None):
        instance = self._fill(obj, attributes) if obj else self.new(attributes)
        self._session.add(instance)
        self._session.commit()
        return instance

    def update(self, model, changedAttributes):

        self._fill(model, changedAttributes)

        session = self._modelSession(model)
        session.add(model)
        session.commit()

        return model

    def delete(self, model):
        session = self._modelSession(model)
        session.delete(model)
        session.commit()
        return model

    def _modelSession(self, model):
        objectSession = object_session(model)
        return objectSession if objectSession else self._session

    def _fill(self, ormObject, attributes):
        for key in attributes:
            setattr(ormObject, key, attributes[key])
        return ormObject

if __name__ == '__main__':
    r = OrmRepository('A','S')
    print(r)