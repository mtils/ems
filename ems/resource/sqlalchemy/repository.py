
from sqlalchemy.orm.session import object_session

from ems.event.hook import EventHook
from ems.resource.repository import Repository

class OrmRepository(Repository):

    def __init__(self, ormClass, session):
        self.ormClass = ormClass
        self._session = session

    def get(self, id_):
        self.getting.fire(id_)
        model = self._session.query(self.ormClass).get(id_)
        self.got.fire(model)
        return model

    def all(self):
        return self._session.query(self.ormClass).all()

    def new(self, attributes=None):
        self.instantiating.fire(attributes)
        instance = self.ormClass()
        attributes = attributes if attributes is not None else {}
        self.fill(instance, attributes)
        self.instantiated.fire(instance)
        return instance

    def store(self, attributes, obj=None):
        self.storing.fire(attributes, obj)
        instance = self.fill(obj, attributes) if obj else self.new(attributes)
        self._session.add(instance)
        self._session.commit()
        self.stored.fire(instance, attributes)
        return instance

    def update(self, model, changedAttributes):
        self.updating.fire(model, changedAttributes)
        self.fill(model, changedAttributes)

        session = self._modelSession(model)
        session.add(model)
        session.commit()

        self.updated.fire(model, changedAttributes)
        return model

    def delete(self, model):
        self.deleting.fire(model)
        session = self._modelSession(model)
        session.delete(model)
        session.commit()
        self.deleted.fire(model)
        return model

    def _modelSession(self, model):
        objectSession = object_session(model)
        return objectSession if objectSession else self._session

if __name__ == '__main__':
    r = OrmRepository('A','S')
    print(r)