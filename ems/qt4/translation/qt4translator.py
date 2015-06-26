
from PyQt4.QtCore import QTranslator

from ems.typehint import accepts
from ems.translation.translator import Translator

class Qt4Translator(Translator):

    @accepts(QTranslator)
    def __init__(self, translator):
        """Intialize with QTranslator. This is a proxy

        :param translator: PyQt4.QtCore.QTranslator

        :returns: void
        """
        self._qTranslator = translator

    def translate(self, key, default='', params={}, quantity=1, lang=None):
        translated = unicode(self._qTranslator.translate(key, default, '', quantity))

        for key in params:
            translated = translated.replace(':{0}'.format(key), params[key])

        return translated