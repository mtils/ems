#coding=utf-8
'''
Created on 02.07.2011

@author: michi
'''

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
    
def stringSimilarity(a,b, returnPercent=False):
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
        #rightLetters = float(aLen - current[n])
        #print "Richtige: %s" % rightLetters
        #print "Richtig: %s" % ( aLen / rightLetters)
        try:
            result = 100.0 - (float(current[n]) / (float(aLen)/100.0))
        except ZeroDivisionError:
            return 0.0
        if result < 0.0:
            return 0.0
        return result
    return current[n]

if __name__ == '__main__':
#    tests = (
#             ("Östliche Rheinbrückenstraße","Östliche Rheinbrückenstr."),
#             ("Östliche Rheinbrückenstraße","Östliche Rheinbrückenstraße"),
#             ("Östliche Rheinbrückenstraße","Rheinbrückenstr."),
#             ("Östliche Rheinbrückenstraße","Östl. Rheinbrückenstr."),
#             ("Östliche Rheinbrückenstraße","Marienweg"),
#             ("Hauptstraße","Hauptstr."),
#             )
#    for test in tests:
#        print "%s (%s) %s:" % (test[0], len(test[0]), test[1])
#        print "%s %s%%" % (stringSimilarity(*test), stringSimilarity(*test, returnPercent=True))
    clause = GenClause('oma.name').like == 'Pups'
    print clause