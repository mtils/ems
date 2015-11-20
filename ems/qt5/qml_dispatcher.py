
import os.path

from PyQt5.QtCore import QUrl
from PyQt5.QtQml import QQmlComponent

class ComponentCreator(object):

    def __init__(self, engine):
        self._engine = engine

    def __call__(self, filePath, routeName):

        url = QUrl.fromLocalFile(filePath)

        component = QQmlComponent(self._engine, url)

        if component.status() != QQmlComponent.Error:
            return component

        if component.errors():
            re = RuntimeError(component.errors()[0].description(), component.errors())
            raise re

        raise RuntimeError('Component has unknown error state')
