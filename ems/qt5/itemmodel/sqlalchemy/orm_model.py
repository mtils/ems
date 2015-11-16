
from PyQt5.QtCore import QAbstractTableModel

class OrmModel(QAbstractTableModel):

    def __init__(self):
        self._query = None