'''
Created on 24.10.2011

@author: michi
'''
from PyQt4.QtCore import Qt

class LandmarkFilter(object):
    
    'FilterType Enum'
    InvalidFilter = 0
    DefaultFilter = 1
    NameFilter = 2
    ProximityFilter = 3
    CategoryFilter = 4
    BoxFilter = 5
    IntersectionFilter = 6
    UnionFilter = 7
    AttributeFilter = 8
    LandmarkIdFilter = 9
    
    'MatchFlag Enum'
    
    MatchExactly = Qt.MatchExactly
    MatchContains = Qt.MatchContains
    MatchStartsWith = Qt.MatchStartsWith
    MatchEndsWith = Qt.MatchEndsWith
    MatchFixedString =  Qt.MatchFixedString
    MatchCaseSensitive = Qt.MatchCaseSensitive