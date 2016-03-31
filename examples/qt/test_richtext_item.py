
import os

from ems.qt import QtCore, QtGui
from ems.qt.graphics.graphics_widget import GraphicsWidget

from ems.qt.graphics.scene_manager import SceneManager
from ems.qt.graphics.storage.manager import SceneStorageManager
from ems.qt.graphics.storage.dict_scene_serializer import DictSceneSerializer
from ems.qt.graphics.storage.temp_file_uri_provider import TempFileTargetUriProvider
from ems.qt.graphics.storage.json_file_scene_storage import JsonFileSceneStorage

QIcon = QtGui.QIcon

QIcon.setThemeSearchPaths([])

QIcon.setThemeName('null')

serializer = DictSceneSerializer()
storage = JsonFileSceneStorage(serializer)
uriProvider = TempFileTargetUriProvider()

QResource = QtCore.QResource

resourcePath = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','ems','qt4','gui','widgets','icons.rcc'))
QResource.registerResource(resourcePath)

resourcePath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','resources','icons','font-awesome')

QResource.registerResource(os.path.join(resourcePath, 'edit.rcc'))
QResource.registerResource(os.path.join(resourcePath, 'text-editor.rcc'))
QResource.registerResource(os.path.join(resourcePath, 'file.rcc'))


sceneManager = SceneManager(storageManager=SceneStorageManager(storage, uriProvider))

dialog = sceneManager.widget

dialog.show()