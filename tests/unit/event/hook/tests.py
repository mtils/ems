
import unittest
from ems.event.hook import EventProperty, EventHook

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


class Listener(object):

    def __init__(self):
        self.params = []
        self.callCount = 0

    def __call__(self, *args):
        self.params = args
        self.callCount += 1


class EventUser(object):

    loaded = EventProperty()

if __name__ == '__main__':
    unittest.main()