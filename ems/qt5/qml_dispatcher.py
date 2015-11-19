
from PyQt5.QtCore import QUrl
from PyQt5.QtQml import QQmlComponent

class ComponentCreator(object):

    def __init__(self, engine):
        self._engine = engine

    def __call__(self, filePath, routeName):

        url = QUrl.fromLocalFile(filePath)

        return QQmlComponent(self._engine, url)