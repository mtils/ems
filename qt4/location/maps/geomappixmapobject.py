'''
Created on 29.10.2011

@author: michi
'''

from PyQt4.QtCore import QPoint, pyqtSignal
from PyQt4.QtGui import QPixmap

from geomapobject import GeoMapObject #@UnresolvedImport
from ems.qt4.location.geocoordinate import GeoCoordinate #@UnresolvedImport

class GeoMapPixmapObject(GeoMapObject):
    '''
    \brief The QGeoMapPixmapObject class is a QGeoMapObject used to draw
    a pixmap on a map.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps-mapping-objects

    The pixmap object is rendered such that the upper left corner of
    QGeoMapPixmapObject::pixmap will be drawn QGeoMapPixmapObject::offset
    pixels away from the position of QGeoMapPixmapObject::coordinate on the
    map.
    '''
    coordinateChanged = pyqtSignal(GeoCoordinate)
    '''This signal is emitted when the coordinate at which the pixmap
    should be drawn has changed.

    The new value will be \a coordinate.'''
    
    pixmapChanged = pyqtSignal(QPixmap)
    '''This signal is emitted when the pixmap associated with this
    pixmap object has changed.

    The new value will be \a pixmap.'''
    
    offsetChanged = pyqtSignal(QPoint)
    '''This signal is emitted when the on-screen offset from the coordinate
    at which this pixmap object should be drawn has changed.

    The new value will be \a offset.'''
    
    def __init__(self, coordinate=None, offset=None, pixmap=None):
        '''
        Constructs a new pixmap object which will draw the pixmap \a pixmap at an
        offset of \a offset pixels from the coordinate \a coordinate.
        
        @param coordinate: Optional GeoCoordinate
        @type coordinate: GeoCoordinate
        @param offset: Optional QPoint for offset
        @type offset: QPoint
        @param pixmap: Optional Pixmap
        @type pixmap: QPixmap
        '''
        GeoMapObject.__init__(self)
        
        if coordinate is not None:
            self.setOrigin(coordinate)
            
        if pixmap is None:
            pixmap = QPixmap()
            
        if offset is None:
            offset = QPoint(0, 0)
            
        self._pixmap = pixmap
        self._offset = offset
    
    def type_(self):
        return GeoMapObject.PixmapType
    
    def coordinate(self):
        '''
        \property QGeoMapPixmapObject::coordinate
        \brief This property holds the coordinate that specifies where the pixmap
        will be drawn by this pixmap object.
    
        The default value of this property is an invalid coordinate. While the
        value of this property is invalid the pixmap object will not be displayed.
        @rtype: GeoCoordinate
        '''
        return self.origin()
    
    def setCoordinate(self, coordinate):
        '''
        @see: coordinate()
        @param coordinate:
        @type coordinate:
        '''
        if self._origin != coordinate:
            self.setOrigin(coordinate)
            self.coordinateChanged.emit(coordinate)
    
    def pixmap(self):
        '''
        \property QGeoMapPixmapObject::pixmap
        \brief This property holds the pixmap that will be drawn by this pixmap
        object.
    
        The default value of this property is a null pixmap. While the value of
        this property is the null pixmap the pixmap object will not be displayed.
    
        The pixmap will be drawn such that the upper left corner of the pixmap
        will be drawn QGeoMapPixmapObject::offset pixels away from the position of
        QGeoMapPixmapObject::coordinate on the map.
        @rtype: QPixmap
        '''
        return self._pixmap
    
    def setPixmap(self, pixmap):
        '''
        @see: pixmap()
        @param pixmap: The pixmap, what else?
        @type pixmap: QPixmap
        '''
        if self._pixmap.isNull() and pixmap.isNull():
            return
        
        if (self._pixmap.isNull() and not pixmap.isNull()) \
           or (not self._pixmap.isNull() and pixmap.isNull())\
           or (self._pixmap.toImage() != pixmap.toImage()):
            self._pixmap = pixmap
            self.pixmapChanged.emit(pixmap)
    
    def offset(self):
        '''
        \property QGeoMapPixmapObject::offset
        \brief This property holds the offset in pixels at which the pixmap will be
        drawn by this pixmap object.
    
        The default value of this property is QPoint(0, 0). If this value is not
        changed the upper left coordinate of the pixmap will be drawn at the
        coordinate specified by QGeoMapPixmapObject::coordinate.
    
        The offset is in pixels and is independent of the zoom level of the map.
        The offset property is provided so that pixmaps such as arrows can be drawn
        with the point of the arrow placed exactly on the associated coordinate.
        
        @rtype: QPoint
        '''
        return self._offset
    
    def setOffset(self, offset):
        '''
        @see: offset()
        @param offset: the offset
        @type offset: QPoint
        '''
        if self._offset != offset:
            self._offset = offset
        self.offsetChanged.emit(offset)