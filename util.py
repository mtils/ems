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
    
    def __str__(self):
        return "%s %s %s" % (self.left, self.operator, self.right)