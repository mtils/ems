'''
Created on 29.10.2011

@author: michi
'''
import os.path

from PyQt4.QtCore import QObject, QPoint, Qt, pyqtSignal, QString
from PyQt4.QtGui import QPixmap

from ems.qt4.location.maps.geomappixmapobject import GeoMapPixmapObject
from ems.qt4.location.maps.geosearchmanager import GeoSearchManager
from ems.qt4.location.geoaddress import GeoAddress
from ems.qt4.location.maps.graphicsgeomap import GraphicsGeoMap
from ems.qt4.location.geocoordinate import GeoCoordinate
from ems.qt4.location.maps.geosearchreply import GeoSearchReply
from ems.qt4.location.geoboundingcircle import GeoBoundingCircle
from ems.qt4.location.landmarks.landmark import Landmark

class Marker(GeoMapPixmapObject):
    
    #MarkerType enum
    MyLocationMarker = 0
    SearchMarker = 1
    WaypointMarker = 2
    StartMarker = 3
    EndMarker = 4
    PathMarker = 5
    
    _type = 0
    
    _name = ""
    
    _moveable = False
    
    _address = GeoAddress
    
    _iconPath = u""
    
    coordinateChanged = pyqtSignal(GeoCoordinate)
    
    addressChanged = pyqtSignal(GeoAddress)
    
    nameChanged = pyqtSignal(QString)
    
    movableChanged = pyqtSignal(bool)
    
    def __init__(self, iconpath, type_):
        GeoMapPixmapObject.__init__(self)
        self._iconPath = iconpath
        
        self.setMarkerType(type_)
        
    
    def setMarkerType(self, type_):
        self._type = type_
        
        if self._type == Marker.MyLocationMarker:
            filename = "mylocation.png"
        elif self._type == Marker.SearchMarker:
            filename = "searchmarker.png"
        elif self._type == Marker.WaypointMarker:
            filename = "waypointmarker.png"
        elif self._type == Marker.StartMarker:
            filename = "startmarker.png"
        elif self._type == Marker.EndMarker:
            filename = "endmarker.png"
        elif self._type == Marker.PathMarker:
            filename = "pathmarker.png"
        
        if self._type == Marker.MyLocationMarker:
            offset = QPoint(-13, -13)
            scale = 25
        else:
            offset = QPoint(-15, -36)
            scale = 30
        
        self.setOffset(offset)
        #print self._iconPath
        filePath = os.path.join(self._iconPath, filename)
        #print filePath
        self.setPixmap(QPixmap(filePath).scaledToWidth(scale,
                                                       Qt.SmoothTransformation))
    
    def address(self):
        return self._address
    
    def setAddress(self, addr):
        if self._address != addr:
            self._address = addr
            self.addressChanged.emit(self._address)
    
    def markerType(self):
        return self._type
    
    def name(self):
        if self._name:
            return self._name
        if self.nokiaName:
            return self.nokiaName
        
    
    def setName(self, name):
        name = QString.fromUtf8(name)
        if name != self._name:
            self._name = name
            self.nameChanged.emit(self._name)
    
    def setMoveable(self, moveable):
        if self._moveable != moveable:
            self._moveable = moveable
            self.movableChanged.emit(self._moveable)
    
    
    
        

class MarkerManager(QObject):
    
    searchError = pyqtSignal(int, str)
    
    searchFinished = pyqtSignal()
    
    _myLocation = Marker
    
    _searchMarkers = []
    
    #a reverse geocode request is currently running
    _revGeoCodeRunning = False
    
    '''a request is currently running, and my location has changed
       since it started (ie, the request is stale)'''
    _myLocHasMoved = False
    
    _map = GraphicsGeoMap
    
    _status = None
    
    _searchManager = GeoSearchManager
    
    _forwardReplies = set()
    
    _reverseReplies = set()
    
    
    def __init__(self, iconPath, sm, myLocationCoord = None, parent=None):
        '''
        @param sm: GeoSearchManager
        @type sm: GeoSearchManager
        @param parent: parent QObject
        @type parent: QObject
        '''
        QObject.__init__(self, parent)
        self._searchManager = sm
        self._status = None
        self._revGeoCodeRunning = False
        self._myLocHasMoved = False
        self._iconPath = iconPath
        
        if myLocationCoord is None:
            myLocationCoord = GeoCoordinate(48.525759, 8.5659) # Pfalzgrafenweiler
        self._myLocation = Marker(iconPath, Marker.MyLocationMarker)
        self._myLocation.setOrigin(myLocationCoord)
        self._myLocation.setName("Heimatfleck")
        
        self._myLocation.coordinateChanged.connect(self._myLocationChanged)
        self._searchManager.finished.connect(self._replyFinished)
        self._searchManager.finished.connect(self._reverseReplyFinished)
    
    def setStatusBar(self, bar):
        self._status = bar
    
    def setMap(self, map_):
        self._map = map_
        self._map.addMapObject(self._myLocation)
    
    def setMyLocation(self, coord):
        self._myLocation.setCoordinate(coord)
    
    def search(self, query, radius=-1):
        if radius > 0:
            boundingCircle = GeoBoundingCircle(self._myLocation.coordinate(),
                                               radius)
            reply = self._searchManager.search(query,
                                               GeoSearchManager.SearchAll,
                                               -1, 0, boundingCircle)
        else:
            reply = self._searchManager.search(query)
        
        self._forwardReplies.add(reply)
        
        if self._status:
            self._status.showText("Suchen...")
        
        if reply.isFinished():
            self._replyFinished(reply)
        else:
            reply.errorOccured.connect(self.searchError)
    
    def removeSearchMarkers(self):
        for m in self._searchMarkers:
            self._map.removeMapObject(m)
            del m
    
    def myLocation(self):
        return self._myLocation.coordinate()
    
    def _myLocationChanged(self, coord):
        if self._revGeoCodeRunning:
            self._myLocHasMoved = True
        else:
            reply = self._searchManager.reverseGeoCode(coord)
            self._reverseReplies.add(reply)
            self._myLocHasMoved = False
            
            if reply.isFinished():
                self._revGeoCodeRunning = False
                self._reverseReplyFinished(reply)
            else:
                self._revGeoCodeRunning = True
    
    def _reverseReplyFinished(self, reply):
        if reply not in self._reverseReplies:
            return
        
        if len(reply.places()) > 0:
            place = reply.places()[0]
            self._myLocation.setAddress(place.address())
        
        self._revGeoCodeRunning = False
        if self._myLocHasMoved:
            self._myLocationChanged(self._myLocation.coordinate())
        
        self._reverseReplies.remove(reply)
        reply.deleteLater()
    
    def _replyFinished(self, reply):
        if reply not in self._forwardReplies:
            return
        
        for place in reply.places():
            m = Marker(self._iconPath, Marker.SearchMarker)
            m.setCoordinate(place.coordinate())
            
            if place.isLandmark():
                lm = Landmark(place)
                m.setName(lm.name())
            else:
                try:
                    m.setName(m.nokiaName)
                except AttributeError:
                    m.setName("{0}, {1}".format(place.address().street(),
                                                place.address().city()))
            
            m.setAddress(place.address())
            m.setMoveable(False)
            
            self._searchMarkers.append(m)
            
            if self._map:
                self._map.addMapObject(m)
                # also zoom out until marker is visible
                while not self._map.viewport().contains(place.coordinate()):
                    self._map.setZoomLevel(self._map.zoomLevel() -1)
        
        self._forwardReplies.remove(reply)
        reply.deleteLater()
        
        self.searchFinished.emit()
        if self._status:
            self._status.hide()
    
    def _searchError(self, msg, fett=None):
        print msg, fett
    
    def searchManager(self):
        return self._searchManager
