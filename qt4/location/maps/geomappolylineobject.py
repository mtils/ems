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
        self.setUnits(GeoMapObject.RelativeArcSecondUnit)
        self.setTransformType(GeoMapObject.ExactTransform)
        self._path = []
        self._pen = QPen()
        self._pen.setCosmetic(True)
        GeoMapObject.__init__(self, mapData)
    
    def type_(self):
        '''
        Returns the type of this map object.
        
        @return: int
        '''
        return GeoMapObject.PolylineType
    
    
    
    
    