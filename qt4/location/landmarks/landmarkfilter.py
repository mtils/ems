'''
Created on 24.10.2011

@author: michi
'''
from PyQt4.QtCore import Qt

class LandmarkFilter(object):
    
    'MatchFlag Enum'
    
    MatchExactly = Qt.MatchExactly
    MatchContains = Qt.MatchContains
    MatchStartsWith = Qt.MatchStartsWith
    MatchEndsWith = Qt.MatchEndsWith
    MatchFixedString =  Qt.MatchFixedString
    MatchCaseSensitive = Qt.MatchCaseSensitive