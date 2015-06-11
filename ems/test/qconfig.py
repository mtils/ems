'''
Created on 09.02.2011

@author: michi
'''
import unittest
import os
import tempfile
from PyQt4.QtCore import QObject,SIGNAL

from ems.config import NoDefaultProfileError
from ems.qt4.config import QConfig
from ems.configuration.node import Node
from ems.configuration.loader.base import CfgFileNotFoundError,\
    CfgFileInvalidError

class SignalReceiver(QObject):
    def __init__(self,parent=None):
        super(SignalReceiver, self).__init__(parent)
        self.edit = []
        self.delete = []
        self.pChange = ''
        self.pDelete = ''
        self.spChange = ''
        self.loaded = ''
        self.saved = ''
        self.pNameChanged = ()
    def receiveEdit(self,profile,varName,val):
        self.edit.append((profile,varName,val))
        
    def receiveDelete(self,profile,varName):
        self.delete.append((profile,varName))
    
    def receivePChange(self,name):
        self.pChange = name
    
    def receivePDelete(self,name):
        self.pDelete = name
    
    def receiveSPChange(self,name):
        self.spChange = name
    
    def receiveLoaded(self,name):
        self.loaded = name
        
    def receiveSaved(self,name):
        self.saved = name
    
    def receivePNameChanged(self,id,name):
        self.pNameChanged = (id,name)

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
        c = QConfig()
        self.assertTrue(isinstance(c, QConfig))
    
    def testSimpleAssignment(self):
        c = QConfig()
        c['appDir'] = 'horstSchlemmer'
        self.assertEqual(c['appDir'],'horstSchlemmer')
        c['appDict'] = ('a','b','c')
        self.assertTrue(isinstance(c['appDict'], tuple))
        self.assertRaises(KeyError,c.__getitem__,'daddy')

    def testProfileAdding(self):
        c = QConfig()

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
        self.assertRaises(NoDefaultProfileError, c.__getitem__, 'foo')

        #setting the defaultProfile manually...
        c.defaultProfile = 'alternate'

        #...results in non equal values of c.foo and profile.foo
        self.assertNotEqual(c['foo'], profile['foo'])

    def testAssignOrder(self):
        c = QConfig()
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
        c = QConfig(tempFile)
#        self.assertRaises(TypeError,c.setProfile,'myprofile', {})
        c.load()
        self.assertEqual(c['driver'],'sqlite')
        self.assertEqual(c['databasefile'],'datadir/database/main2.db')
        self.assertEqual(c['2:databasefile'],'datadir/database/main.db')

        #Test for non existing file
        file2 = os.path.join(tempfile.gettempdir(),"DoesNotExist.xml")
        c2 = QConfig(file2)
        self.assertRaises(CfgFileNotFoundError,c2.load)

        #Test for invalid xml
        tempFile2 = os.path.join(tempfile.gettempdir(),
                              'unittest2.ems.config.xml')
        f2 = open(tempFile2,"w")
        f2.write(testBrokenXml)
        f2.close()
        c3 = QConfig(tempFile2)
        self.assertRaises(CfgFileInvalidError,c3.load)

        os.remove(tempFile)
        os.remove(tempFile2)

    def testSaving(self):
        tempFile = os.path.join(tempfile.gettempdir(),
                              'unittest.save.ems.config.xml')
        c = QConfig(tempFile)
        c.setProfile('first', Node())
        c.setProfileName('first', 'First Profile')
        c['testPath'] = '/a/b/c'
        c['foo'] = 'bar'
        c.setProfile('second', Node())
        c.setProfileName('second', 'Second Profile')
        c.profiles['second']['testPath'] = '/c/b/a'
        c.profiles['second']['bar'] = 'foo'
        c.save()
        c2 = QConfig(tempFile)
        c2.load()
        self.assertEqual(c2.profiles['first']['testPath'],'/a/b/c')
        self.assertRaises(NoDefaultProfileError,c.__getitem__,'testPath')
        c2.setDefaultProfile('second')
        self.assertEqual(c2['testPath'],'/c/b/a')
        os.remove(tempFile)

    def testEmitting(self):
        t = SignalReceiver()
        tempFile = os.path.join(tempfile.gettempdir(),
                              'unittest.emit.ems.config.xml')

        f = open(tempFile,"w")
        f.write(testXml)
        f.close()

        c = QConfig(tempFile)
        c.entryChanged.connect(t.receiveEdit)
        c.entryDeleted.connect(t.receiveDelete)
        c.profileChanged.connect(t.receivePChange)
        c.profileDeleted.connect(t.receivePDelete)
        c.standardProfileChanged.connect(t.receiveSPChange)
        c.configLoaded.connect(t.receiveLoaded)
        c.configSaved.connect(t.receiveSaved)
        c.profileNameChanged.connect(t.receivePNameChanged)

        c.setProfile('first', Node())
        c.setProfileName('first', 'First Profile')

        c.load()

        self.assertEquals(unicode(t.loaded),unicode(tempFile))
        c['driver'] = 'MSSQL'
        self.assertEquals(unicode(t.edit[0][0]),u'1')
        self.assertEquals(unicode(t.edit[0][1]),u'driver')
        self.assertEquals(unicode(t.edit[0][2]),u'MSSQL')
        c['2:testEntry'] = 'myTest'
        self.assertEquals(unicode(t.edit[1][0]),u'2')
        self.assertEquals(unicode(t.edit[1][1]),u'testEntry')
        self.assertEquals(unicode(t.edit[1][2]),u'myTest')
        del c['2:testEntry']
        self.assertEquals(unicode(t.delete[0][0]),u'2')
        self.assertEquals(unicode(t.delete[0][1]),u'testEntry')
        self.assertRaises(KeyError,c.__getitem__,'2:testEntry')
        
        c.delProfile(u'1')
        self.assertEqual(t.pDelete,u'1')
        c.setDefaultProfile(u'2')
        self.assertEqual(t.spChange,u'2')
        c.setProfile(u"3",Node())
        self.assertEqual(t.pChange,u'3')
        c['3:testProperty'] = 'Doesnt matter'
        
        c.setProfileName(u'3', 'Test Profil')
        self.assertEqual(unicode(t.pNameChanged[0]),u'3')
        self.assertEqual(unicode(t.pNameChanged[1]),u'Test Profil')
        self.assertEquals(unicode(t.edit[2][0]),u'3')
        self.assertEquals(unicode(t.edit[2][1]),u'testProperty')
        self.assertEquals(unicode(t.edit[2][2]),u'Doesnt matter')
        self.assertEqual(t.saved,'')
        c.save()
        self.assertEqual(t.saved,tempFile)
        os.remove(tempFile)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testInstanciation']
    unittest.main()