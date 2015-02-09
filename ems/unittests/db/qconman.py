'''
Created on 09.02.2011

@author: michi
'''
from __future__ import absolute_import

import unittest
import os
import tempfile

from PyQt4.QtCore import SIGNAL

from ems.db.conman import ConMan,NoConfigFound,DriverNotConfiguredError,\
    ConnectionNotFoundError,HandleAlreadyUsedError
from ems.unittests.db.conman import Test as BaseClass
from ems.unittests.config import testXml
from ems.qt4.db.conman import QConMan
from ems.db.backends.qsql.connection import Connection
from ems.config import Config,NoDefaultProfileError,CfgFileNameNotSettedError
from ems.qt4.db.concfgloader import QConCfgLoader
from ems.configuration.node import Node
from ems.configuration.loader.base import CfgFileNotFoundError,\
    CfgFileInvalidError
from ems.unittests.signalreceiver import SignalReceiver

class TestQ(BaseClass):

    def getTestConMan(self):
        return QConMan()
    
    def getTestConCfgLoader(self,fileName):
        return QConCfgLoader(fileName)
    
    def testEmitting(self):
        tempFile = os.path.join(tempfile.gettempdir(),
                              'unittest.ems.conman.xml')
        f = open(tempFile,"w")
        f.write(testXml)
        f.close()
        cm = self.getTestConMan()
        cl = self.getTestConCfgLoader(tempFile)
        cl.autoload = True
        cm.loader = cl
        sr = SignalReceiver()
        sr.connect(cm, SIGNAL("loaded(QString)"),sr.recSignal)
        sr.connect(cm, SIGNAL("removed(QString)"),sr.recSignal)

        self.assertTrue(isinstance(cm.get(),Connection))
        self.assertEqual(sr.curEntry()[0],'default')
        con2 = cm.get('alternate','2')
        self.assertEqual(con2.name,'Hauptverbindung')
        cm.remove('alternate')
        self.assertEqual(sr.curEntry()[0],'alternate')
        
        os.remove(tempFile)
        pass
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testInstanciation']
    unittest.main()