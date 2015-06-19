
class StopDispatching(StopIteration):
    def __init__(self):
        self.returnValue = None

class Dispatcher(object):

    def __init__(self):
        self._listeners = {}

    def fire(self, name, *args, **kwargs):

        if not self.hasListeners(name):
            return

        for listener in self._listeners[name]:
            listener(*args, **kwargs)

    def listen(self, name, listener, priority=None):

        if not callable(listener):
            raise TypeError('Listener has to be callable')

        if name not in self._listeners:
            self._listeners[name] = []

        self._listeners[name].append(listener)

    def __call__(self, *args, **kwargs):
        return self.fire(*args, **kwargs)

    def hasListeners(self, name):
        return name in self._listeners