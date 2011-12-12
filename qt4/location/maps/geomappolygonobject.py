'''
Created on 14.11.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QPen, QBrush
from ems.qt4.location.maps.geomapobject import GeoMapObject

class GeoMapPolygonObject(GeoMapObject): 
    '''
    \brief The QGeoMapPolygonObject class is a QGeoMapObject used to draw
    a polygon on a map.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps-mapping-objects

    The polygon is specified by a set of at least 3 valid QGeoCoordinate
    instances listed in the same order in which the coordinates would be
    traversed when traveling around the border of the polygon.
    '''
    _path = []
    
    _pen = QPen
    
    _brush = QBrush
    
    pathChanged = pyqtSignal(list)
    '''This signal is emitted when the ordered list of coordinates that define
    the polygon to be drawn by this polygon object has changed.

    The new value is \a path.'''
    
    penChanged = pyqtSignal(QPen)
    '''This signal is emitted when the pen used to draw the edge of this
    polygon object has changed.

    The new value is \a pen.'''
    
    brushChanged = pyqtSignal(QBrush)
    '''This signal is emitted when the brush used to fill in the interior of
    this polygon object has changed.

    The new value is \a brush.'''
    
    def __init__(self, mapData=None):
        self._brush = QBrush()
        self._path = []
        self._pen = QPen()
        self._pen.setCosmetic(True)
        GeoMapObject.__init__(self, mapData)
        self.setUnits(GeoMapObject.RelativeArcSecondUnit)
        self.setTransformType(GeoMapObject.ExactTransform)
    
    def type_(self):
        '''
        Returns the type of this map object.
        
        @return: int
        '''
        return GeoMapObject.PolygonType
    
    def setPath(self, path):
        '''
        \property QGeoMapPolygonObject::path
        \brief This property holds the ordered list of coordinates which define the
        polygon to be drawn by this polygon object.
    
        The default value of this property is an empty list of coordinates.
    
        The coordinates should be listed in the order in which they would be
        traversed when traveling around the border of the polygon.
    
        Invalid coordinates in the list will be ignored, and if the list of
        coordinates contains less than 3 valid coordinates then the polygon object
        will not be displayed.
        
        @param path: List of GeoCoordinate objects
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
        \property QGeoMapPolygonObject::pen
        \brief This property holds the pen that will be used to draw this object.
    
        The pen is used to draw an outline around the polygon. The polygon is
        filled using the QGeoMapPolygonObject::brush property.
    
        The pen will be treated as a cosmetic pen, which means that the width
        of the pen will be independent of the zoom level of the map.
        
        @param pen: The new pen
        @type pen: QPen
        '''
        newPen = pen
        newPen.setCosmetic(True)
        if newPen == self._pen:
            return
        
        self._pen = newPen
        self.penChanged.emit(self._pen)
    
    def pen(self):
        '''
        @rtype: QPen
        '''
        return self._pen
    
    def setBrush(self, brush):
        '''
        \property QGeoMapPolygonObject::brush
        \brief This property holds the brush that will be used to draw this object.
    
        The brush is used to fill in polygon.
    
        The outline around the perimeter of the polygon is drawn using the
        QGeoMapPolygonObject::pen property.
        
        @param brush: the new brush
        @type brush: QBrush
        '''
        if self._brush != brush:
            self._brush = brush
            self.brushChanged.emit(self._brush)
    
    def brush(self):
        '''
        @rtype: QBrush
        '''
        return self._brush
    
    