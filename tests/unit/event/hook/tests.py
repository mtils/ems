
import unittest
from ems.event.hook import EventProperty, EventHook, EventHookProperty

class HookTest(unittest.TestCase):

    def test_finds_name(self):

        test = EventUser()
        self.assertEquals('loaded', EventUser.loaded._name(test))

    def test_get_set(self):

        test = EventUser()
        test.loaded = True

        self.assertIs(True, test.loaded)

        test.loaded = False

        self.assertIs(False, test.loaded)

    def test_fire_value(self):

        test = EventUser()
        listener = Listener()

        EventUser.loaded += listener

        test.loaded = True

        self.assertIs(test, listener.params[1])
        self.assertIs(True, listener.params[0])
        self.assertEquals(1, listener.callCount)

    def test_listen(self):

        test = EventUser()
        listener = Listener()

        EventUser.loaded.listenOn(test, listener)

        test.loaded = True

        self.assertIs(True, listener.params[0])
        self.assertEquals(1, listener.callCount)

    def test_event_hook_fires(self):

        emitter = EventHookPropertyEmitter()
        listener = Listener()

        emitter.triggered += listener

        self.assertEquals(0, listener.callCount)
        emitter.trigger('someVar')
        self.assertEquals(1, listener.callCount)
        self.assertEquals(('someVar',), listener.params)

    def test_event_hook_works_with_multiple_instances(self):

        emitter = EventHookPropertyEmitter()
        emitter2 = EventHookPropertyEmitter()

        listener = Listener()
        listener2 = Listener()

        emitter.triggered += listener
        emitter2.triggered += listener2

        self.assertEquals(0, listener.callCount)
        self.assertEquals(0, listener2.callCount)
        emitter.trigger('someVar')
        self.assertEquals(1, listener.callCount)
        self.assertEquals(('someVar',), listener.params)
        self.assertEquals(0, listener2.callCount)
        self.assertEquals([], listener2.params)

        emitter2.trigger('someOtherVar')

        self.assertEquals(1, listener.callCount)
        self.assertEquals(('someVar',), listener.params)
        self.assertEquals(1, listener2.callCount)
        self.assertEquals(('someOtherVar',), listener2.params)

class Listener(object):

    def __init__(self):
        self.params = []
        self.callCount = 0

    def __call__(self, *args):
        self.params = args
        self.callCount += 1


class EventUser(object):

    loaded = EventProperty()

class EventHookPropertyEmitter(object):

    triggered = EventHookProperty()

    def trigger(self, *params):
        self.triggered.fire(*params)

if __name__ == '__main__':
    unittest.main()