
from ems.search.base import Search, Criteria

class OrmSearch(Search):

    def __init__(self, session, ormClass):
        self._session = session
        criteria = Criteria()
        criteria.modelClass = ormClass
        super().__init__(criteria)

    def all(self):
        return self._session.query(self.modelClass).all()