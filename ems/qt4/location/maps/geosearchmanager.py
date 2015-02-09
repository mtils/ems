'''
Created on 24.10.2011

@author: michi
'''
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot

from ems.qt4.location.landmarks.landmarkfilter import LandmarkFilter #@UnresolvedImport
from ems.qt4.location.landmarks.landmarknamefilter import LandmarkNameFilter #@UnresolvedImport
from ems.qt4.location.landmarks.landmarkintersectionfilter import LandmarkIntersectionFilter #@UnresolvedImport
from ems.qt4.location.landmarks.landmarkboxfilter import LandmarkBoxFilter #@UnresolvedImport
from ems.qt4.location.landmarks.landmarkproximityfilter import LandmarkProximityFilter #@UnresolvedImport
from ems.qt4.location.landmarks.landmarkfetchrequest import LandmarkFetchRequest #@UnresolvedImport
from ems.qt4.location.landmarks.landmarkabstractrequest import LandmarkAbstractRequest #@UnresolvedImport
from ems.qt4.location.landmarks.landmarkmanager import LandmarkManager #@UnresolvedImport
from ems.qt4.location.geoboundingarea import GeoBoundingArea #@UnresolvedImport
from ems.qt4.location.geoboundingbox import GeoBoundingBox #@UnresolvedImport
from ems.qt4.location.geoboundingcircle import GeoBoundingCircle #@UnresolvedImport


from geosearchreply import GeoSearchReply #@UnresolvedImport

class GeoCombiningSearchReply(GeoSearchReply):
    
    def __init__(self, searchReply, fetchRequests, parent=None):
        '''
        
        @param searchReply: The searchReply
        @type searchReply:  GeoSearchReply
        @param fetchRequests: The requests
        @type fetchRequests: list
        @param parent: Parent object
        @type parent: qobject
        '''
        super(GeoCombiningSearchReply, self).__init__(parent)
        self.fetchRequests = fetchRequests
        self._searchReply = searchReply
        searchReply.finished.connect(self.searchReplyFinished)
        
        for fetchRequest in fetchRequests:
            fetchRequest.stateChanged.connect(self.landmarkFetchStateChanged)
    
    @pyqtSlot()
    def searchReplyFinished(self):
        if self._searchReply.error() == GeoSearchReply.NoError:
            searchReplyPlaces = self._searchReply.places()
            for place in self._searchReply.places():
                self.addPlace(place)
    
            if len(self.fetchRequests) == 0:
                self.finished.emit()
            else:
                self.error.emit(self.error(), self.errorString())
                for req in self.fetchRequests:
                    self.fetchRequests.remove(req)
                    del req
                self.fetchRequests = []
            
    
        del self._searchReply;
        self._searchReply = None
    
    @pyqtSlot(int)
    def landmarkFetchStateChanged(self, newState):
         
        if newState == LandmarkAbstractRequest.FinishedState:
            req = LandmarkFetchRequest(self.sender())
            if req.error() == LandmarkManager.NoError:
    
                for landmark in req.landmarks():
                    self.addPlace(landmark)
                
                
                self.fetchRequests.remove(req)
                del req
                self.fetchRequests = []
    
                if not self._searchReply and (len(self.fetchRequests) == 0):
                    self.finished.emit()
                else:
                    self.error.emit(GeoSearchReply.CombinationError,
                                    req.errorString())
        
                    del self._searchReply
                    self._searchReply = None
                    for req in self.fetchRequests:
                        self.fetchRequests.remove(req)
                        del req
                    self.fetchRequests = []
        

class GeoSearchManager(QObject):
    '''
    The QGeoSearchManager class provides support for searching
    operations related to geographic information.


    The geocode(), reverseGeocode() and search() functions return
    QGeoSearchReply objects, which manage these operations and report on the
    result of the operations and any errors which may have occurred.

    The geocode() and reverseGeocode() functions can be used to convert
    QGeoAddress instances to QGeoCoordinate instances and vice-versa.

    The search() function allows a user to perform a free text search
    for place information.  If the string provided can be interpreted as
    an address it can be geocoded to coordinate information, and the string
    can also be used to search a landmarks database, depending on the level
    of support supplied by the service provider.

    The defaultLandmarkManager() function will return a QLandmarkManager
    instance if access to the service providers landmark database is
    available outside of the search() method.

    A user can supply other QLandmarkManager instances to be searched during
    the execution of search() with setAdditionalLandmarkManagers(). This
    means that a personal database store can be combined with a public source
    of database information with very little effort.

    \note At present the additional landmark managers only search for the
    search string in the name of the landmarks.

    Instances of QGeoSearchManager can be accessed with
    QGeoServiceProvider::searchManager().

    A small example of the usage of QGeoSearchManager and the handling of
    QLandmark results follows:
    '''
    
    finished = pyqtSignal(GeoSearchReply)
    '''This signal is emitted when reply has finished processing.

    If reply::error() equals QGeoSearchReply::NoError then the processing
    finished successfully.

    This signal and QGeoSearchReply::finished() will be emitted at the same
    time.

    Do no delete the reply object in the slot connected to this
    signal. Use deleteLater() instead.'''
    
    error = pyqtSignal(GeoSearchReply, int, str)
    '''This signal is emitted when an error has been detected in the processing of
    reply. The GeoSearchManager.finished() signal will probably follow.

    The error will be described by the error code \a error. If \a errorString is
    not empty it will contain a textual description of the error.

    This signal and QGeoSearchReply::error() will be emitted at the same time.

    \note Do no delete the reply object in the slot connected to this
    signal. Use deleteLater() instead.'''
    
    'SearchType Enum'
    SearchNone = 0x0000
    'Do not use the search string.'
    
    SearchGeocode = 0x0001
    'Use the search string as a textual address in a geocoding operation.'
    
    SearchLandmarks = 0x0002
    '''Use the search string for free-text search against the available landmark
    information sources.'''
    
    SearchAll = 0xFFFF
    'All available information sources should be used as part of the search.'
    
    def __init__(self, engine, parent=None):
        '''
        Constructs a new manager with the specified parent and with the
        implementation provided by engine.
    
        This constructor is used interally by GeoServiceProviderFactory. Regular
        users should acquire instances of QGeoSearchManager with
        GeoServiceProvidersearchManager()
        
        @param engine: The GeoSearchManagerEngine 
        @type engine: GeoSearchManagerEngine
        @param parent: Parent object
        @type parent: QObject
        '''
        
        self.__engine = engine
        QObject.__init__(self, parent)
        if self.__engine:
            self.__engine.setParent(self)
            self.__engine.finished.connect(self.finished)
            self.__engine.error.connect(self.error)
            
            
        else:
            raise ValueError('Engine was null')
    
    
    def managerName(self):
        '''
        Returns the name of the engine which implements the behaviour of this
        search manager.
    
        The combination of managerName() and managerVersion() should be unique
        amongst the plugin implementations.
        
        @rtype: str
        '''
        return self.__engine.managerName()
    
    def managerVersion(self):
        '''
        Returns the version of the engine which implements the behaviour of this
        search manager.
    
        The combination of managerName() and managerVersion() should be unique
        amongst the plugin implementations.
        
        @rtype: int
        '''
        return self.__engine.managerVersion()
    
    
    def geocode(self, address, bounds=None):
        '''
        Begins the geocoding of \a address. Geocoding is the process of finding a
        coordinate that corresponds to a given address.
    
        A QGeoSearchReply object will be returned, which can be used to manage the
        geocoding operation and to return the results of the operation.
    
        This manager and the returned QGeoSearchReply object will emit signals
        indicating if the operation completes or if errors occur.
    
        If supportsGeocoding() returns false an
        QGeoSearchReply::UnsupportedOptionError will occur.
    
        Once the operation has completed, QGeoSearchReply::places() can be used to
        retrieve the results, which will consist of a list of QGeoPlace objects.
        These object represent a combination of coordinate and address data.
    
        The address data returned in the results may be different from \a address.
        This will usually occur if the geocoding service backend uses a different
        canonical form of addresses or if \a address was only partially filled out.
    
        If \a bounds is non-null and valid QGeoBoundingArea it will be used to
        limit the results to thos that are contained within \a bounds. This is
        particularly useful if \a address is only partially filled out, as the
        service will attempt to geocode all matches for the specified data.
    
        The user is responsible for deleting the returned reply object, although
        this can be done in the slot connected to QGeoSearchManager::finished(),
        QGeoSearchManager::error(), QGeoSearchReply::finished() or
        QGeoSearchReply::error() with deleteLater().
        
        @param address: The searched GeoAddress
        @type address: GeoAddress
        @param bounds: A GeoBoundingArea (optional)
        @type bounds: GeoBoundingArea
        '''
        return self.__engine.geocode(address, bounds)
    
    def reverseGeoCode(self, coordinate, bounds=None):
        '''
        Begins the reverse geocoding of coordinate. Reverse geocoding is the
        process of finding an address that corresponds to a given coordinate.
    
        A QGeoSearchReply object will be returned, which can be used to manage the
        reverse geocoding operation and to return the results of the operation.
    
        This manager and the returned GeoSearchReply object will emit signals
        indicating if the operation completes or if errors occur.
    
        If supportsReverseGeocoding() returns false an
        GeoSearchReply.UnsupportedOptionError will occur.
    
        At that point GeoSearchReply.places() can be used to retrieve the
        results, which will consist of a list of QGeoPlace objects. These object
        represent a combination of coordinate and address data.
    
        The coordinate data returned in the results may be different from \a
        coordinate. This will usually occur if the reverse geocoding service
        backend shifts the coordinates to be closer to the matching addresses, or
        if the backend returns results at multiple levels of detail.
    
        If multiple results are returned by the reverse geocoding service backend
        they will be provided in order of specificity. This normally occurs if the
        backend is configured to reverse geocode across multiple levels of detail.
        As an example, some services will return address and coordinate pairs for
        the street address, the city, the state and the country.
    
        If \a bounds is non-null and a valid GeoBoundingBox it will be used to
        limit the results to thos that are contained within \a bounds.
    
        The user is responsible for deleting the returned reply object, although
        this can be done in the slot connected to QGeoSearchManager::finished(),
        GeoSearchManager.error(), GeoSearchReply.finished() or
        GeoSearchReply.error() with deleteLater().
        
        @param coordinate: The coordinate to decode
        @type coordinate: GeoCoordinate
        @param bounds: A bounding area
        @type bounds: GeoBoundingArea
        '''
        return self.__engine.reverseGeoCode(coordinate, bounds)
    
    def search(self, searchString, searchTypes=0xFFFF,
                limit = -1, offset = 0, bounds = None):
        '''
        Begins searching for a place matching  searchString.  The value of
         searchTypes will determine whether the search is for addresses only,
        for landmarks only or for both.
    
        A QGeoSearchReply object will be returned, which can be used to manage the
        geocoding operation and to return the results of the operation.
    
        This manager and the returned QGeoSearchReply object will emit signals
        indicating if the operation completes or if errors occur.
    
        If supportsGeocoding() returns false and  searchTypes is
        QGeoSearchManager::SearchGeocode an
        QGeoSearchReply::UnsupportedOptionError will occur.
    
        Once the operation has completed, QGeoSearchReply::places() can be used to
        retrieve the results, which will consist of a list of QGeoPlace objects.
        These object represent a combination of coordinate and address data.
    
        If any of the QGeoPlace instances in the results have landmark associated
        data, QGeoPlace::isLandmark() will return true and
        QLandmark::QLandmark(const QGeoPlace &place) can be used to convert the
        QGeoPlace instance into a QLandmark instance.
    
        If  searchTypes is QGeoSearchManager::SearchLandmarks or
        QGeoSearchManager::SearchAll, a free text landmark search will be
        performed. The results will be a combination of the backend specific
        landmark search and the same free text search applied to each of the
        QLandmarkManager instances in additionalLandmarkManagers().
    
        \note At present the additional landmark managers only search for the
        search string in the name of the landmarks.
    
        If  limit is -1 the entire result set will be returned, otherwise at most
         limit results will be returned.
    
        The  offset parameter is used to ask the search service to not return the
        first  offset results.
    
        The  limit and  offset results are used together to implement paging.
    
        If additional landmark managers have been setup the number of results
        returned will be at most (1 + number of additional landmark managers) *
         limit.  This happens because the results are requested from all sources, combined, and returned once
        all sources have responded.
    
        If  bounds is non-null and a valid QGeoBoundingArea it will be used to
        limit the results to thos that are contained within  bounds.
    
        The user is responsible for deleting the returned reply object, although
        this can be done in the slot connected to QGeoSearchManager::finished(),
        QGeoSearchManager::error(), QGeoSearchReply::finished() or
        QGeoSearchReply::error() with deleteLater().
        
        @param searchString: The Search Criteria string
        @type searchString: string
        @param searchTypes: A bit mask of searchTypes
        @type searchTypes: int
        @param limit: Limit the results
        @type limit: int
        @param offset: Offset like in sql
        @type offset: int
        @param bounds: Bounding Area
        @type bounds: GeoBoundingArea
        @rtype: GeoSearchReply
        '''
        
        reply = self.__engine.search(searchString,
                                     searchTypes,
                                     limit,
                                     offset,
                                     bounds)

        if ( len(self.__engine.additionalLandmarkManagers()) == 0)\
                or (searchTypes == GeoSearchManager.SearchNone) \
                or (searchTypes == GeoSearchManager.SearchGeocode):
            return reply;
    
        # TODO add default LM to this list and change doc?
    
        fetchRequests = []
    
    
        # TODO replace with free text search filter when it becomes available
        searchFilter = LandmarkNameFilter()
        searchFilter.setName(searchString);
        searchFilter.setMatchFlags(LandmarkFilter.MatchContains);
        
        intersectFilter = LandmarkIntersectionFilter()
        
        intersectFilter.append(searchFilter)
        
        if bounds:
            if bounds.type() == GeoBoundingArea.BoxType:
                box = GeoBoundingBox(bounds)
                if box.isValid() and not box.isEmpty():
                    boxFilter = LandmarkBoxFilter()
                    boxFilter.setBoundingBox(box)
                    intersectFilter.append(boxFilter)
            elif bounds.type() == GeoBoundingArea.CircleType:
                circle = GeoBoundingCircle(bounds) 
                if circle.isValid() and  not circle.isEmpty():
                    proximityFilter = LandmarkProximityFilter(circle.center(),
                                                              circle.radius())
                    intersectFilter.append(proximityFilter)
        
        for lm in self.__engine.additionalLandmarkManagers():
            fetchRequest = LandmarkFetchRequest(lm, self)
            fetchRequest.setFilter(intersectFilter)
            fetchRequest.setLimit(limit)
            fetchRequest.setOffset(offset)
            fetchRequests.append(fetchRequest)
        
        return GeoCombiningSearchReply(reply, fetchRequests)
    
    def supportsGeoCoding(self):
        '''
        Returns whether this manager supports geocoding.
        @rtype: bool
        '''
        return self.__engine.supportsGeoCoding()
    
    def supportsReverseGeoCoding(self):
        '''
        Returns whether this manager supports reverse geocoding.
        
        @rtype: bool
        '''
        return self.__engine.supportsReverseGeoCoding()
    
    def supportedSearchTypes(self):
        '''
        Returns the search types supported by the search() function with this manager.
        
        @rtype: int
        '''
        return self.__engine.supportedSearchTypes()
    
    def defaultLandmarkManager(self):
        '''
        Returns the landmark manager provided by the service provider for
        use with search().
    
        Will return None if the no landmark manager is associated with the service
        provider. This does not indicate that search() does not support
        landmark searching, only that any landmark searching which occurs within in
        search() is done without the use of a QLandmarkManager.
        
        @rtype: LandmarkManager
        '''
        return self.__engine.defaultLandmarkManager()
    
    def setAdditionalLandmarkManagers(self, landmarkManagers):
        '''
        Sets the landmark managers to be used with search() to \a landmarkManagers.

        These landmark managers will be used along with the landmark manager returned
        by defaultLandmarkManager().
        
        @param landmarkManagers: Additional Managers
        @type landmarkManagers: list
        '''
        self.__engine.setAdditionalLandmarkManagers(landmarkManagers)
        
    def additionalLandmarkManagers(self):
        '''
        Returns the landmark managers that will be used with search().

        These landmark managers will be used along with the landmark manager returned
        by defaultLandmarkManager().
        
        @rtype: list
        '''
        return self.__engine.additionalLandmarkManagers()
    
    def addAdditionalLandmarkManager(self, landmarkManager):
        '''
        Adds landmarkManager to the list of landmark managers that will be used
        with search().
    
        These landmark managers will be used along with the landmark manager returned
        by defaultLandmarkManager().
        
        @param landmarkManager: The landmarkmanager
        @type landmarkManager: LandmarkManager
        '''
        if landmarkManager:
            self.__engine.addAdditionalLandmarkManager(landmarkManager)
    
    def setLocale(self, locale):
        '''
        Sets the locale to be used by the this manager to locale.

        If this search manager supports returning the results
        in different languages, they will be returned in the language of locale.
    
        The locale used defaults to the system locale if this is not set.
        
        @param locale: The locale
        @type locale: QLocale
        '''
        self.__engine.setLocale(locale)
    
    def locale(self):
        '''
        Returns the locale used to hint to this search manager about what
        language to use for the results.
        
        @rtype: QLocale
        '''
        return self.__engine.locale()