'''
Created on 09.02.2011

@author: michi
'''
import unittest
import os
import tempfile
from ems.config import Config,NoDefaultProfileError
from ems.configuration.node import Node
from ems.configuration.loader.base import CfgFileNotFoundError,\
    CfgFileInvalidError

testXml = '''<?xml version="1.0" encoding="UTF-8"?>
<pyconfig>
    <profile id="1" standard="true" name="KontaktTabelle">
        <entry name="driver">sqlite</entry>
        <entry name="databasefile">datadir/database/main2.db</entry>
        <entry name="database">main</entry>    
    </profile>
    <profile id="2" name="Hauptverbindung">
        <entry name="driver">sqlite</entry>
        <entry name="databasefile">datadir/database/main.db</entry>
        <entry name="database">main</entry>
    </profile>
</pyconfig>'''

testBrokenXml = '''<?xml version="1.0" encoding="UTF-8"?>
<pyconfig>
    <profile id="1" standard="true" name="KontaktTabelle">
        <entry name="driver">sqlite</entro>
        <entry name="databasefile">datadir/database/main2.db</entry>
        <entry name="database">main</entry>    
    </profile>
    <profile id="2" name="Hauptverbindung">
        <entry name="driver">sqlite</entry>
        <entry name="databasefile">datadir/database/main.db</entry>
        <entry name="database">main</entry>
    </profile>
</pyconfig>'''

class Test(unittest.TestCase):


    def testInstanciation(self):
        c = Config()
        self.assertTrue(isinstance(c, Config))
    
    def testSimpleAssignment(self):
        c = Config()
        c['appDir'] = 'horstSchlemmer'
        self.assertEqual(c['appDir'],'horstSchlemmer')
        c['appDict'] = ('a','b','c')
        self.assertTrue(isinstance(c['appDict'], tuple))
        self.assertRaises(KeyError,c.__getitem__,'daddy')
    
    def testProfileAdding(self):
        c = Config()
        
        #Only add configuration.node.Node
        self.assertRaises(TypeError,c.setProfile,'myprofile', {})
        
        #Assign a profile
        profile = Node()
        profile['foo'] = 'bar'
        profile['fooz'] = 'baz'
        c.setProfile('myprofile',profile)
        
        #As long as we have only one profile, we don't need a standard profile
        self.assertEquals(c['foo'],profile['foo'])
        self.assertEquals(c['fooz'],profile['fooz'])
        
        #add another profile
        profile2= Node()
        profile2['foo'] = 'baz'
        c.setProfile('alternate',profile2)
        
        #getting foo again will raise NoDefaultProfileError
        self.assertRaises(NoDefaultProfileError,c.__getitem__,'foo')
        
        #setting the defaultProfile manually...
        c.defaultProfile = 'alternate'
        
        #...results in non equal values of c.foo and profile.foo
        self.assertNotEqual(c['foo'],profile['foo'])
    
    def testAssignOrder(self):
        c = Config()
        c['a'] = 0
        c['b'] = 1
        c['c'] = 2
        c['d'] = 3
        i=0
        for key in c.profiles['_noname_']:
            self.assertEqual(c[key],i)
            i += 1
    
    def testLoading(self):
        tempFile = os.path.join(tempfile.gettempdir(),
                              'unittest.ems.config.xml')
        f = open(tempFile,"w")
        f.write(testXml)
        f.close()
        c = Config(tempFile)
#        self.assertRaises(TypeError,c.setProfile,'myprofile', {})
        c.load()
        self.assertEqual(c['driver'],'sqlite')
        self.assertEqual(c['databasefile'],'datadir/database/main2.db')
        self.assertEqual(c['2:databasefile'],'datadir/database/main.db')
        
        #Test for non existing file
        file2 = os.path.join(tempfile.gettempdir(),"DoesNotExist.xml")
        c2 = Config(file2)
        self.assertRaises(CfgFileNotFoundError,c2.load)
        
        #Test for invalid xml
        tempFile2 = os.path.join(tempfile.gettempdir(),
                              'unittest2.ems.config.xml')
        f2 = open(tempFile2,"w")
        f2.write(testBrokenXml)
        f2.close()
        c3 = Config(tempFile2)
        self.assertRaises(CfgFileInvalidError,c3.load)
        
        os.remove(tempFile)
        os.remove(tempFile2)
        
    def testSaving(self):
        tempFile = os.path.join(tempfile.gettempdir(),
                              'unittest.save.ems.config.xml')
        c = Config(tempFile)
        c.autoload = False
        c.setProfile('first', Node())
        c.setProfileName('first', 'First Profile')
        c['testPath'] = '/a/b/c'
        c['foo'] = 'bar'
        c.setProfile('second', Node())
        c.setProfileName('second', 'Second Profile')
        c.profiles['second']['testPath'] = '/c/b/a'
        c.profiles['second']['bar'] = 'foo'
        c.save()
        c2 = Config(tempFile)
        c2.load()
        self.assertEqual(c2.profiles['first']['testPath'],'/a/b/c')
        self.assertRaises(NoDefaultProfileError,c.__getitem__,'testPath')
        c2.setDefaultProfile('second')
        self.assertEqual(c2['testPath'],'/c/b/a')
        os.remove(tempFile)
        
    def testAutoload(self):
        tempFile = os.path.join(tempfile.gettempdir(),
                              'unittest.ems.config.xml')
        f = open(tempFile,"w")
        f.write(testXml)
        f.close()
        c = Config(tempFile)
        c.autoload = True
        self.assertEqual(c.isConfigLoaded(),False)
        self.assertEqual(c['driver'],'sqlite')
        self.assertEqual(c.isConfigLoaded(),True)
        os.remove(tempFile)
        
        #Not existing File
        tempFile2 = os.path.join(tempfile.gettempdir(),
                              'unittest2.ems.config.xml')
        c2 = Config(tempFile2)
        c2.autoload = True
        self.assertRaises(CfgFileNotFoundError,c2.__getitem__,'foo')
        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testInstanciation']
    unittest.main()