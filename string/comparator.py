#coding=utf-8
'''
Created on 26.01.2012

@author: michi
'''

from difflib import SequenceMatcher

synonyms_de_DE = {
                  u'ß':'ss',
                  u'ä':'ae',
                  u'ü':'ue',
                  u'ö':'oe',
                  u'Str.':'Strasse',
                  u'str.':'strasse',
                  #u'Straße':
                  } 
class StringComparator(object):
    
    valForOnlyCaseDiff = 0.99
    synonymDiffRange = (0.15,0.90)
    synonymCorrection = 0.05
    
    def __init__(self, typicalSynonyms={}):
        self.typicalSynonyms = typicalSynonyms
    
    def compare(self, a, b):
        if a == b:
            return 1.0
        if a.lower() == b.lower():
            return self.valForOnlyCaseDiff
        
        
        matcher = SequenceMatcher()
        matcher.set_seqs(a, b)
        ratio = matcher.ratio()
        if ratio > self.synonymDiffRange[0] and \
            ratio < self.synonymDiffRange[1]:
            translatedA = a
            translatedB = b
            for key in self.typicalSynonyms:
                translatedA = translatedA.replace(key, self.typicalSynonyms[key])
                translatedB = translatedB.replace(key, self.typicalSynonyms[key])
            matcher = SequenceMatcher()
            matcher.set_seqs(translatedA, translatedB)
            
            ratio = matcher.ratio() - self.synonymCorrection

        return ratio
            
                