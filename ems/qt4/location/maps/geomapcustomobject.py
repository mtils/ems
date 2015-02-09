'''
Created on 06.11.2011

@author: michi
'''
from PyQt4.QtCore import QPoint, pyqtSignal
from PyQt4.QtGui import QGraphicsItem

from geomapobject import GeoMapObject #@UnresolvedImport

class GeoMapCustomObject(GeoMapObject):
    '''
    \brief The QGeoMapCustomObject class is a QGeoMapObject used to draw
    a pixmap on a map.

    \inmodule QtLocation

    \ingroup maps-mapping-objects
    \since 1.2

    Any arbitrary QGraphicsItem can be associated with a QGeoMapCustomObject, and to
    this end it contains support for interpreting the coordinates of the
    QGraphicsItem in a variety of different ways.

    For example, the following code creates a QGraphicsEllipseItem and a
    QGeoMapCustomObject to display it. The EllipseItem extends from the origin point,
    out 20 meters to the east and 30 metres south.

    \code
    QGraphicsEllipseItem *ellipseItem = new QGraphicsEllipseItem;
    ellipseItem->setRect(0, 0, 20, 30);

    QGeoMapCustomObject *mapObject = new QGeoMapCustomObject;
    mapObject->setGraphicsItem(ellipseItem);
    mapObject->setUnits(QGeoMapObject::MeterUnit);
    mapObject->setOrigin(QGeoCoordinate(-27.5796, 153.1));
    \endcode

    \section2 Units and coordinates

    The local units and coordinates of the QGraphicsItem are transformed
    onto the map based on the \a units, \a origin, \a transformType and
    \a transform properties. Several systems are available, including
    pixels, meters and seconds of arc.

    It should be noted that both pixel and meter coordinate systems are south-
    oriented (ie, positive Y axis faces south on the map). However, the
    RelativeArcSeconds unit system faces north to align with the standard
    latitude grid. The Y axis can be flipped if necessary by making use of the
    GraphicsItem's \a transform property

    \code
    QTransform northFlip;
    northFlip.scale(0, -1);

    ellipseItem->setTransform(northFlip);
    \endcode

    \section2 Transform methods

    Normally, the GraphicsItem will be transformed into map coordinates using
    a bilinear interpolation. Another option is the ExactTransform, which
    converts the GraphicsItem exactly into map coordinates, but is only available
    for certain subclasses of QGraphicsItem. Other interpolation methods may
    be provided in future for greater accuracy near poles and in different
    map projections, without the limitations of ExactTransform.

    Calling setUnits() or setting the units property will result in the
    default value of transformType being restored. See QGeoMapObject::transformType
    for more details.

    \section2 Caveats

    Other than the coordinate system features, there are a few differences
    with using QGraphicsItems on a map compared to using them on a standard
    QGraphicsScene. One of the most important of these is the use of the
    \a update() function. When an application changes anything that has an
    effect upon the appearance, size, shape etc of the QGraphicsItem, it
    must call \a QGeoMapCustomObject::update() to ensure that the map is updated.

    Another is the use of child items of a QGraphicsItem. These are supported
    in more or less the same manner as in QGraphicsScene, with the exception
    of use in concert with \a ExactTransform -- any object with transformType
    set to \a ExactTransform will not have children of its QGraphicsItem drawn
    on the map.
    
    '''
    
    triggerUpdate = pyqtSignal()
    graphicsItemChanged = pyqtSignal(QGraphicsItem)
    '''This signal is emitted when the graphics item which this custom object
    draws is changed.

    The new value will be \a graphicsItem.'''
    
    offsetChanged = pyqtSignal(QPoint)
    '''This signal is emitted when the on-screen offset from the coordinate 
    at which this custom object should be drawn has changed.

    The new value will be \a offset.'''
    
    def __init__(self, coordinate=None, offset=None):
        '''
        @param coordinate: Optional GeoCoordinate
        @type coordinate: GeoCoordinate
        @param offset: The offset
        @type offset: QPoint
        '''
        GeoMapObject.__init__(self)
        if coordinate is not None:
            self.setOrigin(coordinate)
            
        self._graphicsItem = None#QGraphicsItem()
        self._offset = offset
        
    
    def type_(self):
        return GeoMapObject.CustomType
    
    def update(self):
        self.triggerUpdate.emit()
        
    def graphicsItem(self):
        '''
        \property QGeoMapCustomObject::graphicsItem
        \brief This property holds the graphics item which will
        be drawn by this custom object.
    
        If the graphics item is 0 then nothing will be drawn.
        @rtype: QGraphicsItem
        '''
        return self._graphicsItem
    
    def setGraphicsItem(self, graphicsItem):
        '''
        \property QGeoMapCustomObject::graphicsItem
        \brief This property holds the graphics item which will
        be drawn by this custom object.
    
        If the graphics item is 0 then nothing will be drawn.
        
        @param graphicsItem: The new graphicsitem
        @type graphicsItem: QGraphicsItem
        '''
        if self._graphicsItem == graphicsItem:
            return
        
        self._graphicsItem = graphicsItem
        self.graphicsItemChanged.emit(graphicsItem)
    
    def offset(self):
        '''
        \property QGeoMapCustomObject::offset
        \brief This property holds the offset in pixels at which the graphics
        item will be drawn by this custom object.
        
        The default value of this property is QPoint(0, 0). If this value is not
        changed the upper left coordinate of the graphics item will be drawn at the
        coordinate specified by QGeoMapCustomObject::coordinate.
        
        The offset is in pixels and is independent of the zoom level of the map.
        @rtype: QPoint
        '''
        return self._offset
    
    def setOffset(self, offset):
        '''
        @see: offset()
        @param offset: the new offset
        @type offset: QPoint
        '''
        if self._offset != offset:
            self._offset = offset
            self.offsetChanged.emit(offset)
    