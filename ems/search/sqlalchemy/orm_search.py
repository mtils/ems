
from ems.search.base import Search, Criteria

class OrmSearch(Search):

    def __init__(self, session, ormClass):
        self._session = session
        criteria = Criteria()
        criteria.modelClass = ormClass
        super().__init__(criteria)

    def all(self):

        self.searching.fire(self)
        query = self._session.query(self.modelClass)
        otherQuery = self.querying.fire(self, query)

        if otherQuery:
            result = otherQuery.all()
        else:
            result = query.all()

        self.searched.fire(self, result)

        return result