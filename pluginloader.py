#coding=utf-8
'''
Created on 20.10.2013

@author: michi
'''

class Plugin(object):
    def match(self, query):
        raise NotImplementedError()

class PluginLoader(object):

    plugins = []

    def _find_plugin(self, query):
        for plugin in self.plugins:
            if plugin.match(query):
                return plugin

    def _find_plugins(self, query):
        plugins = []
        for plugin in self.plugins:
            if plugin.match(query):
                plugins.append(plugin)
        return plugins