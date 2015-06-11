
from ems.eventhook import EventHook

class Container(object):

    def __init__(self):

        self._bindings = {}
        self._instances = {}
        self._aliases = {}

        self.resolving = EventHook()
        self.afterResolving = EventHook()

    def make(self, abstract, *args, **kwargs):

        if self.isAlias(abstract):
            return self.make(self.abstract(abstract), *args, **kwargs)

        if self.isShared(abstract) and self.hasInstance(abstract):
            return self.getInstance(abstract)

        instance = self._createInstance(abstract, *args, **kwargs)

        if self.isShared(abstract):
            self._instances[abstract] = instance

        return instance

    def bind(self, abstract, creator):

        self._bindings[abstract] = {
            'creator': creator,
            'shared': False
        }

    def share(self, abstract, creator):

        self._bindings[abstract] = {
            'creator': creator,
            'shared': False
        }

    def shareInstance(self, abstract, instance):
        self._bindings[abstract] = {
            'creator': instance,
            'shared': True
        }
        self._instances[abstract] = instance

    def bound(self, abstract):
        return abstract in self._bindings

    def alias(self, abstract, alias):
        self._aliases[alias] = abstract

    def isAlias(self, abstract):
        return abstract in self._aliases

    def abstract(self, alias):
        return self._aliases[alias]

    def isShared(self, abstract):

        if not self.bound(abstract):
            return False

        return self._bindings[abstract]['shared']

    def hasInstance(self, abstract):
        return abstract in self._instances

    def getInstance(self, abstract):
        return self._instances[abstract]

    def _createInstance(self, abstract, *args, **kwargs):

        creator = self._bindings[abstract]['creator']

        instance = creator(*args, **kwargs)

        self.resolving.fire(instance, self)

        self.afterResolving.fire(instance, self)

        return instance

    def __getitem__(self,key):

        return self.make(key)

    def __contains__(self, key):
        return key in self._instances

    def __setitem__(self,key,val):
        return self.shareInstance(key, val)

    def __delitem__(self,key):

        profileId, key = self.__getProfileAndVarName(key)
        del self.__profiles[profileId][key]
        self.entryDeleted.fire(profileId, key)