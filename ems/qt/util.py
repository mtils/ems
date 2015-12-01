
from ems.qt.identifiers import ItemData

class Inspector(object):

    def __init__(self, model):
        self._model = model

    def columnOfName(self, colName):

        for i in range(self._model.columnCount()):
            modelColName = self._model.headerData(i, 1, ItemData.ColumnNameRole)
            if modelColName == colName:
                return i

        return -1

    def nameOfColumn(self, column):

        pass