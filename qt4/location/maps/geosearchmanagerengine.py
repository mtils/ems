'''
Created on 16.11.2011

@author: michi
'''
from PyQt4.QtCore import QObject, pyqtSignal, QLocale
from ems.qt4.location.maps.geosearchreply import GeoSearchReply

class GeoSearchManagerEngine(QObject):
    '''
    \brief The QGeoSearchManagerEngine class provides an interface and
    convenience methods to implementers of QGeoServiceProvider plugins who want
    to provide support for searching operations related to geographic data.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps-impl

    In the default implementation, supportsGeocoding() and supportsReverseGeocoding() returns false while
    geocode() and reverseGeocode()
    cause QGeoSearchReply::UnsupportedOptionError to occur.

    If the service provider supports geocoding the subclass should provide an
    implementation of geocode() and call setSupportsGeocoding(true) at
    some point in time before geoocode() is called.

    Similarly, if the service provider supports reverse geocoding the subclass
    should provide an implementation reverseGeocode() and call
    setSupportsReverseGeocoding(true) at some point in time before
    reverseGeoocode() is called.

    The search() function will make use of the QLandmarkManager instances
    returned by additionalLandmarkManagers(). If a QLandmarkManager is used
    internally to query the service providers landmark data the
    QLandmarkManager can be made available to the users with
    setDefaultLandmarkManager().

    The subclass should call setSupportedSearchTypes() at some point in time
    before search() is called.

    If the service supports searching for places the subclass should provide
    an implementetation of search() and call setSupportedSearchTypes() at
    some point in time before search() is called.

    A subclass of QGeoSearchManagerEngine will often make use of a subclass
    fo QGeoSearchReply internally, in order to add any engine-specific
    data (such as a QNetworkReply object for network-based services) to the
    QGeoSearchReply instances used by the engine.

    \sa QGeoSearchManager
    '''
    
    _managerName = ""
    
    _managerVersion = -1
    
    _defaultLandmarkManager = None
    _additionalLandmarkManagers = []

    _supportsGeocoding = False
    _supportsReverseGeocoding = False
    _supportedSearchTypes = 0

    _locale = QLocale
    
    finished = pyqtSignal(GeoSearchReply)
    '''This signal is emitted when \a reply has finished processing.

    If reply::error() equals QGeoSearchReply::NoError then the processing
    finished successfully.

    This signal and QGeoSearchReply::finished() will be emitted at the same
    time.

    \note Do no delete the \a reply object in the slot connected to this
    signal. Use deleteLater() instead.'''
    
    error = pyqtSignal(GeoSearchReply, int, str)
    '''This signal is emitted when an error has been detected in the processing of
    \a reply. The QGeoSearchManagerEngine::finished() signal will probably follow.

    The error will be described by the error code \a error. If \a errorString is
    not empty it will contain a textual description of the error.

    This signal and QGeoSearchReply::error() will be emitted at the same time.

    \note Do no delete the \a reply object in the slot connected to this
    signal. Use deleteLater() instead.'''
    
    def __init__(self, parameters, parent=None):
        '''
        Constructs a new engine with the specified \a parent, using \a parameters
        to pass any implementation specific data to the engine.
        
        @param parameters: Params for the engine
        @type parameters: dict
        @param parent: Parent QObject
        @type parent: QObject
        '''
        self._defaultLandmarkManager = None
        QObject.__init__(self, parent)
    
    def _setManagerName(self, managerName):
        '''
        Sets the name which this engine implementation uses to distinguish itself
        from the implementations provided by other plugins to \a managerName.
    
        The combination of managerName() and managerVersion() should be unique
        amongst plugin implementations.
        
        @param managerName: The manager Name
        @type managerName: basestring
        '''
        self._managerName = managerName
    
    def managerName(self):
        '''
        Returns the name which this engine implementation uses to distinguish
        itself from the implementations provided by other plugins.
    
        The combination of managerName() and managerVersion() should be unique
        amongst plugin implementations.
        @rtype: basestring
        '''
        return self._managerName
    
    def _setManagerVersion(self, managerVersion):
        '''
        Sets the version of this engine implementation to \a managerVersion.

        The combination of managerName() and managerVersion() should be unique
        amongst plugin implementations.
        
        @param managerVersion: The version
        @type managerVersion: int
        '''
        self._managerVersion = managerVersion
    
    def managerVersion(self):
        '''
        Returns the version of this engine implementation.

        The combination of managerName() and managerVersion() should be unique
        amongst plugin implementations.
        @rtype: int
        '''
        return self._managerVersion
    
    def geocode(self, address, bounds):
        '''
        Begins the geocoding of \a address. Geocoding is the process of finding a
        coordinate that corresponds to a given address.
    
        A QGeoSearchReply object will be returned, which can be used to manage the
        geocoding operation and to return the results of the operation.
    
        This engine and the returned QGeoSearchReply object will emit signals
        indicating if the operation completes or if errors occur.
    
        If supportsGeocoding() returns false an
        QGeoSearchReply::UnsupportedOptionError will occur.
    
        Once the operation has completed, QGeoSearchReply::places() can be used to
        retrieve the results, which will consist of a list of QGeoPlace objects.
        These object represent a combination of coordinate and address data.
    
        The address data returned in the results may be different from \a address.
        This will usually occur if the geocoding service backend uses a different
        canonical form of addresses or if \a address was only partially filled out.
    
        If \a bounds is non-null and a valid QGeoBoundingArea it will be used to
        limit the results to those that are contained by \a bounds. This is
        particularly useful if \a address is only partially filled out, as the
        service will attempt to geocode all matches for the specified data.
    
        The user is responsible for deleting the returned reply object, although
        this can be done in the slot connected to QGeoSearchManagerEngine::finished(),
        QGeoSearchManagerEngine::error(), QGeoSearchReply::finished() or
        QGeoSearchReply::error() with deleteLater().
        
        @param address: The address which GeoCoordinate is searched
        @type address: GeoAddress
        @param bounds: Limit the results if bounds.isValid()
        @type bounds: GeoBoundingArea
        '''
        return GeoSearchReply(GeoSearchReply.UnsupportedOptionError,
                              "Geocoding is not supported by this service provider.",
                              self)
    
    def reverseGeoCode(self, coordinate, bounds):
        '''
        Begins the reverse geocoding of \a coordinate. Reverse geocoding is the
        process of finding an address that corresponds to a given coordinate.
    
        A QGeoSearchReply object will be returned, which can be used to manage the
        reverse geocoding operation and to return the results of the operation.
    
        This engine and the returned QGeoSearchReply object will emit signals
        indicating if the operation completes or if errors occur.
    
        If supportsReverseGeocoding() returns false an
        QGeoSearchReply::UnsupportedOptionError will occur.
    
        At that point QGeoSearchReply::places() can be used to retrieve the
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
    
        If \a bounds is non-null and a valid QGeoBoundingArea it will be used to
        limit the results to those that are contained by \a bounds.
    
        The user is responsible for deleting the returned reply object, although
        this can be done in the slot connected to QGeoSearchManagerEngine::finished(),
        QGeoSearchManagerEngine::error(), QGeoSearchReply::finished() or
        QGeoSearchReply::error() with deleteLater().
        
        @param coordinate: GeoCoordinate
        @type coordinate: GeoCoordinate
        @param bounds: Bounds, if isValid() search will be reduced to that area
        @type bounds: GeoBoundingArea
        '''
        return GeoSearchReply(GeoSearchReply.UnsupportedOptionError,
                              "Reverse geocoding is not supported by this service provider.",
                              self)
    
    def search(self, searchString, searchTypes, limit, offset, bounds):
        '''
        Begins searching for a place matching \a searchString.  The value of
        \a searchTypes will determine whether the search is for addresses only,
        for landmarks only or for both.
    
        A QGeoSearchReply object will be returned, which can be used to manage the
        geocoding operation and to return the results of the operation.
    
        This engine and the returned QGeoSearchReply object will emit signals
        indicating if the operation completes or if errors occur.
    
        If supportsGeocoding() returns false and \a searchTypes is
        QGeoSearchManagerEngine::SearchGeocode an
        QGeoSearchReply::UnsupportedOptionError will occur.
    
        Once the operation has completed, QGeoSearchReply::places() can be used to
        retrieve the results, which will consist of a list of QGeoPlace objects.
        These object represent a combination of coordinate and address data.
    
        If any of the QGeoPlace instances in the results have landmark associated
        data, QGeoPlace::isLandmark() will return true and
        QLandmark::QLandmark(const QGeoPlace &place) can be used to convert the
        QGeoPlace instance into a QLandmark instance.
    
        If \a searchTypes is QGeoSearchManagerEngine::SearchLandmarks or
        QGeoSearchManagerEngine::SearchAll, a free text landmark search will be
        performed. The results will be a combination of the backend specific
        landmark search and the same free text search applied to each of the
        QLandmarkManager instances in additionalLandmarkManagers().
    
        \note At present the additional landmark managers only search for the
        search string in the name of the landmarks.
    
        If \a limit is -1 the entire result set will be returned, otherwise at most
        \a limit results will be returned.
    
        The \a offset parameter is used to ask the search service to not return the
        first \a offset results.
    
        The \a limit and \a offset results are used together to implement paging.
    
        If additional landmark managers have been setup the number of results
        returned will be at most (1 + number of additional landmark managers) *
        \a limit.  This happens because the results are requested from all sources, combined, and returned once
        all sources have responded.
    
    
        If \a bounds is non-null and a valid QGeoBoundingArea it will be used to
        limit the results to those that are contained by \a bounds.
    
        The user is responsible for deleting the returned reply object, although
        this can be done in the slot connected to QGeoSearchManagerEngine::finished(),
        QGeoSearchManagerEngine::error(), QGeoSearchReply::finished() or
        QGeoSearchReply::error() with deleteLater().
        
        @param searchString: The string to search for
        @type searchString: basestring
        @param searchTypes: bitwise or Types
        @type searchTypes: int
        @param limit: The limit of results as int
        @type limit: int
        @param offset: the offset, normally 0 but not setted as default
        @type offset: int
        @param bounds: GeoBoundingArea, if isValid() considered
        @type bounds: GeoBoundingArea
        '''
        return GeoSearchReply(GeoSearchReply.UnsupportedOptionError,
                              "Searching is not supported by this service provider.",
                              self)
    
    def _setSupportsGeocoding(self, supported):
        '''
        Sets whether geocoding is supported by this engine to \a supported.

        It is important that subclasses use this method to ensure that the engine
        reports its capabilities correctly.  If this function is not used the
        engine will report that it does not support geocoding.
        
        @param supported: if supported True
        @type supported: bool
        '''
        self._supportsGeocoding = supported
    
    def supportsGeocoding(self):
        '''
        Returns whether this engine supports geocoding.
        @rtype: bool
        '''
        return self._supportsGeocoding
    
    def _setSupportsReverseGeocoding(self, supported):
        '''
        Sets whether reverse geocoding is supported by this engine to \a supported.

        It is important that subclasses use this method to ensure that the engine
        reports its capabilities correctly.  If this function is not used the
        engine will report that it does not support reverse geocoding.
        
        @param supported: If supported True
        @type supported: bool
        '''
        self._supportsReverseGeocoding = supported
    
    def supportsReverseGeocoding(self):
        '''
        Returns whether this engine supports reverse geocoding.
        @rtype: bool
        '''
        return self._supportsReverseGeocoding
    
    def _setSupportedSearchTypes(self, searchTypes):
        '''
        Sets the search types supported by the search() with this engine to \a searchTypes.

        It is important that subclasses use this method to ensure that the engine
        reports its capabilities correctly.  If this function is not used the
        engine will report that it does not support any search types.
        
        @param searchTypes: The supported SearchTypes
        @type searchTypes: int
        '''
        self._supportedSearchTypes = searchTypes
    
    def supportedSearchTypes(self):
        '''
        Returns the search types supported by the search() with this engine.
        @rtype: int
        '''
        return self._supportedSearchTypes
    
    def _setDefaultLandmarkManager(self, landmarkManager):
        '''
        Sets the landmark manager provided by the service provider for
        use with search() to \a landmarkManager.
    
        This should only be set if search() makes use of a QLandmarkManager
        instance to provide landmark searching functionality.
    
        It is important that subclasses use this method to ensure that the engine
        is able to carry out landmark searches.  If this function is not used the
        engine will not be able to use or return the default landmark manager.
        
        @param landmarkManager: the landmarkmanager
        @type landmarkManager: LandmarkManager
        '''
        self._defaultLandmarkManager = landmarkManager
    
    def defaultLandmarkManager(self):
        '''
         Returns the landmark manager provided by the service provider for
        use with search().
    
        Will return 0 if the no landmark manager is associated with the service
        provider. This does not indicate that search() does not support
        landmark searching, only that any landmark searching which occurs within in
        search() is done without the use of a QLandmarkManager.
        @rtype: LandmarkManager
        '''
        return self._defaultLandmarkManager
    
    def setAdditionalLandmarkManagers(self, landmarkManagers):
        '''
        Sets the landmark managers to be used with search() to \a landmarkManagers.

        These landmark managers will be used along with the landmark manager returned
        by defaultLandmarkManager().
        
        @param landmarkManagers: list of LandmarkManager objects
        @type landmarkManagers: LandmarkManager
        '''
        for manager in landmarkManagers:
            if manager:
                self._additionalLandmarkManagers.append(manager)
    
    def additionalLandmarkManagers(self):
        '''
        Returns the landmark managers that will be used with search().

        These landmark managers will be used along with the landmark manager returned
        by defaultLandmarkManager().
        @rtype: list
        '''
        return self._additionalLandmarkManagers
    
    def addAdditionalLandmarkManager(self, landmarkManager):
        '''
        Adds \a landmarkManager to the list of landmark managers that will be used with search().

        These landmark managers will be used along with the landmark manager returned
        by defaultLandmarkManager().
        
        @param landmarkManager: An additional LandmarkManager
        @type landmarkManager: LandmarkManager
        '''
        if landmarkManager:
            self._additionalLandmarkManagers.append(landmarkManager)
    
    def setLocale(self, locale):
        '''
        Sets the locale to be used by the this manager to \a locale.

        If this search manager supports returning the results
        in different languages, they will be returned in the language of \a locale.
    
        The locale used defaults to the system locale if this is not set.
        
        @param locale: The new locale
        @type locale: QLocale
        '''
        self._locale = locale
    
    def locale(self):
        '''
        Returns the locale used to hint to this search manager about what
        language to use for the results.
        @rtype: QLocale
        '''
        return self._locale
    
    
    