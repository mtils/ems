
from locale import getdefaultlocale
from abc import ABCMeta, abstractmethod

from ems.patterns.facade import Facade
from ems.event.hook import EventProperty

class Translator(object):

    __metaclass__ = ABCMeta

    locale = EventProperty('lang', default=getdefaultlocale()[0][0:2])

    @abstractmethod
    def translate(self, key, default='', params={}, quantity=1, lang=None):
        raise NotImplementedError()


class Lang(object):

    __metaclass__ = Facade
    __forcetype__ = Translator

    @classmethod
    def get(cls, *args, **kwargs):
        return cls.facade_root.translate(*args, **kwargs)


def trans(self, *args, **kwargs):
    return Lang.get(*args, **kwargs)

def locale():
    return Lang.locale