'''
Created on 05.11.2011

@author: michi
'''
from PyQt4.QtCore import pyqtProperty, pyqtSignal
from PyQt4.QtGui import QPen, QBrush

from geomapobject import GeoMapObject #@UnresolvedImport
from ems.qt4.location.geocoordinate import GeoCoordinate
from ems.qt4.location.geoboundingcircle import GeoBoundingCircle

class GeoMapCircleObject(GeoMapObject):
    '''
    \brief The QGeoMapCircleObject class is a QGeoMapObject used to draw the region
    within a given distance of a coordinate.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps-mapping-objects

    The circle is specified by either a valid QGeoBoundingCircle instance or a
    valid QGeoCoordinate instance and a qreal with value greater than 0.0,
    which represent the center of the circle and the radius of the circle in
    metres respectively.

    The circle may appear as an ellipse on maps which use the Mercator
    projection. This is done so that the circle accurately covers all points at
    a distance of the radius or less from the center.
    '''
    _center = GeoCoordinate()
    _radius = 0
    _pen = QPen()
    _brush = QBrush()
    _pointCount = 0
    _circle = GeoBoundingCircle()
    
    centerChanged = pyqtSignal(GeoCoordinate)
    '''This signal is emitted when the center of the circle object has
    changed.

    The new value is \a center.'''
    
    radiusChanged = pyqtSignal(int)
    '''his signal is emitted when the radius of the circle object has
    changed.

    The new value is \a radius.'''
    
    penChanged = pyqtSignal(QPen)
    '''This signal is emitted when the pen used to draw the edge of
    the circle object has changed.

    The new value is \a pen.'''
    
    brushChanged = pyqtSignal(QBrush)
    '''This signal is emitted when the brush used to fill the inside of
    the circle object has changed.

    The new value is \a brush.'''

    def __init__(self, circleOrCenter=None, radius=None, mapData=None):
        
        self._pointCount = 120
        self._pen = QPen()
        self._pen.setCosmetic(True)
        self._center = GeoCoordinate()
        self._radius = 0
        self._brush = QBrush()
        self._circle = GeoBoundingCircle()
        GeoMapObject.__init__(self, mapData)
        
        self.setUnits(GeoMapObject.MeterUnit)
        
        self.setTransformType(self.ExactTransform)
        
        if isinstance(circleOrCenter, GeoBoundingCircle):
            self._circle = circleOrCenter
        elif isinstance(circleOrCenter, GeoCoordinate):
            self._circle = GeoBoundingCircle()
            self.setOrigin(circleOrCenter)
        if radius is not None:
            self.setRadius(radius)
            
    def type_(self):
        return GeoMapObject.CircleType
    
    
    def pen(self):
        '''
        \brief This property holds the pen that will be used to draw this object.

        The pen is used to draw an outline around the circle. The circle is
        filled using the QGeoMapCircleObject::brush property.
    
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
        oldPen = self._pen
        
        if oldPen == newPen:
            return
        self._pen = newPen
        self.penChanged.emit(newPen)
    
    def contains(self, coordinate):
        '''
        @param coordinate: The coordinate
        @type coordinate: GeoCoordinate
        @rtype: bool
        '''
        return self._circle.contains(coordinate)
    
    
    def brush(self):
        '''
        \property QGeoMapCircleObject::brush
        \brief This property holds the brush that will be used to draw this object.
    
        The brush is used to fill in circle.
    
        The outline around the perimeter of the circle is drawn using the
        QGeoMapCircleObject::pen property.
        @rtype: QBrush
        '''
        return self._brush
    
    
    def setBrush(self, brush):
        '''
        @param brush: The new brush
        @type brush: QBrush
        '''
        if self._brush != brush:
            self._brush = brush
            self.brushChanged.emit(brush)
    
    
    def pointCount(self):
        '''
        \property QGeoMapCircleObject::pointCount
        \brief This property holds the number of vertices used in an approximate polygon.
    
        \since 1.2
    
        For a circle using ExactTransform, this property describes the number
        of sides that should be used to generate a polygonal approximation which
        is then transformed vertex-by-vertex into screen coordinates.
        @rtype: int
        '''
        return self._pointCount
    
    
    def setPointCount(self, pointCount):
        '''
        @param pointCount: The new pointCount
        @type pointCount: int
        '''
        self._pointCount = pointCount
    
    
    def circle(self):
        '''
        Returns a QGeoBoundingCircle instance which corresponds to the circle that
        will be drawn by this object.
    
        This is equivalent to
        \code
            QGeoMapCircleObject *object;
            // setup object
            QGeoBoundingCircle(object->center(), object->radius());
        \endcode
        
        @rtype: GeoBoundingCircle
        '''
        return self._circle
    
    
    def setCircle(self, circle):
        '''
        Sets the circle that will be drawn by this object to \a circle.

        This is equivalent to
        \code
            QGeoMapCircleObject *object;
            // setup object
            object->setCenter(circle.center());
            object->setRadius(circle.radius());
        \endcode
        
        @param circle: The new Circle
        @type circle: GeoBoundingCircle
        '''
        oldCircle = self._circle
        if oldCircle == circle:
            return
        
        self._circle = circle
        self.setOrigin(circle.center())
        self.setRadius(circle.radius())
        
        if oldCircle.center() != self._circle.center():
            self.centerChanged.emit(self._circle.center())
        
        if oldCircle.radius() != self._circle.radius():
            self.radiusChanged.emit(self._circle.radius())
        
    
    def center(self):
        '''\property QGeoMapCircleObject::center

        \brief This property holds the coordinate of the center of the circle to be
        drawn by this circle object.
    
        The default value of this property is an invalid coordinate.  While the
        value of this property is invalid the circle object will not be displayed.
        @rtype: GeoCoordinate
        '''
        return self._center
    
    
    def setCenter(self, center):
        '''
        @param center: The new center
        @type center: GeoCoordinate
        '''
        if self._circle.center() != center:
            self._circle.setCenter(center)
            self.setOrigin(center)
            self.centerChanged.emit(center)
    
    def radius(self):
        '''
        \property QGeoMapCircleObject::radius
        \brief This property holds the radius in metres of the circle that will be
        drawn by this circle object.
    
        The default value of this property is -1.0. While the value of this
        property is not greater than 0 the circle object will not be displayed.
        @rtype: int
        '''
        return self._circle.radius()
    
    def setRadius(self, radius):
        '''
        @param radius: The new radius
        @type radius: int
        '''
        if self._circle.radius() != radius:
            self._circle.setRadius(radius)
            self.radiusChanged.emit(radius)
    
    