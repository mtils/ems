
from ems.search.base import Search, Criteria

class OrmSearch(Search):

    def __init__(self, session, ormClass):
        self._session = session
        criteria = Criteria()
        criteria.modelClass = ormClass
        super().__init__(criteria)

    def all(self):

        self.searching.fire(self)
        query = self._newQuery()
        otherQuery = self.querying.fire(self, query)

        if otherQuery:
            result = otherQuery.all()
        else:
            result = query.all()

        self.searched.fire(self, result)

        return result

    def _newQuery(self):
        return self._session.query(self.modelClass)

    @staticmethod
    def _collectColumns(ormClass, prefix=''):
        keys = [str(c).split('.')[1] for c in ormClass.__table__.columns]

        if not prefix:
            return keys

        return ["{}.{}".format(prefix,c) for c in keys]