'''
Created on 29.10.2011

@author: michi
'''
from PyQt4.QtCore import SLOT, pyqtSlot
from PyQt4.QtGui import QMainWindow, QMenuBar, QApplication, QMenu, QMessageBox,\
    QDialog
from PyQt4.QtNetwork import QNetworkConfigurationManager, QNetworkSession

from mapswidget import MapsWidget #@UnresolvedImport
from ems.qt4.location.maps.geoserviceprovider import GeoServiceProvider #@UnresolvedImport
from ems.unittests.qt4.location.maps.navigatedialog import NavigateDialog #@UnresolvedImport
from ems.unittests.qt4.location.maps.searchDialog import SearchDialog #@UnresolvedImport

class MainWindow(QMainWindow):
    
    _serviceProvider = None
    _mapsWidget = None
    _markerManager = None
    _positionSource = None
    _lastNavigator = None
    
    _session = None
    _netConfigManager = None
    
    _tracking = True
    
    _firstUpdate = True
    
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        
        self._serviceProvider = None
        self._markerManager = None
        self._positionSource = None
        self._lastNavigator = None
        self._tracking = True
        self._firstUpdate = True
        
        self._mapsWidget = MapsWidget(self)
        self.setCentralWidget(self._mapsWidget)
        
        mbar = QMenuBar(self)
        mbar.addAction("Quit", QApplication.instance(),SLOT('quit()'))
        mbar.addAction("My Location", self._goToMyLocation)
        
        searchMenu = QMenu("Search", mbar)
        mbar.addMenu(searchMenu)
        searchMenu.addAction("For address or name",self._showSearchDialog)
        
        navigateMenu = QMenu("Directions", mbar)
        mbar.addMenu(navigateMenu)
        
        navigateMenu.addAction("From here to address", self._showNavigateDialog)
        
        self.setMenuBar(mbar)
        self.setWindowTitle("Maps Demo")
        #self.initialize()
        self._netConfigManager = QNetworkConfigurationManager()
        self._netConfigManager.updateCompleted.connect(self._openNetworkSession)
        self._netConfigManager.updateConfigurations()
    
    @pyqtSlot()
    def _openNetworkSession(self):
        self._session = QNetworkSession(self._netConfigManager.defaultConfiguration())
        if self._session.isOpen():
            self.initialize()
        else:
            self._session.opened.connect(self.initialize)
            self._session.open()
    
    @pyqtSlot()
    def _goToMyLocation(self):
        #self._mapsWidget.animatedPanTo(center)
        self._mapsWidget.map.setFocus()
        self.tracking = True
    
    def initialize(self):
        if self._serviceProvider:
            del self._serviceProvider
            self._serviceProvider = None
        
        providers = GeoServiceProvider.availableServiceProviders()
        if len(providers) < 1:
            QMessageBox.information(self, "Maps Demo",
                                    "No service providers are available")
            QApplication.instance().quit()
            return
        
        for provider in providers:
            self._serviceProvider = GeoServiceProvider(provider)
            if self._serviceProvider.mappingManager() and \
                self._serviceProvider.searchManager() and \
                self._serviceProvider.routingManager():
                break
        
        #print self._serviceProvider.mappingManager()
        if self._serviceProvider.error() != GeoServiceProvider.NoError:
            QMessageBox.information(self, "Maps Demo",
                                    self.tr("Error loading geoservice plugin "))
            QApplication.instance().quit()
            return
        
        if not self._serviceProvider.mappingManager() or \
            not self._serviceProvider.searchManager() or \
            not self._serviceProvider.routingManager():
            QMessageBox.information(self, "Maps Demo",
                                    self.tr("No geoservice found with mapping/search/routing"))
            QApplication.instance().quit()
            return
        
        self._mapsWidget.initialize(self._serviceProvider.mappingManager())
        self._mapsWidget.markerClicked.connect(self._showMarkerDialog)
        self._mapsWidget.mapPanned.connect(self._disableTracking)
    
    def _disableTracking(self):
        self._tracking = False
    
    def _updateMyPosition(self, info):
        if self._mapsWidget:
            self._mapsWidget.setMyLocation(info.coordinate())
            if self._tracking:
                self._mapsWidget.animatedPanTo(info.coordinate())
            if self._firstUpdate:
                self._mapsWidget.statusBar().showText("Receiving from GPS")
        self._firstUpdate = False
    
    def _showNavigateDialog(self):
        nd = NavigateDialog()
        if nd.exec_() == QDialog.Accepted:
            if self._markerManager:
                pass
    
    def _showMarkerDialog(self, marker):
        print "MarkerDialog should be showed now"
    
    def _showSearchDialog(self):
        sd = SearchDialog()
        return
    
    def _showErrorMessage(self, err, msg):
        QMessageBox.critical(self, 'Error', msg)
        self._mapsWidget.statusBar().hide()
        self._mapsWidget.map.setFocus()