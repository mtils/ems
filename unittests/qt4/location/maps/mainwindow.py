'''
Created on 29.10.2011

@author: michi
'''
from PyQt4.QtCore import SLOT
from PyQt4.QtGui import QMainWindow, QMenuBar, QApplication, QMenu, QMessageBox
from mapswidget import MapsWidget #@UnresolvedImport
from ems.qt4.location.maps.geoserviceprovider import GeoServiceProvider #@UnresolvedImport

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        
        self.serviceProvider = None
        self.markerManager = None
        self.positionSource = None
        self.lastNavigator = None
        self.tracking = False
        self.firstUpdate = True
        
        self.mapsWidget = MapsWidget(self)
        self.setCentralWidget(self.mapsWidget)
        
        mbar = QMenuBar(self)
        mbar.addAction("Quit", QApplication.instance(),SLOT('quit()'))
        mbar.addAction("My Location", self.goToMyLocation)
        
        searchMenu = QMenu("Search", mbar)
        mbar.addMenu(searchMenu)
        searchMenu.addAction("For address or name",self.showSearchDialog)
        
        navigateMenu = QMenu("Directions", mbar)
        mbar.addMenu(navigateMenu)
        
        navigateMenu.addAction("From here to address", self.showNavigateDialog)
        
        self.setMenuBar(mbar)
        self.setWindowTitle("Maps Demo")
        self.initialize()
        
    
    def goToMyLocation(self):
        self.mapsWidget.map.setFocus()
        self.tracking = True
    
    def showSearchDialog(self):
        print "Kommt noch"
    
    def showNavigateDialog(self):
        print "Kommt auch noch"
    
    def initialize(self):
        if self.serviceProvider:
            del self.serviceProvider
            self.serviceProvider = None
        
        providers = GeoServiceProvider.availableServiceProviders()
        if len(providers) < 1:
            QMessageBox.information(self, "Maps Demo",
                                    "No service providers are available")
            QApplication.instance().quit()
            return