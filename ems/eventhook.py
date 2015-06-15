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
        self._store = None

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
                return

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

    def get(self):
        """Get a value from store to reduce the if value changed lines in using objects
           Simply set the value via self.loaded.set(True) and self.loaded.get()
           to let Eventhook do the work
        """
        return self._store

    def set(self, value):
        """Set a value to a store to reduce the if value changed lines in using objects
           Simply set the value via self.loaded.set(True) and self.loaded.get()
           to let Eventhook do the work
        """
        if self._store == value:
            return

        self._store = value
        self.fire(value)

    def __len__(self):
        return len(self.__receivers)