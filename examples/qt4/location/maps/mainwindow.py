'''
Created on 29.10.2011

@author: michi
'''
import os.path
from PyQt4.QtCore import SLOT, pyqtSlot
from PyQt4.QtGui import QMainWindow, QMenuBar, QApplication, QMenu, QMessageBox,\
    QDialog
from PyQt4.QtNetwork import QNetworkConfigurationManager, QNetworkSession

from mapswidget import MapsWidget #@UnresolvedImport
from ems.qt4.location.maps.geoserviceprovider import GeoServiceProvider #@UnresolvedImport
from ems.unittests.qt4.location.maps.navigatedialog import NavigateDialog #@UnresolvedImport
from ems.unittests.qt4.location.maps.searchDialog import SearchDialog #@UnresolvedImport
from marker import MarkerManager #@UnresolvedImport
from ems.qt4.location.geocoordinate import GeoCoordinate
from ems.unittests.qt4.location.maps.markerdialog import MarkerDialog #@UnresolvedImport
from ems.qt4.location.maps.georouterequest import GeoRouteRequest
from ems.unittests.qt4.location.maps.navigator import Navigator #@UnresolvedImport

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
        
        #HIER DIE WUNSCH KOORDINATE
        #self._homeCoordinate = GeoCoordinate(48.525759, 8.5659) #Pfalzgrafenweiler
        #self._homeCoordinate = GeoCoordinate(40.7145, -74.0071) #New York
        
        self._homeCoordinate = GeoCoordinate(40.7368927949, -74.0074199438) #New York leicht danaben
        
        
        self._serviceProvider = None
        self._markerManager = None
        self._positionSource = None
        self._lastNavigator = None
        self._tracking = True
        self._firstUpdate = True
        
        self._mapsWidget = MapsWidget(self._homeCoordinate, self)
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
        coord = self._markerManager.myLocation()
        self._mapsWidget.animatedPanTo(coord)
        self._mapsWidget.map_().setFocus()
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
        
        iconPath = os.path.join(os.path.dirname(__file__),'images')
        self.iconPath = iconPath
        
        
        
        self._markerManager = MarkerManager(iconPath,
                                            self._serviceProvider.searchManager(),
                                            self._homeCoordinate)
        self._mapsWidget.setMarkerManager(self._markerManager)
        self._markerManager.searchError.connect(self.onSearchError)
        
        
        
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
                req = GeoRouteRequest()
                req.setTravelModes(nd.travelMode())
                # tell the old navigator instance to delete itself
                # so that its map objects will disappear
                if (self._lastNavigator):
                    self._lastNavigator.deleteLater()
                
                nvg = Navigator(self._serviceProvider.routingManager(),
                                self._serviceProvider.searchManager(),
                                self._mapsWidget, nd.destinationAddress(),
                                req)
                nvg.iconPath = self.iconPath
                
                self._lastNavigator = nvg
                nvg.searchError.connect(self._showErrorMessage)
                nvg.routingError.connect(self._showErrorMessage)
                
                self._mapsWidget.statusBar().showText("Route suchen...")
                
                nvg.start()
                
                nvg.finished.connect(self._mapsWidget.statusBar().hide)
                self._mapsWidget.map_().setFocus()
    
    def _showMarkerDialog(self, marker):
        md = MarkerDialog(marker, self)
        if md.exec_() == QDialog.Accepted:
            md.updateMarker()
            self._mapsWidget.map_().setFocus()
    
    def _showSearchDialog(self):
        sd = SearchDialog(self)
        sd.show()
        if sd.exec_() == QDialog.Accepted:
            if self._markerManager:
                self._markerManager.removeSearchMarkers()
                self._markerManager.search(sd.searchTerms(),
                                           sd.radius())
                self._mapsWidget.map_().setFocus()
        return
    
    def onSearchError(self, error, msg):
        print "SearchError: {0}".format(error)
        #print reply
        print error, msg
    
    def _showErrorMessage(self, err, msg):
        QMessageBox.critical(self, 'Error', msg)
        self._mapsWidget.statusBar().hide()
        self._mapsWidget.map_().setFocus()