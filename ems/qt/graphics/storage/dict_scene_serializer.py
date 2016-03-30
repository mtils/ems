
from ems.qt.graphics.storage.interfaces import SceneSerializer
from ems.qt.graphics.page_item import PageItem

class DictSceneSerializer(SceneSerializer):

    def serialize(self, scene, tools):

        saveData = {
            '@author': 'Michael Tils',
            '@desciption': 'Graphics Scene Contents',
            '@data': {
                'pages': []
            }
        }

        items = []
        for item in scene.items():
            if isinstance(item, PageItem):
                continue
            items.append(tools.serialize(item))

        saveData['@data']['pages'].append({'items':items})

        return saveData

    def deserialize(self, sceneData, scene, tools):

        page = PageItem()
        scene.addItem(page)

        for page in sceneData['@data']['pages']:
            for item in page['items']:
                item = tools.deserialize(item)
                scene.addItem(item)