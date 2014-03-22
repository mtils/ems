#coding=utf-8
'''
Created on 20.10.2013

@author: michi
'''

from eventhook import EventHook

class Plugin(object):
    def match(self, query):
        raise NotImplementedError()

class PluginLoader(object):

    _plugins = []

    pluginAdded = EventHook()
    pluginRemoved = EventHook()

    def __iadd__(self, plugin):
        self._plugins.append(plugin)
        PluginLoader.pluginAdded.fire(plugin)
        return self

    def __isub__(self, plugin):
        self._plugins.remove(plugin)
        PluginLoader.pluginRemoved.fire(plugin)
        return self

    def _find_plugin(self, query):
        for plugin in self._plugins:
            if plugin.match(query):
                return plugin

    def _find_plugins(self, query):
        plugins = []
        for plugin in self._plugins:
            if plugin.match(query):
                plugins.append(plugin)
        return plugins