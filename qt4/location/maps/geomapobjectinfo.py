'''
Created on 20.10.2011

@author: michi
'''
from PyQt4.QtCore import QObject
from ems.qt4.location.geoboundingbox import GeoBoundingBox #@UnresolvedImport

class GeoMapObjectInfo(QObject):
    '''
    The QGeoMapObjectInfo class is the base class used to define the
    parts of QGeoMapObject and its subclasses that are specific to a
    particular QGeoMapData subclass.

    Most of the mapping functionality is provided by a QGeoMapData subclass,
    including the rendering of the map itself.

    This means that QGeoMapData subclasses need to be able to render each of
    the QGeoMapObject instances and instances of the QGeoMapObject subclasses.

    Furthermore, the need to be able to create and manipulate map objects
    independently from the QGeoMapData instance precludes the use of a set of
    factory methods for creating QGeoMapData specific map objects.

    The QGeoMapObjectInfo class is used to provide the QGeoMapData subclass
    specific behaviours for the map objects in a way which fulfils this need,
    as the QGeoMapObjectInfo instances are only created at the point when a
    map object becomes associated with a QGeoMapData subclass - which is most
    commonly when the object is added to a QGraphicsGeoMap.
    '''
    _mapData = None
    _mapObject = None
    
    def __init__(self, mapData, mapObject):
        '''
        Constructs a new object info instance which will provide the behaviours of
        mapObject which are specific to mapData.
        
        @param mapData: The mapData
        @type mapData: GeoMapData
        @param mapObject: The mapObject
        @type mapObject: GeoMapObject
        '''
        QObject.__init__(self, mapObject)
        self._mapData = mapData
        self._mapObject = mapObject
    
    def init(self):
        '''
        This function is run after the constructor.

        The default implementation does nothing.
        '''
        pass
    
    def windowSizeChanged(self, windowSize):
        '''
        This function is called when the window size of the map changes to
        windowSize.
    
        The default implementation does nothing.
    
        @param windowSize: The new windowsize
        @type windowSize: QSizeF
        '''
        pass
    
    def zoomLevelChanged(self, zoomLevel):
        '''
        This function is called when the zoom level of the map changes to
        zoomLevel.
    
        The default implementation does nothing.
        
        @param zoomLevel: The zoomlevel
        @type zoomLevel: int
        '''
        pass
    
    def centerChanged(self, coordinate):        
        '''
        This function is called when the center of the map changes to
        coordinate.
    
        The default implementation does nothing.
        
        @param coordinate: The center coord
        @type coordinate: GeoCoordinate
        '''
        pass
    
    def zValueChanged(self, zValue):
        '''
        This function is run when the z value of the object changes to \a zValue.

        The default implementation does nothing.
        
        @param zValue: The Z-Val
        @type zValue: int
        '''
        pass
    
    def visibleChanged(self, visible):
        '''
        This function is run when the visible state of the object changes to
        visible.

        The default implementation does nothing.
        
        @param visible: Visibility
        @type visible: bool
        '''
        pass
    
    def selectedChanged(self, selected):
        '''
         This function is run when the selected state of the object changes to
        selected.
    
        The default implementation does nothing.
        
        @param selected: Selected or not
        @type selected: bool
        '''
        pass
    
    def originChanged(self, origin):
        '''
        This function is run when the origin of the object changes to
        origin.
    
        The default implementation does nothing.
        
        @param origin: The origin
        @type origin: GeoCoordinate
        '''
        pass
        
    def unitsChanged(self, units):
        '''
        This function is run when the coordinate units of the object changes to
        units.
    
        The default implementation does nothing.
        
        @param units: The new units
        @type units: int
        '''
        pass
    
    def transformTypeChanged(self, transformType):
        '''
        This function is run when the transform type of the object changes to
        transformType.
    
        The default implementation does nothing.
        
        @param transformType: The transformType
        @type transformType: int
        '''
        pass
    
    def boundingBox(self):
        '''
        Returns a bounding box which contains this map object.

        The default implementation returns an invalid bounding box.
        '''
        return GeoBoundingBox()
    
    def contains(self, coordinate):
        '''
        Returns whether coordinate is contained with the boundary of this
        map object.
    
        The default implementation returns false.
        
        @param coordinate: The coordinate to test
        @type coordinate: GeoCoordinate
        @return: bool
        '''
        return False
    
    def mapData(self):
        '''
        Returns the QGeoMapData instance associated with this info object.
        '''
        return self._mapData
    
    def mapObject(self):
        '''
        Returns the QGeoMapObject instance associated with this info object.
        '''
        return self._mapObject
    
    
        