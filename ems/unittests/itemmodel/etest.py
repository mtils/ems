'''
Created on 20.02.2011

@author: michi
'''
from ems.thirdparty.modeltest import ModelTest

class ETest(ModelTest):
    defaultTests = [
        "nonDestructiveBasicTest",
        "rowCount",
        "columnCount",
        "hasIndex",
        "index",
        "parent",
        "data"
    ]
    
    def __init__(self, _model, parent, tests=[]):
        self.tests = []
        if not len(tests):
            self.tests = ETest.defaultTests
        else:
            self.tests = tests
        super(ETest, self).__init__(_model, parent)
    
    def runAllTests(self):
        if self.fetchingMore:
            return
        for testMethod in self.tests:
            super(ETest, self).__getattribute__(testMethod)()
