'''
Created on 04.11.2011

@author: michi
'''
from PyQt4.QtCore import QSize

from ems.qt4.location.maps.geomappingmanagerengine import GeoMappingManagerEngine 
from geotiledmapdata import GeoTiledMapData #@UnresolvedImport

class GeoTiledMappingManagerEngine(GeoMappingManagerEngine):
    '''
    \brief The QGeoTiledMappingManagerEngine class is provided to make writing
    Qt Maps and Navigation API plugins for tiled based mapping services easier.

    \inmodule QtLocation

    \ingroup maps-impl-tiled

    \since 1.2

    Subclasses of QGeoTiledMappingManagerEngine need to provide an implementation
    of getTileImage().

    It is important that the function setTileSize() is called before
    getTileImage() to ensure that the tile is dealt with correctly after it is
    fetched.  If setTileSize() is not calle dfirst the behaviour is undefined.

    A subclass of QGeoTiledMappingManagerEngine will often make use of a subclass
    fo QGeoTiledMapReply internally, in order to add any engine-specific
    data (such as a QNetworkReply object for network-based services) to the
    QGeoTiledMapReply instances used by the engine.

    QGeoTiledMappingManagerEngine will report that custom map objects are supported
    by default.
    '''
    def __init__(self, parameters, parent=None):
        '''
        Constructs a new tiled mapping manager using the parameters \a parameters
        and the parent \a parent.
        
        @param parameters: A dict of params
        @type parameters: dict
        @param parent: Parent Obj
        @type parent: QObject
        '''
        GeoMappingManagerEngine.__init__(self, parent)
        self._tileSize = QSize(0,0)
        self._setSupportsCustomMapObjects(True)
    
    ''' Requests the map tiled specified by \a request.

    A QGeoTiledMapReply object will be returned, which can be used to manage the
    fetching of the tile and to return the tile data.

    This manager and the returned QGeoTiledMapReply object will emit signals
    indicating if the operation completes or if errors occur.

    Once the operation has completed, QGeoTiledMapReply::mapImageData() and
    QGeoTiledMapReply::mapImageFormat() can be used to generate the tile image.

    The user is responsible for deleting the returned reply object, although
    this can be done in the slot connected to QGeoTiledMappingManagerEngine::finished(),
    QGeoTiledMappingManagerEngine::error(), QGeoTiledMapReply::finished() or
    QGeoTiledMapReply::error() with deleteLater().'''
        
    def getTileImage(self, request):
        '''
        Requests the map tiled specified by \a request.

        A QGeoTiledMapReply object will be returned, which can be used to manage the
        fetching of the tile and to return the tile data.
    
        The returned QGeoTiledMapReply object will emit signals
        indicating if the operation completes or if errors occur.
    
        Once the operation has completed, QGeoTiledMapReply::mapImageData() and
        QGeoTiledMapReply::mapImageFormat() can be used to generate the tile image.
    
        The user is responsible for deleting the returned reply object, although
        this can be done in the slot connected to QGeoTiledMapReply::finished() or
        QGeoTiledMapReply::error() with deleteLater().
        
        @param request: The request
        @type request: GeoTiledMapRequest
        @rtype: GeoTiledMapReply
        '''
        raise NotImplementedError('Please implement getTileImage()')
        
    def createMapData(self):
        '''
        Returns a new QGeoMapData instance which will be managed by
        this manager.
    
        A QGeoMapData instance contains and manages the information about
        what a map widget is looking at.  A  single manager can be used by several
        QGraphcisGeoMap instances since each instance has an associated QGeoMapData instance.
    
        The QGeoMapData instance can be treated as a kind of session object, or
        as a model in a model-view-controller architecture, with QGraphicsGeoMap
        as the view and QGeoMappingManagerEngine as the controller.
    
        The instance returned by the default implementation will be a
        QGeoTiledMapData instance. Subclasses of QGeoTiledMappingManagerEngine are
        free to override this function to return subclasses of QGeoTiledMapData in
        order to customize the map.
        
        @rtype: GeoMapData
        '''
        return GeoTiledMapData(self)
    
    def tileSize(self):
        '''
        Returns the size of the tiles returned by this tiled mapping manager.
        @rtype: QSize
        '''
        return self._tileSize
    
    def setTileSize(self, tileSize):
        '''
        Sets the size of the tiles returned by this tiled mapping manager to \a
        tileSize.
    
        Subclasses of QGeoTiledMappingManagerEngine should use this function to
        ensure tileSize() provides accurate information.
        
        @param tileSize: The new tileSize
        @type tileSize: QSize
        '''
        self._tileSize = tileSize
    
    