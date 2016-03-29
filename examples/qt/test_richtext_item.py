
import os

from ems.qt import QtCore
from ems.qt.graphics.graphics_widget import GraphicsWidget
from ems.qt.graphics.json_file_repository import JsonFileRepository

QResource = QtCore.QResource

resourcePath = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','ems','qt4','gui','widgets','icons.rcc'))
QResource.registerResource(resourcePath)
repository = JsonFileRepository()

dialog = GraphicsWidget()
dialog.setRepository(repository)
dialog.show()