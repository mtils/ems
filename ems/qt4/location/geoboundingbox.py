'''
Created on 13.10.2011

@author: michi
'''
from geoboundingarea import GeoBoundingArea #@UnresolvedImport
from geocoordinate import GeoCoordinate #@UnresolvedImport

class GeoBoundingBox(GeoBoundingArea):
    '''
    The QGeoBoundingBox class defines a rectangular geographic area.

    The rectangle is defined in terms of a QGeoCoordinate which specifies the
    top left coordinate of the rectangle and a QGeoCoordinate which specifies
    the bottom right coordinate of the rectangle.

    A bounding box is considered invalid if the top left or bottom right
    coordinates are invalid or if the top left coordinate is south of the
    bottom right coordinate.

    Bounding boxes can never cross the poles.

    Several methods behave as though the bounding box is defined in terms of a
    center coordinate, the width of the bounding box in degrees and the height
    of the bounding box in degrees.

    If the height or center of a bounding box is adjusted such that it would
    cross one of the poles the height is modified such that the bounding box
    touches but does not cross the pole and that the center coordinate is still
    in the center of the bounding box.
    '''
    
    _topLeft = None
    '''The topLeft Coordinate
    @type _topLeft: GeoCoordinate
    '''
    _bottomRight = None
    '''The bottomRight Coordinate
    @type _bottomRight: GeoCoordinate
    '''
    
    def __init__(self, centerOrTopLeftOrBoundingBox=None,
                  degreesWidthOrBottomRight=None,
                  degreesHeight=None):
        if centerOrTopLeftOrBoundingBox is None:
            pass
        if isinstance(degreesWidthOrBottomRight, GeoCoordinate):
            self._topLeft = centerOrTopLeftOrBoundingBox
            self._bottomRight = degreesWidthOrBottomRight
        else:
            if isinstance(centerOrTopLeftOrBoundingBox, GeoBoundingBox):
                self._topLeft = centerOrTopLeftOrBoundingBox.topLeft()
                self._bottomRight = centerOrTopLeftOrBoundingBox.bottomRight()
            else:
#                self.__init__(centerOrTopLeftOrBoundingBox,
#                              centerOrTopLeftOrBoundingBox)
#                self.setWidth(degreesWidthOrBottomRight)
#                self.setHeight(degreesHeight)
                pass
    
    def __ilshift__(self, other):
        '''
        a <<= b
        
        Assigns other to this bounding box and returns a reference to this
        bounding box.
        In C++ this is the = operator, I solved this is python with an
        <<= operator
        
        @param other: Right operand
        @type other: GeoBoundingBox
        @return GeoBoundingBox
        '''
        self._topLeft = other.topLeft()
        self._bottomRight = other.bottomRight()
        return self
    
    def __eq__(self, other):
        '''
        a == b
        
        Returns whether this bounding box is equal to other.
        
        @param other: The other box
        @type other: GeoBoundingBox
        '''
        return ((self._topLeft == other.topLeft()) and
                (self._bottomRight == other.bottomRight()))
    
    def __ne__(self, other):
        '''
        a != b
        
        Returns whether this bounding box is not equal to other.
        
        @param other: The other box
        @type other: GeoBoundingBox
        '''
        return not self.__eq__(other)
    
    
    
    def type_(self):
        '''
        Returns the type of this area.
        
        @return: int
        '''
        return self.BoxType
    
    def isValid(self):
        '''
        Returns whether this bounding area is valid.

        An area is considered to be invalid if some of the data that is required to
        unambiguously describe the area has not been set or has been set to an
        unsuitable value.
        
        @return: bool
        '''
        
        return self._topLeft.isValid() and self._bottomRight.isValid() and \
               self._topLeft.latitude() >= self._bottomRight.latitude()
    
    def isEmpty(self):
        '''
        Returns whether this bounding area is empty.

        An empty area is a region which has a geometrical area of 0.
        
        @return: bool
        '''
        return (not self.isValid()
                or (self._topLeft.latitude() == self._bottomRight.latitude())
                or (self._topLeft.longitude() == self._bottomRight.longitude()))
    
    def setTopLeft(self, topLeft):
        '''
        Sets the top left coordinate of this bounding box to \a topLeft.

        @param topLeft: The topleft coord
        @type topLeft: GeoCoordinate
        '''
        self._topLeft = topLeft
    
    def topLeft(self):
        '''
        Returns the top left coordinate of this bounding box.
        
        @return GeoCoordinate
        '''
        return self._topLeft
    
    def setTopRight(self, topRight):
        '''
        Sets the top right coordinate of this bounding box to topRight.
        
        @param topRight: The topright coord
        @type topRight: GeoCoordinate
        '''
        self._topLeft.setLatitude(topRight.latitude())
        self._bottomRight.setLongitude(topRight.longitude())
    
    def topRight(self):
        '''
        Returns the top right coordinate of this bounding box.
        
        @return: GeoCoordinate
        '''
        
        if not self.isValid():
            return GeoCoordinate()
        
        return GeoCoordinate(self._topLeft.latitude(),
                             self._bottomRight.longitude(),
                             projection=self._topLeft.projection)
    
    def setBottomLeft(self, bottomLeft):
        '''
        Sets the bottom left coordinate of this bounding box to \a bottomLeft.
        
        @param bottomLeft: The bottom left coord
        @type bottomLeft: GeoCoordinate
        '''
        self._bottomRight.setLatitude(bottomLeft.latitude())
        self._topLeft.setLongitude(bottomLeft.longitude())
    
    def bottomLeft(self):
        '''
        Returns the bottom left coordinate of this bounding box.
        
        @return: GeoCoordinate
        '''
        if not self.isValid():
            return GeoCoordinate()
        return GeoCoordinate(self._bottomRight.latitude(),
                             self._topLeft.longitude(),
                             projection=self._topLeft.projection)
    
    def setBottomRight(self, bottomRight):
        '''
        Sets the bottom right coordinate of this bounding box to bottomRight.
        
        @param bottomRight: The bottom right coord
        @type bottomRight: GeoCoordinate
        '''
        self._bottomRight = bottomRight
    
    def bottomRight(self):
        '''
        Returns the bottom right coordinate of this bounding box.
        
        @return: GeoCoordinate
        '''
        return self._bottomRight
    
    def setCenter(self, center):
        '''
        Sets the center of this bounding box to \a center.

        If this causes the bounding box to cross on of the poles the height of the
        bounding box will be truncated such that the bounding box only extends up
        to the pole. The center of the bounding box will be unchanged, and the
        height will be adjusted such that the center point is at the center of the
        truncated bounding box.
        
        @param center: The center coord
        @type center: GeoCoordinate
        '''
        width = self.width()
        height = self.height()
        
        tlLat = center.latitude() + height / 2.0
        tlLon = center.longitude() - width / 2.0
        brLat = center.latitude() - height / 2.0
        brLon = center.longitude() + width / 2.0
        
        if tlLon < -180.0:
            tlLon += 360.0
        if tlLon > 180.0:
            tlLon -= 360.0
        
        if brLon < -180.0:
            brLon += 360.0
        if brLon > 180.0:
            brLon -= 360.0
        
        if tlLat > 90.0:
            brLat = 2 * center.latitude() - 90.0
            tlLat = 90.0
        
        if tlLat < -90.0:
            brLat = -90.0
            tlLat = -90.0
        
        if brLat > 90.0:
            tlLat = 90.0
            brLat = 90.0
        
        if brLat < -90.0:
            tlLat = 2 * center.latitude() + 90
            brLat = -90.0
            
        if width == 360.0:
            tlLon = -180.0
            brLon = 180.0
        
        self._topLeft = GeoCoordinate(tlLat, tlLon, projection=center.projection)
        self._bottomRight = GeoCoordinate(brLat, brLon, projection=center.projection)
    
    def center(self):
        '''
        Returns the center of this bounding box.
        @return GeoCoordinate
        '''
        if not self.isValid():
            return GeoCoordinate()
        
        cLat = (self._topLeft.latitude() + self._bottomRight.latitude()) / 2.0
        cLon = (self._bottomRight.longitude() + self._topLeft.longitude()) / 2.0
        
        if self._topLeft.longitude() > self._bottomRight.longitude():
            cLon = cLon - 180.0
        
        if cLon < -180.0:
            cLon += 360.0
        if cLon > 180.0:
            cLon -= 360.0
        
        return GeoCoordinate(cLat, cLon, projection=self._topLeft.projection)
    
    def setWidth(self, degreesWidth):
        '''
        Sets the width of this bounding box in degrees to degreesWidth.

        If degreesWidth is less than 0.0 or if this bounding box is invalid this
        function does nothing.  To set up the values of an invalid
        QGeoBoundingBox based on the center, width and height you should use
        setCenter() first in order to make the QGeoBoundingBox valid.
    
        If degreesWidth is greater than 360.0 then 360.0 is used as the width,
        the leftmost longitude of the bounding box is set to -180.0 degrees and the
        rightmost longitude of the bounding box is set to 180.0 degrees.
        
        @param degreesWidth: The new width
        @type degreesWidth: float
        '''
        if not self.isValid():
            return
        
        if degreesWidth < 0.0:
            return
        
        if degreesWidth >= 360.0:
            self._topLeft.setLongitude(-180.0)
            self._bottomRight.setLongitude(180.0)
            return
        
        tlLat = self._topLeft.latitude()
        brLat = self._bottomRight.latitude()
        
        c = self.center()
        
        tlLon = c.longitude() - degreesWidth / 2.0
        
        if tlLon < -180.0:
            tlLon += 360.0
        if tlLon > 180.0:
            tlLon -= 360.0
        
        brLon = c.longitude() - degreesWidth / 2.0
        
        if brLon < -180.0:
            brLon += 360.0
        if brLon > 180.0:
            brLon -= 360.0
        
        self._topLeft = GeoCoordinate(tlLat, tlLon, projection=c.projection)
        self._bottomRight = GeoCoordinate(brLat, brLon, projection=c.projection)
    
    def width(self):
        '''
        Returns the width of this bounding box in degrees.

        The return value is undefined if this bounding box is invalid.
        
        @return float
        '''
        
        if not self.isValid():
            return None
        
        result = self._bottomRight.longitude() -  self._topLeft.longitude()
        if result < 0.0:
            result += 360.0
        if result > 360.0:
            result -= 360.0
        
        return result
    
    def setHeight(self, degreesHeight):
        '''
        Sets the height of this bounding box in degrees to degreesHeight.

        If degreesHeight is less than 0.0 or if this bounding box is invalid
        this function does nothing. To set up the values of an invalid
        QGeoBoundingBox based on the center, width and height you should use
        setCenter() first in order to make the QGeoBoundingBox valid.
    
        If the change in height would cause the bounding box to cross a pole
        the height is adjusted such that the bounding box only touches the pole.
    
        This changes is done such that the center coordinate is still at the
        center of the bounding box, which may result in a bounding box with
        a smaller height than might otherwise be expected.
    
        If degreesHeight is greater than 180.0 then 180.0 is used as the height.
        
        @param degreesHeight: The new height
        @type degreesHeight: float
        '''
        if not self.isValid():
            return
        
        if degreesHeight < 0.0:
            return
        
        if degreesHeight >= 180.0:
            degreesHeight = 180.0
        
        tlLon = self._topLeft.longitude()
        brLon = self._bottomRight.longitude()
        
        c = self.center()
        
        tlLat = c.latitude() +  degreesHeight / 2.0
        brLat = c.latitude() + degreesHeight / 2.0
        
        if tlLat > 90.0:
            brLat = 2 * c.latitude() - 90.0
            tlLat = 90.0
        
        if tlLat < -90.0:
            brLat = -90.0
            tlLat = -90.0
        
        if brLat > 90.0:
            tlLat = 90.0
            brLat = 90.0
        
        if brLat < -90.0:
            tlLat = 2 * c.latitude() + 90.0
            brLat = -90.0
        
        self._topLeft = GeoCoordinate(tlLat, tlLon, projection=c.projection)
        self._bottomRight = GeoCoordinate(brLat, brLon, projection=c.projection)
    
    def height(self):
        '''
        Returns the height of this bounding box in degrees.

        The return value is undefined if this bounding box is invalid.
        
        @return: float
        '''
        
        if not self.isValid():
            return None
        
        result = self._topLeft.latitude() - self._bottomRight.latitude()
        if result < 0.0:
            return None
        return result
    
    def contains(self, coordinate):
        '''
        Returns whether the coordinate coordinate is contained within this
        area.
        
        @param coordinate: The coordinate to test
        @type coordinate: GeoCoordinate
        @return: bool
        '''
        if not self.isValid() or not coordinate.isValid():
            return False
        
        if isinstance(coordinate, GeoBoundingBox):
            return (self.contains(coordinate.topLeft())
                    and self.contains(coordinate.topRight())
                    and self.contains(coordinate.bottomLeft())
                    and self.contains(coordinate.bottomRight()))
        
        left = self._topLeft.longitude()
        right = self._bottomRight.longitude()
        top = self._topLeft.latitude()
        bottom = self._bottomRight.latitude()
        
        lon = coordinate.longitude()
        lat = coordinate.latitude()
        
        if lat > top:
            return False
        if lat < bottom:
            return False
        
        if (lat == 90.0) and (top == 90.0):
            return True
        
        if (lat == -90.0) and (bottom == -90.0):
            return True
        
        if left <= right:
            if (lon < left) or (lon > right):
                return False
        else:
            if (lon < left) and (lon > right):
                return False
        return True
    
    def intersects(self, boundingBox):
        '''
        Returns whether the bounding box boundingBox intersects this bounding
        box.
    
        If the top or bottom edges of both bounding boxes are at one of the poles
        the bounding boxes are considered to be intersecting, since the longitude
        is irrelevant when the edges are at the pole.
    
        @param boundingBox: The bounding box which seems to be checked
        @type boundingBox: GeoBoundingBox
        '''
        
        left1 = self._topLeft.longitude()
        right1 = self._bottomRight.longitude()
        top1 = self._topLeft.latitude()
        bottom1 = self._bottomRight.latitude()
        
        left2 = boundingBox.topLeft().longitude()
        right2 = boundingBox.bottomRight().longitude()
        top2 = boundingBox.topLeft().latitude()
        bottom2 = boundingBox.bottomRight.latitude()
        
        if top1 < bottom2:
            return False
        
        if bottom1 > top2:
            return False
        
        if (top1 == 90.0) and (top1 == top2):
            return True
        
        if (bottom1 == -90.0) and (bottom1 == bottom2):
            return True
        
        if left1 < right1:
            if left2 < right2:
                if (left1 > right2) or right1 < left2:
                    return False
            else:
                if (left1 > right2) and (right1 < left2):
                    return False
        else:
            if left2 < right2:
                if (left2 > right1) and (right2 < left1):
                    return False
        return True
    
    def translate(self, degreesLatitude, degreesLongitude):
        '''
        Translates this bounding box by degreesLatitude northwards and \a
        degreesLongitude eastwards.
    
        Negative values of degreesLatitude and degreesLongitude correspond to
        southward and westward translation respectively.
    
        If the translation would have caused the bounding box to cross a pole the
        bounding box will be translated until the top or bottom edge of bounding
        box touches the pole but not further.
         
        @param degreesLatitude: The lat degrees
        @type degreesLatitude: float
        @param degreesLongitude: The lon degrees
        @type degreesLongitude: float
        '''
        
        tlLat = self._topLeft.latitude()
        tlLon = self._topLeft.longitude()
        brLat = self._bottomRight.latitude()
        brLon = self._bottomRight.longitude()
        
        if (tlLat != 90.0) or (brLat != -90.0):
            tlLat += degreesLatitude
            brLat += degreesLatitude
        
        if (tlLon != 180.0) or (brLon != 180.0):
            tlLon += degreesLongitude
            brLon += degreesLongitude
        
        if tlLon < -180.0:
            tlLon += 360.0
        if tlLon > 180.0:
            tlLon -= 360.0
        
        if brLon < 180.0:
            brLon += 360.0
        if brLon > 180.0:
            brLon -= 360.0
        
        if tlLat > 90.0:
            tlLat = 90.0
        
        if tlLat < -90.0:
            tlLat = -90.0
        
        if brLat > 90.0:
            brLat = 90.0
        
        if brLat < -90.0:
            brLat = -90.0
        
        self._topLeft = GeoCoordinate(tlLat, tlLon, projection=self._topLeft.projection)
        self._bottomRight = GeoCoordinate(brLat, brLon, projection=self._topLeft.projection)
    
    def translated(self, degreesLatitude, degreesLongitude):
        '''
        Returns a copy of this bounding box translated by degreesLatitude northwards and 
        degreesLongitude eastwards.
    
        Negative values of degreesLatitude and degreesLongitude correspond to
        southward and westward translation respectively.
    
        @param degreesLatitude: The lat degrees
        @type degreesLatitude: float
        @param degreesLongitude: The lon degrees
        @type degreesLongitude:float
        '''
        result = GeoBoundingBox(self)
        result.translate(degreesLatitude, degreesLongitude)
        return result
    
    def united(self, boundingBox):
        '''
        Returns the smallest bounding box which contains both this bounding box and boundingBox.
        
        @param boundingBox: The bounding box to be united with this
        @type boundingBox: GeoBoundingBox
        '''
        
        result = GeoBoundingBox(self)
        result |= boundingBox
        return result
    
    def __or__(self, boundingBox):
        '''
        self | other
        
        @see self.__ior__
        @type boundingBox: GeoBoundingBox
        '''
        return self.__ior__(boundingBox)
    
    def __ior__(self, boundingBox):
        '''
        self |= other
        
        Returns the smallest bounding box which contains both this bounding box and boundingBox.
        
        @param boundingBox: The right Operand
        @type boundingBox: GeoBoundingBox
        '''
        
        # If non-intersecting goes for most narrow box
        left1 = self._topLeft.longitude()
        right1 = self._bottomRight.longitude()
        top1 = self._topLeft.latitude()
        bottom1 = self._bottomRight.latitude()
    
        left2 = boundingBox.topLeft().longitude()
        right2 = boundingBox.bottomRight().longitude()
        top2 = boundingBox.topLeft().latitude()
        bottom2 = boundingBox.bottomRight().latitude()
        
        top = max(top1, top2)
        bottom = min(bottom1, bottom2)
        
        left = 0.0
        right = 0.0
        
        wrap1 = (left1 > right1)
        wrap2 = (left2 > right2)
        
        if (wrap1 and wrap2) or (not wrap1 and not wrap2):
            left = min(left1, left2)
            right = max(right1, right2)
        else:
            wrapLeft = 0.0
            wrapRight = 0.0
            nonWrapLeft = 0.0
            nonWrapRight = 0.0
            
            if wrap1:
                wrapLeft = left1
                wrapRight = right1
                nonWrapLeft = left2
                nonWrapRight = right2
            else:
                wrapLeft = left2
                wrapRight = right2
                nonWrapLeft = left1
                nonWrapRight = right1
            
            joinWrapLeft = (nonWrapRight >= wrapLeft)
            joinWrapRight = (nonWrapLeft <= wrapRight)
            
            if joinWrapLeft:
                if joinWrapRight:
                    left = -180.0;
                    right = 180.0;
                else:
                    left = nonWrapLeft
                    right = wrapRight
            else:
                if joinWrapRight:
                    left = wrapLeft
                    right = nonWrapRight
                else:
                    wrapRightDistance = nonWrapLeft - wrapRight
                    wrapLeftDistance = wrapLeft - nonWrapRight
    
                    if (wrapLeftDistance == wrapRightDistance):
                        left = -180.0
                        right = 180.0
                    elif (wrapLeftDistance < wrapRightDistance):
                        left = nonWrapLeft
                        right = wrapRight
                    else:
                        left = wrapLeft
                        right = nonWrapRight
                        
        if ((left1 == -180) and (right1 == 180.0))\
                or ((left2 == -180) and (right2 == 180.0)):
            left = -180;
            right = 180;
    
        self._topLeft = GeoCoordinate(top, left, projection=self._topLeft.projection);
        self._bottomRight = GeoCoordinate(bottom, right, projection=self._topLeft.projection);
    
        return self;
    
    def __str__(self):
        return "GeoBoundingBox {0}/{1}".format(self._topLeft, self._bottomRight)