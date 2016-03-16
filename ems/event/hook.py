
import sys

class _EventForwarder(object):

    def __init__(self, eventName, forwarder):
        self.eventName = eventName
        self.forwarder = forwarder

    def __call__(self, *args, **kwargs):
        self.forwarder(self.eventName, *args, **kwargs)

class EventHook(object):
    """A 'event' Transmitter
       You can hook into it with hook += myReceiver (callable)
       then hook.fire() will call myReceiver()
       (or hook += myobj.onFoo => hook.fire(bar) will call myobj.onFoo(bar))

       Normal usage would be:
       class DB(object):
           def __init__(self):
               self.recordCreated = EventHook()

           def create(self, entry):
               //...code
               self.recordCreated.fire(entry)

        class DebugPrinter(object):
            def printCreatedEntry(self, entry):

        db = DB()
        dp = DebugPrinter()
        db.recordCreated += dp.printCreatedEntry

    """
    def __init__(self):
        self.__receivers = []
        self.fireBlocked = False
        self.wasFired = False

    def __iadd__(self, handler):
        """Adds a receiver to this EventHook

        args:
            handler A callable which will be called on fire

        :returns: EventHook
        """
        self.__receivers.append(handler)
        return self

    def __isub__(self, handler):
        """Removes a receiver from this EventHook

        args:
            handler The callable which was previous assigned

        :returns: EventHook
        """
        self.__receivers.remove(handler)
        return self

    def fire(self, *args, **keywargs):
        """Fires a 'event'. Not really, it calls every assigned callable
           If some callable returns true, it will stop Propagation

        :returns: void
        """
        if self.fireBlocked:
            return

        self.wasFired = True

        for handler in self.__receivers:
            result = handler(*args, **keywargs)
            if result:
                return result

    def forward(self, eventName, forwarder):
        self.__iadd__(_EventForwarder(eventName, forwarder))

    def __call__(self, *args, **keywargs):
        """Alias for fire(). The main purpose of this method is to allow
           chaining of events. So like
           instance.hook += my_callable
           you can write
           instance.hook += my_object.hook
           Than the event of instance will be fired if my_object.hook is fired

        :rtype: void
        """
        return self.fire(*args, **keywargs)

    def clearOfType(self, receiverObj):
        """Removes all receivers of the class of the class
           ob the passed method

           :returns EventHook
        """

        deleteLater = set()

        for knownReceiver in self.__receivers:
            if knownReceiver.im_self == receiverObj:
                deleteLater.add(knownReceiver)

        for knownReceiver in deleteLater:
            self -= knownReceiver
        return self

    def clear(self):
        """Clears all receivers
           :returns: EventHook
        """
        self.__receivers = []
        return self

    def __len__(self):
        return len(self.__receivers)

    def __iter__(self):
        return iter(self.__receivers)

class EventProperty(object):

    def __init__(self, name=None, default=None, eventHook=None):
        self.__name = name
        self._eventHook = EventHook() if eventHook is None else eventHook
        self._listeners = {}
        self._listenerInstalled = False
        self._default = default

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self._name(instance), self._default)

    def __set__(self, instance, value):

        name = self._name(instance)

        if name in instance.__dict__ and instance.__dict__[name] == value:
            return

        instance.__dict__[name] = value
        self._eventHook.fire(value, instance)

    def __delete__(self, instance):
        del instance.__dict__[self._name(instance)]

    def _name(self, instance):

        if self.__name:
            return self.__name

        cls = instance.__class__

        for name in cls.__dict__:
            if cls.__dict__[name] is self:
                self.__name = name
                return name

    def __iadd__(self, handler):
        """Adds a receiver to this EventHook

        args:
            handler A callable which will be called on fire

        :returns: EventHook
        """
        self._eventHook.__iadd__(handler)
        return self

    def __isub__(self, handler):
        """Removes a receiver from this EventHook

        args:
            handler The callable which was previous assigned

        :returns: EventHook
        """
        self._eventHook.__isub__(handler)
        return self

    def forward(self, eventName, forwarder):
        return self._eventHook.forward(eventName, forwarder)

    def listenOn(self, instance, listener):

        if instance not in self._listeners:
            self._listeners[instance] = []

        self._installListener()

        self._listeners[instance].append(listener)

    def _installListener(self):
        if self._listenerInstalled:
            return

        self._listenerInstalled = True

        self._eventHook += self._callListeners

    def _callListeners(self, value, instance):

        try:
            for listener in self._listeners[instance]:
                listener(value)
        except KeyError:
            return


class EventHookProperty(object):

    def __init__(self):
        self._hooksByInstance = {}

    def __get__(self, instance, owner):

        if instance is None:
            return self

        if instance not in self._hooksByInstance:
            self._hooksByInstance[instance] = EventHook()

        return self._hooksByInstance[instance]

class TestListener(object):

    def __init__(self, printOnCalls=False):
        self.params = []
        self.callCount = 0
        self.printOnCalls = printOnCalls

    def __call__(self, *args):
        self.params = args
        self.callCount += 1
        if self.printOnCalls:
            sys.stdout.write("TestListener.called: count:{} params:{}".format(self.callCount, self.params))