'''
Created on 29.10.2011

@author: michi
'''
import sys

from PyQt4.QtGui import QApplication

from mainwindow import MainWindow #@UnresolvedImport
from ems.qt4.location.maps.geoserviceprovider import GeoServiceProvider #@UnresolvedImport


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName('Nokia')
    app.setApplicationName('MapsDemo')
    app.setGraphicsSystem('raster')
    from ems.qt4.location.plugins.nokia.geoserviceproviderfactory_nokia import \
        GeoServiceProviderFactoryNokia #@UnresolvedImport
    GeoServiceProvider.addPlugin(GeoServiceProviderFactoryNokia())
    
    mw = MainWindow()
    mw.resize(360,640)
    mw.show()
    app.exec_()