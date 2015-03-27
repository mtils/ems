#coding=utf-8
'''
Created on 26.01.2012

@author: michi
'''
from collections import OrderedDict
from difflib import SequenceMatcher

synonyms_de_DE = OrderedDict((
                  (u'ß','ss'),
                  (u'ä','ae'),
                  (u'ü','ue'),
                  (u'ö','oe'),
                  (u' Str.',' Strasse'),
                  (u'-Str.','-Strasse'),
                  (u'str.','strasse')
                  ))
class StringComparator(object):

    valForOnlyCaseDiff = 0.99
    synonymDiffRange = (0.15,0.90)
    synonymCorrection = 0.05

    def __init__(self, typicalSynonyms={}):
        self.typicalSynonyms = typicalSynonyms

    def compare(self, a, b):
        if not isinstance(a, basestring):
            return 0.0
        if not isinstance(b, basestring):
            return 0.0
        if a == b:
            return 1.0
        if a.lower() == b.lower():
            return self.valForOnlyCaseDiff


        matcher = SequenceMatcher()
        matcher.set_seqs(a.lower(), b.lower())
        ratio = matcher.ratio()
        if ratio > self.synonymDiffRange[0] and \
            ratio < self.synonymDiffRange[1]:
            translatedA = a
            translatedB = b
            for key in self.typicalSynonyms:
                translatedA = translatedA.replace(key, self.typicalSynonyms[key])
                translatedB = translatedB.replace(key, self.typicalSynonyms[key])

            matcher = SequenceMatcher()
            matcher.set_seqs(translatedA.lower(), translatedB.lower())

            ratio = matcher.ratio() - self.synonymCorrection

        return ratio

    def find_best_matching(self, reference, pool, min_percent=90):

        pool_by_similarity = {}

        for candidate in pool:
            percent = self.compare(candidate, reference)*100.0
            if percent >= min_percent:
                pool_by_similarity[percent] = candidate

        if len(pool_by_similarity):
            percents = pool_by_similarity.keys()
            percents.sort()
            percents.reverse()
            return ( pool_by_similarity[percents[0]], percents[0] )

        raise LookupError()