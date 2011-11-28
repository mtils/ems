'''
Created on 27.11.2011

@author: michi
'''

from PyQt4.QtCore import QObject, pyqtSignal, Qt
from PyQt4.QtGui import QPen

from ems.unittests.qt4.location.maps.marker import Marker
from ems.qt4.location.maps.georoutereply import GeoRouteReply
from ems.qt4.location.maps.geomaprouteobject import GeoMapRouteObject

class Navigator(QObject):
    
    _address = None
    
    _request = None
    
    _routingManager = None
    
    _searchManager = None
    
    _mapsWidget = None
    
    _addressReply = None
    
    _routeReply = None
    
    _routeObject = None
    
    _endMarker = None
    
    _startMarker = None
    
    _firstRoute = None
    
    finished = pyqtSignal()
    
    searchError = pyqtSignal(int, str)
    
    routingError = pyqtSignal(int, str)
    
    def __init__(self, routingManager, searchManager, mapsWidget, address, requestTemplate):
        QObject.__init__(self, None)
        self._routingManager = routingManager
        self._searchManager = searchManager
        self._mapsWidget = mapsWidget
        self._address = address
        self._request = requestTemplate
        self.iconPath = ""
    
    def __del__(self):
        if self._routeObject:
            self._mapsWidget.map_().removeMapObject(self._routeObject)
            del self._routeObject
        if self._endMarker:
            self._mapsWidget.map_().removeMapObject(self._endMarker)
            del self._endMarker
        if self._startMarker:
            self._mapsWidget.map_().removeMapObject(self._startMarker)
            del self._startMarker
    
    def start(self):
        waypoints = self._request.waypoints()
        myLocation = self._mapsWidget.markerManager().myLocation()
        waypoints.append(myLocation)
        self._request.setWaypoints(waypoints)
        
        startMarker = Marker(self.iconPath, Marker.StartMarker)
        startMarker.setCoordinate(myLocation)
        startMarker.setName("Startpunkt")
        
        self._addressReply = self._searchManager.search(self._address)
        if self._addressReply.isFinished():
            self._onAddressSearchFinished()
        else:
            self._addressReply.errorOccured.connect(self.searchError)
            self._addressReply.finished.connect(self.onAddressSearchFinished)
    
    def onAddressSearchFinished(self):
        if len(self._addressReply.places()) <= 0:
            self._addressReply.deleteLater()
            return
        place = self._addressReply.places()[0]
        
        waypoints = self._request.waypoints()
        waypoints.append(place.coordinate())
        self._request.setWaypoints(waypoints)
        
        self._routeReply = self._routingManager.calculateRoute(self._request)
        if self._routeReply.isFinished():
            self.onRoutingFinished()
        else:
            self._routeReply.errorOccured.connect(self.routingError)
            self._routeReply.finished.connect(self.onRoutingFinished)
        
        self._endMarker = Marker(self.iconPath, Marker.EndMarker)
        self._endMarker.setCoordinate(place.coordinate())
        self._endMarker.setAddress(place.address())
        self._endMarker.setName("Ziel")
        self._mapsWidget.map_().addMapObject(self._endMarker)
        
        self._addressReply.deleteLater()
    
    def route(self):
        return self._firstRoute
    
    def onRoutingFinished(self):
        if len(self._routeReply.routes()) <= 0:
            self.routingError.emit(GeoRouteReply.NoError, "No valid routes returned")
            self._routeReply.deleteLater()
            return
        
        route = self._routeReply.routes()[0]
        self._firstRoute = route
        
        routeObject = GeoMapRouteObject()
        routeObject.setRoute(route)
        routeObject.setPen(QPen(Qt.blue, 2.0))
        
        self._mapsWidget.map_().addMapObject(routeObject)
        self.finished.emit()
        self._routeReply.deleteLater()
        
