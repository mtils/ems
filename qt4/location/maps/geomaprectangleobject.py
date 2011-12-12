'''
Created on 12.12.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QPen, QBrush

from ems.qt4.location.maps.geomapobject import GeoMapObject
from ems.qt4.location.geoboundingbox import GeoBoundingBox
from ems.qt4.location.geocoordinate import GeoCoordinate

class GeoMapRectangleObject(GeoMapObject):
    '''
    \brief The QGeoMapRectangleObject class is a QGeoMapObject used to draw
    a rectangular region on a map.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps-mapping-objects

    The rectangle is specified by either a valid QGeoBoundingBox instance or
    a pair of valid QGeoCoordinate instances which represent the top left and
    bottom right coordinates of the rectangle respectively.
    '''
    
    _bounds = GeoBoundingBox()
    
    _pen = QPen()
    
    _brush = QBrush()
    
    topLeftChanged = pyqtSignal(GeoCoordinate)
    '''This signal is emitted when the top left coordinate of this rectangle
    object has changed.

    The new value is \a topLeft.'''
    
    bottomRightChanged = pyqtSignal(GeoCoordinate)
    '''This signal is emitted when the bottom right coordinate of this rectangle
    object has changed.

    The new value is \a bottomRight.'''
    
    penChanged = pyqtSignal(QPen)
    '''This signal is emitted when the pen used to draw the perimeter of this
    rectangle object has changed.

    The new value is \a pen.'''
    
    brushChanged = pyqtSignal(QBrush)
    '''This signal is emitted when the brush used to fill in the interior of
    this rectangle object has changed.

    The new value is \a brush.'''
    
    def __init__(self, boundingBox=None, mapData=None):
        '''
        Constructs a new rectangle object.
        @param mapData: Optional GeoMapData
        @type mapData: GeoMapData
        '''
        self._path = []
        self._pen = QPen()
        self._pen.setCosmetic(True)
        GeoMapObject.__init__(self, mapData)
        self.setUnits(GeoMapObject.AbsoluteArcSecondUnit)
        self.setTransformType(GeoMapObject.ExactTransform)
        self._bounds = boundingBox
    
    def type_(self):
        return GeoMapObject.RectangleType
    
    def bounds(self):
        '''
         Returns a QGeoBoundingBox instance which corresponds to the rectangle that
        will be drawn by this object.
    
        This is equivalent to
        \code
            QGeoMapRectangleObject *object;
            // setup object
            QGeoBoundingBox(object->topLeft(), object->bottomRight());
        \endcode
        @rtype: GeoBoundingBox
        '''
        return self._bounds
    
    def setBounds(self, bounds):
        '''
        Sets the rectangle that will be drawn by this object to \a bounds.

        This is equivalent to
        \code
            QGeoMapRectangleObject *object;
            // setup object
            object->setTopLeft(bounds.topLeft());
            object->setBottomRight(bounds.bottomRight());
        \endcode
        
        @param bounds: The new bounds
        @type bounds: GeoBoundingBox
        '''
        oldBounds = self._bounds
        
        if oldBounds == bounds:
            return
        
        self._bounds = bounds
        
        if self._bounds.topLeft() != oldBounds.topLeft():
            self.topLeftChanged.emit(self._bounds.topLeft())
        
        if self._bounds.bottomRight() != oldBounds.bottomRight():
            self.bottomRightChanged.emit(self._bounds.bottomRight())
    
    def topLeft(self):
        '''
        \property QGeoMapRectangleObject::topLeft
        \brief This property holds the top left coordinate of the rectangle to be
        drawn by this rectangle object.
    
        The default value of this property is an invalid coordinate.  While
        the value of this property is invalid the rectangle object will not be
        displayed.
        @rtype: GeoCoordinate
        '''
        return self._bounds.topLeft()
    
    def setTopLeft(self, topLeft):
        '''
        @param topLeft: New topleft
        @type topLeft: GeoCoordinate
        '''
        if self._bounds.topLeft() != topLeft:
            self._bounds.setTopLeft(topLeft)
            self.topLeftChanged.emit(self._bounds.topLeft)
    
    def bottomRight(self):
        '''
         \property QGeoMapRectangleObject::bottomRight
        \brief This property holds the bottom right coordinate of the rectangle to
        be drawn by this rectangle object.
    
        The default value of this property is an invalid coordinate.  While
        the value of this property is invalid the rectangle object will not be
        displayed.
        @rtype: GeoCoordinate
        '''
        return self._bounds.bottomRight()
    
    def setBottomRight(self, bottomRight):
        if self._bounds.bottomRight() != bottomRight:
            self._bounds.setBottomRight(bottomRight)
            self.bottomRightChanged.emit(self._bounds.bottomRight())
    
    def pen(self):
        '''
        \property QGeoMapRectangleObject::pen
        \brief This property holds the pen that will be used to draw this object.
    
        The pen is used to draw an outline around the rectangle. The rectangle is
        filled using the QGeoMapRectangleObject::brush property.
    
        The pen will be treated as a cosmetic pen, which means that the width
        of the pen will be independent of the zoom level of the map.
        @rtype: QPen
        '''
        return self._pen
    
    def setPen(self, pen):
        '''

        @param pen: The new pen
        @type pen: QPen
        '''
        newPen = pen
        newPen.setCosmetic(True)
        if self._pen == newPen:
            return
        
        self._pen = newPen
        self.penChanged.emit(self._pen)
    
    def brush(self):
        '''
        \property QGeoMapRectangleObject::brush
        \brief This property holds the brush that will be used to draw this object.
    
        The brush is used to fill in rectangle.
    
        The outline around the perimeter of the rectangle is drawn using the
        QGeoMapRectangleObject::pen property.
        @rtype: QBrush
        '''
        return self._brush
    
    def setBrush(self, brush):
        if self._brush != brush:
            self._brush = brush
            self.brushChanged.emit(brush)