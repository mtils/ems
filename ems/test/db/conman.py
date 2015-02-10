'''
Created on 09.02.2011

@author: michi
'''
import unittest
import os
import tempfile
from ems.db.conman import ConMan,NoConfigFound,DriverNotConfiguredError,\
    ConnectionNotFoundError,HandleAlreadyUsedError

from ems.unittests.config import testXml
from ems.db.backends.qsql.connection import Connection
from ems.config import Config,NoDefaultProfileError,CfgFileNameNotSettedError
from ems.db.concfgloader import ConCfgLoader
from ems.configuration.node import Node
from ems.configuration.loader.base import CfgFileNotFoundError,\
    CfgFileInvalidError

class Test(unittest.TestCase):


    def testInstanciation(self):
        c = self.getTestConMan()
        self.assertTrue(isinstance(c, ConMan))
    
    def testLoad(self):
        c = self.getTestConMan()
        self.assertRaises(NoConfigFound,c.get)
        config = {'database':'/tmp/ems.db.conman.db'}
        self.assertRaises(DriverNotConfiguredError,c.load,'test',config)
        config['name'] = 'Test Connection'
        config['driver'] = 'sqlite'
        self.assertTrue(isinstance(c.load('test',config), Connection))
    
    def getTestConMan(self):
        return ConMan()
    
    def getTestConCfgLoader(self,fileName):
        return ConCfgLoader(fileName)
    
    def testLoadDefault(self):
        c = self.getTestConMan()
        config = {'database':'/tmp/ems.db.conman.db',
                  'driver':'sqlite',
                  'name':'Test Connection'}
        c.setCfgForHandle('default', config)
        self.assertTrue(isinstance(c.get(), Connection))
    
    def testMultipleConnections(self):
        c = self.getTestConMan()
        config = {'database':'/tmp/ems.db.conman.db',
                  'driver':'sqlite',
                  'name':'Test Connection'}
        c.setCfgForHandle('default', config)
        config2 = {'database':'TestDB',
                  'driver':'sqlite',
                  'name':'Test Connection 2'}
        c.setCfgForHandle('alternate', config2)
        #Test default connection is sqlite
        self.assertTrue(isinstance(c.get(),Connection))
        self.assertEqual(c.get().name,'Test Connection')
        self.assertTrue(isinstance(c.get('alternate'),Connection))
        self.assertEqual(c.get('alternate').name,'Test Connection 2')
        
        c.remove('alternate')
        self.assertRaises(NoConfigFound,c.get,'alternate')
        self.assertRaises(NoConfigFound,c.getCfgForHandle,'alternate')
        
        self.assertRaises(HandleAlreadyUsedError,c.load,'default')
    
    def testAutoCfgLoad(self):
        #Save config
        tempFile = os.path.join(tempfile.gettempdir(),
                              'unittest.ems.conman.xml')
        f = open(tempFile,"w")
        f.write(testXml)
        f.close()
        #Instanciate config with config file
        cfg = self.getTestConCfgLoader(tempFile)
        cfg.autoload = True
        cm = self.getTestConMan()
        #Assign cfg as loader
        cm.loader = cfg
        
        con1 = cm.get()
        con2 = cm.get('alternate','2')
        con3 = cm.get('next','1')
        self.assertEqual(con1.name,'KontaktTabelle')
        self.assertEqual(con2.name,'Hauptverbindung')
        self.assertEqual(con3.name,'KontaktTabelle')
        
        os.remove(tempFile)
        
    def testAutoCfgLoadError(self):
        cfg = self.getTestConCfgLoader('')
        cfg.autoload = True
        cm = self.getTestConMan()
        cm.loader = cfg
        self.assertRaises(CfgFileNameNotSettedError,cm.get)
        #Non existing config
        tempFile = os.path.join(tempfile.gettempdir(),
                              'unittest.ems.conman.xml')
        cm.loader.fileName = tempFile
        self.assertRaises(CfgFileNotFoundError,cm.get)
        
        return
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testInstanciation']
    unittest.main()
