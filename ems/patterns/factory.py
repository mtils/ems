
class Factory(object):

    def make(self, abstract, *args, **kwargs):
        raise NotImplementedError('Please implement make')

class DummyFactory(Factory):

    def make(self, abstract, *args, **kwargs):
        return abstract(*args, **kwargs)