
import os

from ems.qt import QtCore
from ems.qt.graphics.graphics_widget import GraphicsWidget

from ems.qt.graphics.scene_manager import SceneManager
from ems.qt.graphics.storage.manager import SceneStorageManager
from ems.qt.graphics.storage.dict_scene_serializer import DictSceneSerializer
from ems.qt.graphics.storage.temp_file_uri_provider import TempFileTargetUriProvider
from ems.qt.graphics.storage.json_file_scene_storage import JsonFileSceneStorage


serializer = DictSceneSerializer()
storage = JsonFileSceneStorage(serializer)
uriProvider = TempFileTargetUriProvider()

QResource = QtCore.QResource

resourcePath = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','ems','qt4','gui','widgets','icons.rcc'))
QResource.registerResource(resourcePath)

sceneManager = SceneManager(storageManager=SceneStorageManager(storage, uriProvider))

dialog = sceneManager.widget

dialog.show()