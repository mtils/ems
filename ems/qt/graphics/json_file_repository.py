from pprint import pprint as pp
from ems.qt.graphics.interfaces import SceneRepository
from ems.qt.graphics.page_item import PageItem

class JsonFileRepository(SceneRepository):

    def save(self, scene, tools):
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

        pp(saveData)

    def load(self, scene, tools):
        pass