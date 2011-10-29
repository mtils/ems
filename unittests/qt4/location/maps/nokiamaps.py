'''
Created on 29.10.2011

@author: michi
'''
import sys

from PyQt4.QtGui import QApplication

from mainwindow import MainWindow #@UnresolvedImport

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName('Nokia')
    app.setApplicationName('MapsDemo')
    
    mw = MainWindow()
    mw.resize(800,600)
    mw.show()
    app.exec_()