#coding=utf-8
'''
Created on 02.07.2011

@author: michi
'''

import sys, re

from difflib import SequenceMatcher
from uuid import uuid4

platformNames = {
                 'linux':'Linux',
                 'linux2':'Linux',
                 'win32':'Windows',
                 'cygwin':'Windows/Cygwin',
                 'darwin':'Mac OS X',
                 'os2':'OS/2',
                 'os2emx':'OS/2 EMX',
                 'riscos':'RiscOS',
                 'atheos':'AtheOS'
                 }

def platformName():
    return platformNames[sys.platform]

class GenClause(object):
    def __init__(self, left):
        self.left = left
        self.operator = ''
        self.right = None
    
    def __eq__(self, other):
        self.operator = '=='
        self.right = other
        return self
    
    def __ne__(self, other):
        self.operator = '!='
        self.right = other
        return self
    
    def __le__(self, other):
        self.operator = '<='
        self.right = other
        return self
    
    def __lt__(self, other):
        self.operator = '<'
        self.right = other
        return self
    
    def __ge__(self, other):
        self.operator = '>='
        self.right = other
        return self
    
    def __gt__(self, other):
        self.operator = '>'
        self.right = other
        return self
    
    def __nonzero__(self):
        self.operator = 'if'
        self.right = ''
        return self
    
    def in_(self, *args):
        self.operator = 'in'
        self.right = args
        return self
        
        
    
#    def __getattr__(self, key):
#        print "__getattr__(%s)" % key
#        try:
#            return super(GenClause, self).__getattr__(key)
#        except AttributeError, e:
#            return self
#            if self.operator == key:
#                return self.right
#            raise e
#    
#    def __setattr__(self, key, val):
#        print "__setattr__(%s, %s)" % (key, val)
#        try:
#            return super(GenClause, self).__setattr__(key, val)
#        except AttributeError:
#            self.operator = key
#            self.right = val
    
    def __str__(self):
        return "%s %s %s" % (self.left, self.operator, self.right)


def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if not s1:
        return len(s2)
 
    previous_row = xrange(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
 
    return previous_row[-1]

def stringSimilarity(a, b, returnPercent=False):
    "Calculates the Levenshtein distance between a and b."
    aLen = len(a)
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
        
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*m
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
    if returnPercent:
        #print "Lang: %s" % aLen
        rightLetters = float(aLen - current[n])
        wrongLetters = current[n]
        #print "Richtige: %s" % rightLetters
        #print "Falsche: %s" % wrongLetters
        #print "Richtig: %s" % ( 100.0 - (float(current[n]) / (float(aLen)/100.0)))
        
        #matcher = SequenceMatcher()
        #matcher.set_seqs(a, b)
        #print "SequenceMatcher: {0}".format(matcher.ratio()*100)
        #print "Falsche: {0}".format(levenshtein(a, b))
        
        try:
            result = 100.0 - (float(current[n]) / (float(aLen)/100.0))
        except ZeroDivisionError:
            return 0.0
        if result < 0.0:
            return 0.0
        return result
    return current[n]


def splitIntAlpha(intString):
    integer = []
    string = []

    firstNonDigitFound = False
  
    for char in unicode(intString):
        if firstNonDigitFound:
            string.append(unicode(char))
            continue
        if char.isdigit():
            integer.append(char)
            continue
        if not char.isalpha():
            firstNonDigitFound = True
            continue
        string.append(unicode(char))
        firstNonDigitFound = True
    try:
        return (int("".join(integer)), "".join(string).strip())
    except ValueError:
        return (0,'')

def isiterable(obj):
    try:
        it = iter(obj)
        return True
    except TypeError:
        return False
    
def items2list(listOfItemAccessable, keyName):
    result = []
    for row in listOfItemAccessable:
        result.append(row.__getitem__(keyName))
    return result

def properties2list(listOfAttributeAccessable, propertyName):
    result = []
    for row in listOfAttributeAccessable:
        result.append(row.__getattribute__(propertyName))
    return result

def methodResults2list(listOfAttributeAccessable, methodName):
    result = []
    for row in listOfAttributeAccessable:
        result.append(row.__getattribute__(methodName)())
    return result

def global_uid():
    return "{" + str(uuid4()) + "}"

def snake_case(camelCase):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camelCase)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def camelCase(value):
    def camelcase(): 
        yield str.lower
        while True:
            yield str.capitalize

    c = camelcase()
    return "".join(c.next()(x) if x else '_' for x in value.split("_"))

class classproperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()