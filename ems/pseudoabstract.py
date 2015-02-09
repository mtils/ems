'''
Created on 07.01.2011

@author: michi
'''
def pseudoAbstractCheck(cls,methodList):
    notCallable = []
    errorOccured = False
    for name in methodList:
        if hasattr(cls, name):
            if not callable(cls.__getattribute__(name)):
                errorOccured = True
                notCallable.append(name)
        else:
            notCallable.append(name)
            errorOccured = True
    if errorOccured:
        raise NotImplementedError(
            "You have to implement method(s): %s" % ", ".join(notCallable))

if __name__ == '__main__':
    class Test(object):
        def __init__(self):
            pseudoAbstractCheck(self,['test','test2','test3'])
        def test(self):
            print "Isch"
    
    class Test2(Test):
        def __init__(self):
            super(Test2, self).__init__()
        
    
    foo = Test2()
    foo.test2()