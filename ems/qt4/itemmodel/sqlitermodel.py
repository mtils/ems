
from PyQt4.QtCore import Qt

from filtermodels import SortFilterProxyModel
from ems import qt4
from ems.qt4.util import variant_to_pyobject
from sqliter.query import test, c, and_, or_, GenClause, PathNotFoundError

class SqlIterFilterModel(SortFilterProxyModel):

    def __init__(self, parent=None):
        SortFilterProxyModel.__init__(self, parent)
        self._query = None
        self._filterRowCount = 0
        self._filterColumnCount = 0
        self._query = None
        self._visibleColumnCache = None
        self._groupByResults = None
        self._name2ColumnMap = {}

        self._queryColumns = set()
        self._whereColumns = set()
        self._groupByColumns = set()

        self._hasGroupBy = False
        self._hasWhere = False
        self._hasColumnFilter = False
        self._visibleColumns = []

    def name2ColumnMap(self):

        if not self._name2ColumnMap:

            sourceModel = self.sourceModel()

            self._name2ColumnMap = {}

            for col in range(sourceModel.columnCount()):
                    colVariant = sourceModel\
                                   .headerData(col, Qt.Horizontal,
                                               qt4.ColumnNameRole)
                    colName = variant_to_pyobject(colVariant)
                    if not colName:
                        colName = "col-{0}".format(col)
                    self._name2ColumnMap[colName] = col

        return self._name2ColumnMap

    def filterAcceptsRow(self, sourceRow, sourceParent):

        if not self.usesRowQueryFilter():
            super(SqlIterFilterModel, self).filterAcceptsRow(sourceRow,
                                                             sourceParent)

        self._filterRowCount += 1

        columnMap = self.name2ColumnMap()

        whereResult = True
        groupByResult = True

        if self._hasWhere:
            # Only use columns which are needed to filter the model
            whereRow = {}

            for fieldName in self._whereColumns:
                col = columnMap[fieldName]
                whereRow[fieldName] = variant_to_pyobject(self.sourceModel()\
                                                        .index(sourceRow, col)\
                                                        .data(self.filterRole()))
                whereResult = self._query.match(whereRow)


        if self._hasGroupBy:
            # Only use columns which are needed to filter the model
            groupByRow = {}
            for fieldName in self._groupByColumns:
                col = columnMap[fieldName]
                groupByRow[fieldName] = variant_to_pyobject(self.sourceModel()\
                                                           .index(sourceRow, col)\
                                                           .data(self.filterRole()))
            groupByResult = self._groupByCheck(groupByRow)

        return whereResult and groupByResult

    def _groupByCheck(self, row):
        if self._hasGroupBy:
            test = []
            for field in self._query.group_by():
                try:
                    test.append(unicode(GenClause.extractValue(row, field)[0]))
                except PathNotFoundError:
                    test.append('')
            rowHash = u"|-|".join(test)
            if rowHash in self._groupByResults:
                return False
            self._groupByResults.add(rowHash)
        return True

    def invalidate(self):
        self.resetCaches()
        return SortFilterProxyModel.invalidate(self)

    def invalidateFilter(self):
        self.resetCaches()
        return SortFilterProxyModel.invalidateFilter(self)

    def resetCaches(self):
        self._groupByResults = set()
        self._name2ColumnMap.clear()

    def filterAcceptsColumn(self, sourceColumn, sourceParent):
        if self._hasColumnFilter:
            cols = self.visibleColumns()
            if cols:
                return (sourceColumn in cols)
        return SortFilterProxyModel.filterAcceptsColumn(self, sourceColumn, sourceParent)

    def visibleColumns(self):
        # TODO Fields with dots
        if self._hasColumnFilter and not self._visibleColumnCache:
            self._visibleColumnCache = []
            fields = self._query.fields()
            columnMap = self.name2ColumnMap()
            for colName in columnMap:
                if colName in fields:
                    self._visibleColumnCache.append(columnMap[colName])

        return self._visibleColumnCache

    def query(self):
        return self._query

    def setQuery(self, query):
        self._query = query
        self.resetCaches()
        if self._query:
            self._hasGroupBy = self._query.has_group_by()
            self._hasWhere = self._query.has_where()
            self._queryColumns = self._getFirstSegments(self._query.collect_fieldnames())
            self._groupByColumns = self._getFirstSegments(self._query.group_by_fieldnames())
            self._whereColumns = self._getFirstSegments(self._query.where_fieldnames())
            self._hasColumnFilter = self._query.has_fields()
            self._visibleColumnCache = None
        else:
            self._hasGroupBy = False
            self._hasWhere = False
            self._queryColumns = set()
            self._groupByColumns = set()
            self._whereColumns = set()
            self._hasColumnFilter = False
            self._visibleColumnCache = None

        #self.layoutAboutToBeChanged.emit()
        self.modelAboutToBeReset.emit()
        self.invalidateFilter()
        #self.layoutChanged.emit()
        self.modelReset.emit()

    def _getFirstSegments(self, fields):
        firstSegments = set()
        for field in fields:
            firstSegments.add(field.split('.')[0])
        return firstSegments

    def usesRowQueryFilter(self):
        return self._hasGroupBy or self._hasWhere