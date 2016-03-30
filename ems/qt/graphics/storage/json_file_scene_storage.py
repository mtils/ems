
import json

from ems.typehint import accepts
from ems.qt.graphics.storage.interfaces import SceneStorage, SceneSerializer

class JsonFileSceneStorage(SceneStorage):

    @accepts(SceneSerializer)
    def __init__(self, serializer):
        self._serializer = serializer

    def load(self, scene, tools, uri):

        with open(uri) as jsonFile:
            data = json.load(jsonFile)
        scene.clear()
        self._serializer.deserialize(data, scene, tools)


    def save(self, scene, tools, uri):
        serialized = self._serializer.serialize(scene, tools)

        with open(uri, 'w') as outfile:
            json.dump(serialized, outfile, indent=4)
