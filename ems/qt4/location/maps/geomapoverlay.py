'''
Created on 14.11.2011

@author: michi
'''
from ems.qt4.location.maps.geomapdata import GeoMapData

class GeoMapOverlay(object):
    '''
    \brief The QGeoMapOverlay class is used to draw overlays on the map.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps-mapping

    This allows for general drawing to occur in overlays above the map.
    '''
    _mapData = GeoMapData
    
    def __init__(self):
        '''
        Constructs a new map overlay object.
        '''
        object.__init__(self)
        self._mapData = None
    
    def paint(self, painter, option):
        '''
        
        \fn void QGeoMapOverlay::paint(QPainter *painter, const QStyleOptionGraphicsItem *option)
        
        Paints the overlay on \a painter, using the options \a option.
        
        @param painter: The QPainter
        @type painter: QPainter
        @param option: A StyleOption
        @type option: QStyleOptionGraphicsItem
        '''
        raise NotImplementedError("Please implement paint() method")
    
    def setMapData(self, mapData):
        '''
        internal, orignal private
        
        @param mapData: The GeoMapData Obj
        @type mapData: GeoMapData
        '''
        self._mapData = mapData
    
    def mapData(self):
        '''
        Returns the QGeoMapData instance that this overlay is associated, or 0
        if there is not such instance.
    
        The QGeoMapData instance provides access to information such as the
        zoom level and viewport position as well as methods to convert
        screen positions to coordinates and vice-versa.
        @rtype: GeoMapData
        '''
        return self._mapData