
from PyQt4.QtCore import Qt

from filtermodels import SortFilterProxyModel
from ems import qt4
from ems.qt4.util import variant_to_pyobject
from sqliter.query import test, c, and_, or_, GenClause

class SqlIterFilterModel(SortFilterProxyModel):

    def __init__(self, parent=None):
        SortFilterProxyModel.__init__(self, parent)
        self._query = None
        self._filterRowCount = 0
        self._filterColumnCount = 0
        self._query = None
        self._visibleColumnCache = None
        self._groupByResults = None

    def filterAcceptsRow(self, sourceRow, sourceParent):
        #self._filterRowCount += 1
        #print "SqlIterFilterModel.filterAcceptsRow",self._filterRowCount

        testRow = {}

        name2Column = {}

        for col in range(self.sourceModel().columnCount()):
            colName = variant_to_pyobject(self.sourceModel()\
                                          .index(sourceRow, col)\
                                          .data(qt4.ColumnNameRole))
            if not colName:
                colName = "col-{0}".format(col)

            name2Column[colName] = col

            testRow[colName] = variant_to_pyobject(self.sourceModel()\
                                                    .index(sourceRow, col)\
                                                    .data(self.filterRole()))

        if self._query and self._query.has_where():
            if self._groupByCheck(testRow):
                return self._query.match(testRow)
            return self._query.match(testRow)

        if not self._groupByCheck(testRow):
            return False

        return SortFilterProxyModel.filterAcceptsRow(self, sourceRow, sourceParent)

    def _groupByCheck(self, row):
        if self._groupByResults is not None:
            test = []
            for field in self._query.group_by():
                test.append(unicode(GenClause.extractValue(row, field)[0]))
            rowHash = u"|-|".join(test)
            if rowHash in self._groupByResults:
                return False
            self._groupByResults.add(rowHash)
        return True

    def _parseGroupBy(self):
        if self._query and self._query.has_group_by():
            self._groupByResults = set()
        else:
            self._groupByResults = None

    def invalidate(self):
        self._visibleColumnCache = None
        return SortFilterProxyModel.invalidate(self)

    def invalidateFilter(self):
        self._visibleColumnCache = None
        return SortFilterProxyModel.invalidateFilter(self)
    
    def resetCaches(self):
        self._visibleColumnCache = None
        self._groupByResults = None
        self._parseGroupBy()

    def filterAcceptsColumn(self, sourceColumn, sourceParent):
        cols = self.visibleColumns()
        if cols:
            return (sourceColumn in cols)
        return SortFilterProxyModel.filterAcceptsColumn(self, sourceColumn, sourceParent)

    def visibleColumns(self):
        # TODO Fields with dots
        if self._visibleColumnCache is None:
            if self._query and self._query.has_fields():
                self._visibleColumnCache = []
                fields = self._query.fields()
                for col in range(self.sourceModel().columnCount()):
                    colVariant = self.sourceModel()\
                                   .headerData(col, Qt.Horizontal,
                                               qt4.ColumnNameRole)
                    colName = variant_to_pyobject(colVariant)
                    if colName in fields:
                        self._visibleColumnCache.append(col)

            else:
                self._visibleColumnCache = ()

        return self._visibleColumnCache

    def query(self):
        return self._query

    def setQuery(self, query):
        self._query = query
        self._parseGroupBy()
        self.layoutAboutToBeChanged.emit()
        self.invalidateFilter()
        self.layoutChanged.emit()