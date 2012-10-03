'''
Created on 04.11.2011

@author: michi
'''
from PyQt4.QtCore import QRect

class GeoTiledMapRequest(object):
    '''
    \brief The QGeoTiledMapRequest class represents a request for a map tile
    from a tile-based mapping service.

    \inmodule QtLocation

    \ingroup maps-impl-tiled

    \since 1.2

    The tile is specified by a map type, a zoom level, a row and a column.

    At a zoom level of z the world is represented as a 2^z by 2^z grid
    of tiles, and the row and column are relative to the grid of tiles
    for the zoom level of the request.
    '''
    def __init__(self, connectivityModeOrOther=None, mapType=None, zoomLevel=None,
                  row=None, column=None, tileRect=None):
        if isinstance(connectivityModeOrOther, GeoTiledMapRequest):
            self.__ilshift__(connectivityModeOrOther)
            connectivityModeOrOther = 0
        elif connectivityModeOrOther is None:
            connectivityModeOrOther = 0
            
        if mapType is None:
            mapType = 0
        if zoomLevel is None:
            zoomLevel = 0
        if row is None:
            row = -1
        if column is None:
            column = -1
        if tileRect is None:
            tileRect = QRect()
            
        self._zoomLevel = zoomLevel
        self._row = row
        self._column = column
        self._tileRect = tileRect
        self._mapType = mapType
        self._connectivityMode = connectivityModeOrOther
        self._cacheId = ""
        
    def __ilshift__(self, other):
        '''
        self <<= other
        
        replacement for c++ = operator overload
        @param other: GeoTiledMapRequest
        @type other: GeoTiledMapRequest
        '''
        for prop in ('zoomLevel','row','column','tileRect','mapType',
                     'connectivityMode'):
            self.__setattr__('_' + prop, other.__getattribute__(prop)())
    
    
    def __eq__(self, other):
        '''
        self == other
        
        @param other: Another GeoTiledMapRequest
        @type other: GeoTiledMapRequest
        '''
        for prop in ('zoomLevel','row','column','mapType', 'connectivityMode'):
            if not self.__getattribute__('_' + prop) == other.__getattribute__(prop)():
                return False
        
        return True
    
    def cacheId(self):
        
        return "{0}|{1}|{2}|{3}|{4}".format(self._zoomLevel, self._row, self._column, self._mapType, self._connectivityMode)
        #args = (str(int(self._zoomLevel)), str(self._row), str(self._column),
        #    str(self._mapType), str(self._connectivityMode))
        #return "|".join(args)
        
    
#    def __hash__(self):
#        hashList = []
#        for prop in ('_zoomLevel','_row','_column','_mapType', '_connectivityMode'):
#            hashList.append(str(self.__getattribute__(prop)))
#        return "|".join(hashList)
    
    def connectivityMode(self):
        '''
        Returns the connectivity mode of the tile request.
        @rtype: int
        '''
        return self._connectivityMode
    
    def mapType(self):
        '''
        Returns the map type of the requested tile.
        
        @rtype: int
        '''
        return self._mapType
    
    def zoomLevel(self):
        '''
        Returns the zoom level of the requested tile.

        The lower and upper bounds of the zoom level are set by
        the QGeoMappingManager that created this request.
        
        @rtype: int
        '''
        return self._zoomLevel
    
    def row(self):
        '''
        Returns the row of the requested tile.

        At a zoom level of z the world is represented as a 2^z by 2^z grid
        of tiles, and so the row will be between 0 and 2^z - 1.
        
        @rtype: int
        '''
        return self._row
    
    def column(self):
        '''
        Returns the column of the requested tile.

        At a zoom level of z the world is represented as a 2^z by 2^z grid
        of tiles, and so the column will be between 0 and 2^z - 1.
        
        @rtype: int
        '''
        return self._column
    
    def tileRect(self):
        '''
        Returns the rectangle that the tile covers on the map at the maximum zoon
        level.
    
        At a zoom level of z the world is represented as a 2^z by 2^z grid of
        tiles. If m is the maximum zoom level and the tiles are t by t pixel
        squares, then the entire world could be viewed as a 2^m * t by 2^m * t
        pixel image.
    
        The rectangle returned is specified relative to the pixel coordinates of
        the map at the maximum zoom level.
        
        @rtype: QRect
        '''
        return self._tileRect
    
    
        
        
    