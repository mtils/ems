
import os

from ems.qt import QtCore
from ems.qt.graphics.graphics_widget import GraphicsWidget

QResource = QtCore.QResource

resourcePath = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','ems','qt4','gui','widgets','icons.rcc'))
QResource.registerResource(resourcePath)

dialog = GraphicsWidget()
dialog.show()