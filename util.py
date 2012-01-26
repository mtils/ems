#coding=utf-8
'''
Created on 02.07.2011

@author: michi
'''
from difflib import SequenceMatcher

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
    
    def __nonzero__(self, other):
        self.operator = 'if'
        self.right = other
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

if __name__ == '__main__':
    tests = (
             ("Östliche Rheinbrückenstraße","Östliche Rheinbrückenstr."),
             ("Östliche Rheinbrückenstraße","Östliche Rheinbrückenstraße"),
             ("Östliche Rheinbrückenstraße","Rheinbrückenstr."),
             ("Östliche Rheinbrückenstraße","Östl. Rheinbrückenstr."),
             ("Östliche Rheinbrückenstraße","Marienweg"),
             ("Hauptstraße","Hauptstr."),
             ("Cresbacher Str.", "Breslauer Str."),
             (u"Im Gässle", u"Im Gäßle"),
             (u"Hafenweg", u"HAFENWEG")
             )
    for test in tests:
        print "%s (%s) %s:" % (test[0], len(test[0]), test[1])
        print "%s %s%%" % (stringSimilarity(*test), stringSimilarity(*test, returnPercent=True))
#    clause = GenClause('oma.name').like == 'Pups'
#    print clause

def splitIntAlpha(intString):
    integer = []
    string = []

    firstNonDigitFound = False
  
    for char in intString:
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