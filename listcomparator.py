'''
Created on 02.10.2012

@author: michi
'''
from ems.util import isiterable


class EqualsComparator(object):
    def compare(self, a, b):
        return a == b

class PropertyComparator(object):
    def __init__(self, propertyName):
        self.propertyName = propertyName
         
    def compare(self, a, b):
        return a.__getattribute__(self.propertyName) == \
            b.__getattribute__(self.propertyName)

class ItemComparator(object):
    def __init__(self, keyName):
        self.keyName = keyName
         
    def compare(self, a, b):
        return a[self.keyName] == b[self.keyName]

class MethodComparator(object):
    def __init__(self, methodName):
        self.methodName = methodName
    
    def compare(self, a, b):
        return a.__getattribute__(self.methodName)() == \
            b.__getattribute__(self.methodName)()

class ListComparator(object):
    
    def __init__(self, iterableA=None, iterableB=None, comparator=None):
        
        if iterableA is not None:
            self.setA(iterableA)
        
        if iterableB is not None:
            self.setB(iterableB)
        
        self._reset()
        
        if comparator is None:
            comparator = EqualsComparator()
            
        self.setComparator(comparator)
    
    def _reset(self):
        self._union = []
        self._intersection = []
        self._difference = []
        self._onlyContainedInA = []
        self._onlyContainedInB = []
        self._symetricDifference = []
        self._isParsed = False
        self._onlyContainedInAParsed = False
        self._onlyContainedInBParsed = False
        self._unionParsed = False
        self._symetricDifferenceParsed = False
    
    def getA(self):
        return self._iterableA
    
    def setA(self, iterableA):
        if not isiterable(iterableA):
            raise TypeError("A and B has to be iterable and countable by len()")
        self._iterableA = iterableA
        self._reset()
        return self
    
    a = property(getA, setA)
    
    def getB(self):
        return self._iterableB
    
    def setB(self, iterableB):
        if not isiterable(iterableB):
            raise TypeError("A and B has to be iterable and countable by len()")
        self._iterableB = iterableB
        self._reset()
        return self
    
    b = property(getB, setB)
    
    def getComparator(self):
        
        '''
        Returns the object which makes the comparison
        @rtype: EqualsComparator
        '''
        return self._comparator
    
    def setComparator(self, comparator):
        if not hasattr(comparator, 'compare'):
            raise TypeError("")
        
        self._comparator = comparator
        return self
    
    comparator = property(getComparator, setComparator)
    
    def getIntersection(self):
        '''
        Returns the Intersection of a and b
        @return: The values which are in a and b
        @rtype: list
        '''
        if not self._onlyContainedInAParsed:
            self.getOnlyContainedInA()
        return self._intersection
    
    intersection = property(getIntersection)
    
    def getUnion(self):
        '''
        Returns the unification of a and b
        @return: All Values of a and b (unique)
        @rtype: list
        '''
        if not self._unionParsed:
            inter = self.getIntersection()
            sym = self.getSymetricDifference()
            interLen = len(inter)
            symLen = len(sym)
            
            fullLength = max(interLen, symLen)
            
            for i in range(fullLength):
                if i < symLen:
                    self._union.append(sym[i])
                if i < interLen:
                    self._union.append(inter[i])
            
        return self._union
    
    union = property(getUnion)
    
    def getOnlyContainedInA(self):
        '''
        Returns all values which are only in a
        @return: All values of a which are not contained in b
        @rtype: list
        '''
        if not self._onlyContainedInAParsed:
            for aVal in self._iterableA:
                aIsInB = False
                for bVal in self._iterableB:
                    if self._comparator.compare(aVal, bVal):
                        aIsInB = True
                        self._intersection.append(aVal)
                    
                if not aIsInB:
                    self._onlyContainedInA.append(aVal)
            self._onlyContainedInAParsed = True

        return self._onlyContainedInA
    
    onlyContainedInA = property(getOnlyContainedInA)
    
    def getOnlyContainedInB(self):
        '''
        Returns all values which are only in b
        @return: All values in b which are not contained in a
        @rtype: list
        '''
        if not self._onlyContainedInBParsed:
            for bVal in self._iterableB:
                bIsInA = False
                for aVal in self._iterableA:
                    if self._comparator.compare(aVal, bVal):
                        bIsInA = True
                        #self._intersection.append(aVal)
                    
                if not bIsInA:
                    self._onlyContainedInB.append(bVal)
            self._onlyContainedInBParsed = True
            
        return self._onlyContainedInB
    
    onlyContainedInB = property(getOnlyContainedInB)
    
    def getDifference(self):
        return self.getOnlyContainedInA()
    
    difference = property(getDifference)
    
    def getSymetricDifference(self):
        if not self._symetricDifferenceParsed:
            self._symetricDifference = self.getOnlyContainedInA() + \
                                       self.getOnlyContainedInB()
                                       
            self._symetricDifferenceParsed = True
        return self._symetricDifference
    
    symetricDifference = property(getSymetricDifference)
    
    def getComplement(self):
        return self.getOnlyContainedInB()
    
    complement = property(getComplement)
    
    def _parse(self):
        
        if self._isParsed:
            return
        
        self._isParsed = True
    
if __name__ == '__main__':
    
    simpleList = []
    
    a = {
     'Title':'Simple Lists',
     'a' : [1,2,3,4,5,6,7,8,9],
     'b' : [2,4,6,8,10,12,14,16],
    }
    a['c'] = ListComparator(a['a'], a['b'])
    
    b = {
         'Title':'Dicts',
         'a': [{'testItem':1},{'testItem':2},{'testItem':3},{'testItem':4},
               {'testItem':5},{'testItem':6},{'testItem':7},{'testItem':8},
               {'testItem':9}],
         'b': [{'testItem':2},{'testItem':4},{'testItem':6},{'testItem':8},
               {'testItem':10},{'testItem':12},{'testItem':14},{'testItem':16}]
         }
    b['c'] = ListComparator(b['a'], b['b'], ItemComparator('testItem'))
    
    for test in a,b:
        print "------------------------------------------"
        print "Title:", test['Title']
        print "a", test['a']
        print "b", test['b']
        print "Intersection:", test['c'].intersection
        print "Only in A:", test['c'].onlyContainedInA
        print "Only in B:", test['c'].onlyContainedInB
        print "Union", test['c'].union
        print "SymetricDifference", test['c'].symetricDifference
    
    