'''
Created on 12.12.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSignal, QPoint, Qt
from PyQt4.QtGui import QPen, QBrush, QFont

from ems.qt4.location.maps.geomapobject import GeoMapObject
from ems.qt4.location.geoboundingbox import GeoBoundingBox
from ems.qt4.location.geocoordinate import GeoCoordinate

class GeoMapTextObject(GeoMapObject):
    '''
    \brief The QGeoMapTextObject class is a QGeoMapObject used to draw
    text on a map.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps-mapping-objects

    The text is drawn at a given coordinate on the map.

    The text object is drawn such that the rendered size of the text object is
    independent of the zoom level of the map.
    '''

    _text = ""
    
    _font = QFont()
    
    _pen = QPen()
    
    _brush = QBrush()
    
    _offset = QPoint()
    
    _alignment = Qt.AlignCenter | Qt.AlignVCenter
    
    
    
    penChanged = pyqtSignal(QPen)
    '''This signal is emitted when the pen used to draw the perimeter of this
    rectangle object has changed.

    The new value is \a pen.'''
    
    brushChanged = pyqtSignal(QBrush)
    '''This signal is emitted when the brush used to fill in the interior of
    this rectangle object has changed.

    The new value is \a brush.'''
    
    coordinateChanged = pyqtSignal(GeoCoordinate)
    '''This signal is emitted when the coordinate at which this text
    object will be drawn has changed.

    The new value is \a coordinate.'''
    
    textChanged = pyqtSignal(unicode)
    '''This signal is emitted when the text to be drawn by this text object
    has changed.

    The new value is \a text.'''
    
    fontChanged = pyqtSignal(QFont)
    '''This signal is emitted when the font use to draw this text object
    has changed.

    The new value is \a font.'''
    
    offsetChanged = pyqtSignal(QPoint)
    '''This signal is emitted when the on screen offset from the coordinate at
    which this text object will be drawn has changed.

    The new value is \a offset.'''
    
    alignmentChanged = pyqtSignal(Qt.Alignment)
    '''This signal is emitted when the alignment of this text object has changed.

    The new value is \a alignment.'''
    
    def __init__(self, coordinate=None, text=None, font=None,
                 offset=None, alignment=None, mapData=None):
        '''
        Constructs a new rectangle object.
        @param mapData: Optional GeoMapData
        @type mapData: GeoMapData
        '''
        self._path = []
        self._pen = QPen()
        self._pen.setCosmetic(True)
        self._offset = QPoint(0, 0)
        GeoMapObject.__init__(self, mapData)
        
        if coordinate is not None:
            self.setOrigin(coordinate)
        if text is not None:
            self._text = text
        if font is not None:
            self._font = font
        if offset is not None:
            self._offset = offset
        if alignment is not None:
            self._alignment = alignment
        self.setUnits(GeoMapObject.PixelUnit)
        
    
    def type_(self):
        return GeoMapObject.TextType
    
    def coordinate(self):
        '''
        \property QGeoMapTextObject::coordinate
        \brief This property holds the coordinate at which this text object
        will be rendered.
    
        The default value of this property is an invalid coordinate. While the
        value of this property is invalid the text object will not be displayed.
    
        If QGeoMapTextObject::offset and QGeoMapTextObject::alignment are not set
        the text will be drawn so that it is centered both horizontally and
        vertically around the position of QGeoMapTextObject::coordinate on the
        screen.
        @rtype: GeoCoordinate
        '''
        return self.origin()
    
    def setCoordinate(self, coordinate):
        if self._origin != coordinate:
            self.setOrigin(coordinate)
            self.coordinateChanged.emit(coordinate)
    
    def text(self):
        '''
         \property QGeoMapTextObject::text
        \brief This property holds the text that will be displayed by this text
        object.
    
        The default value of this property is an empty string.
        @rtype: unicode
        '''
        return self._text
    
    def setText(self, text):
        '''
        
        @param text: str
        @type text: str
        '''
        if self._text != text:
            self._text = text
            self.textChanged.emit(text)
    
    def font(self):
        '''
        \property QGeoMapTextObject::font
        \brief This property holds the font that will be used to render the text
        for this text object.
    
        The default value of this property is the application's default font.
    
        It is not necessary to account for the zoom level of the map, since text
        objects are scaled such that they appear to be independent of the zoom
        level.
        @rtype: QFont
        '''
        return self._font
    
    def setFont(self, font):
        '''
        @param font: The new font
        @type font: QFont
        '''
        if self._font != font:
            self._font = font
            self.fontChanged.emit(font)
    
    
    
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
    
    def offset(self):
        '''
        \property QGeoMapTextObject::offset
        \brief This property holds the offset in pixels from the screen position of
        QGeoMapTextObject::coordinate at which the text will be rendered when
        drawing this text object.
    
        The default value of this property is QPoint(0,0).
        @rtype: QPoint
        '''
        return QPoint(self._offset.x(), self._offset.y())
    
    def setOffset(self, offset):
        '''
        @param offset: New offset
        @type offset: QPoint
        '''
        if self._offset != offset:
            self._offset = offset
            self.offsetChanged.emit(offset)
    
    def alignment(self):
        '''
        \property QGeoMapTextObject::alignment
        \brief This property holds the alignment options used to align the
        text when drawing this text object.
    
        The default value of this property will align the text so that it is
        centered both horizontally and vertically around the point that is
        QGeoMapTextObject::offset pixels away from the position of
        QGeoMapTextObject::coordinate on the screen.
    
        Using
        \code
        textObject->setAlignment(Qt::AlignLeft | Qt::AlignVCenter);
        \endcode
        will place the text so that the point halway up the left edge of
        the text is at the anchor point defined by
        QGeoMapTextObject::offset and QGeoMapTextObject::coordinate.
    
        The alignment property is a flag, so using
        \code
        textObject->setAlignment(Qt::AlignLeft);
        \endcode
        may alter the vertical alignment as well.
    
        The Qt::AlignVertical_Mask and Qt::AlignHorizontal_Mask enum
        values can be used to alter one component of the alignment
        independent of the other.
        \code
        textObject->setAlignment(Qt::AlignLeft | (textObject->alignment() & Qt::AlignVertical_Mask));
        \endcode
    
        The alignment does not take the width of QGeoMapTextObject::pen into
        consideration.
        @rtype: Qt.Alignment
        '''
        return self._alignment
    
    def setAlignment(self, alignment):
        '''
        @param alignment: new alignment
        @type alignment: Qt.Alignment
        '''
        if self._alignment != alignment:
            self._alignment = alignment
            self.alignmentChanged.emit(self._alignment)
    
    