
from ems.patterns.factory import Factory
from ems.eventhook import EventHook
from ems.typehint import MethodWrapper

class Container(Factory):

    def __init__(self, *args, **kwargs):

        self._bindings = {}
        self._instances = {}
        self._aliases = {}

        self._resolvingListeners = {}
        self._afterResolvingListeners = {}

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
            'shared': True
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

    def resolving(self, abstract, listener):

        if not callable(listener):
            raise TypeError('Listener has to be callable')

        if not abstract in self._resolvingListeners:
            self._resolvingListeners[abstract] = []

        self._resolvingListeners[abstract].append(listener)

    def afterResolving(self, abstract, listener):

        if not callable(listener):
            raise TypeError('Listener has to be callable')

        if not abstract in self._afterResolvingListeners:
            self._afterResolvingListeners[abstract] = []

        self._afterResolvingListeners[abstract].append(listener)

    def _createInstance(self, abstract, *args, **kwargs):

        try:
            creator = self._bindings[abstract]['creator']
        except KeyError:
            creator = abstract
            if not callable(creator):
                raise LookupError("No factory for abstract '{0}' registered".format(creator))

        if creator is abstract and self.hasTypeHint(abstract) and not args:
            args = self._buildDependencies(abstract)

        instance = creator(*args, **kwargs)

        self._callListeners(abstract, instance, self._resolvingListeners)
        self._callListeners(abstract, instance, self._afterResolvingListeners)

        return instance

    def hasTypeHint(self, abstract):
        try:
            return isinstance(abstract.__init__, MethodWrapper)
        except AttributeError:
            return False

    def _buildDependencies(self, abstract):

        init = abstract.__init__

        objects = []

        for type_ in init.types:
            objects.append(self.make(type_))

        return objects

    def _callListeners(self, abstract, instance, listeners):

        for key in listeners:
            if key == abstract:
                for listener in listeners[key]:
                    listener(instance, self)

            elif isinstance(key, type) and isinstance(instance, key):
                for listener in listeners[key]:
                    listener(instance, self)

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