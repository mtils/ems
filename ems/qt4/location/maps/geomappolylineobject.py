'''
Created on 14.11.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QPen

from ems.qt4.location.maps.geomapobject import GeoMapObject

class GeoMapPolylineObject(GeoMapObject):
    '''
    \brief The QGeoMapPolylineObject class is a QGeoMapObject used to draw
    a segmented line on a map.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps-mapping-objects

    The polyline is specified by a list of at least 2 valid QGeoCoordinate
    instances and a line will be drawn between every adjacent pairs of
    coordinates in the list.
    '''
    
    _path = []
    _pen = QPen
    
    pathChanged = pyqtSignal(list)
    
    penChanged = pyqtSignal(QPen)
    
    def __init__(self, mapData=None):
        '''
        Constructs a new polyline object.
        @param mapData: Optional GeoMapData
        @type mapData: GeoMapData
        '''
        self._path = []
        self._pen = QPen()
        self._pen.setCosmetic(True)
        
        GeoMapObject.__init__(self, mapData)
        self.setUnits(GeoMapObject.RelativeArcSecondUnit)
        self.setTransformType(GeoMapObject.ExactTransform)
        
#        GeoMapObject.__init__(self, mapData)
    
    def type_(self):
        '''
        Returns the type of this map object.
        
        @return: int
        '''
        return GeoMapObject.PolylineType
    
    def setPath(self, path):
        '''
        \property QGeoMapPolylineObject::path
        \brief This property holds the ordered list of coordinates which define the
        segmented line to be drawn by this polyline object.
    
        The default value of this property is an empty list of coordinates.
    
        A line will be drawn between every pair of coordinates which are adjacent in
        the list.
    
        Invalid coordinates in the list will be ignored, and if the list of
        coordinates contains less than 2 valid coordinates then the polyline object
        will not be displayed.
        
        @param path: list of GeoCoordinates
        @type path: list
        '''
        if self._path != path:
            self._path = path
            self.setOrigin(path[0])
            self.pathChanged.emit(self._path)
    
    def path(self):
        '''
        @rtype: list
        '''
        
        return self._path
    
    def setPen(self, pen):
        '''
        \property QGeoMapPolylineObject::pen
        \brief This property holds the pen that will be used to draw this object.
    
        The pen is used to draw the polyline.
    
        The pen will be treated as a cosmetic pen, which means that the width
        of the pen will be independent of the zoom level of the map.
        
        @param pen: The new pen
        @type pen: QPen
        '''
        pen.setCosmetic(False)
        
        if self._pen == pen:
            return
        
        self._pen = pen
        self.penChanged.emit(self._pen)
    
    def pen(self):
        '''
        @rtype: QPen
        '''
        return self._pen
    
    
    
    
    
    
    