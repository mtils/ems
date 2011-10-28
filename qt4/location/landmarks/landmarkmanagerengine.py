'''
Created on 28.10.2011

@author: michi
'''
from PyQt4.QtCore import QObject, Qt, QVariant, pyqtSignal, QMutexLocker,\
    QString
    
from landmarkfilter import LandmarkFilter #@UnresolvedImport
from landmarkmanager import LandmarkManager #@UnresolvedImport
from landmark import Landmark #@UnresolvedImport
from landmarkcategory import LandmarkCategory #@UnresolvedImport
from ems.qt4.location.landmarks.landmarksortorder import LandmarkSortOrder #@UnresolvedImport
from landmarkattributefilter import LandmarkAttributeFilter #@UnresolvedImport
from landmarkboxfilter import LandmarkBoxFilter #@UnresolvedImport
from landmarkcategoryfilter import LandmarkCategoryFilter #@UnresolvedImport
from landmarkintersectionfilter import LandmarkIntersectionFilter #@UnresolvedImport
from landmarkidfilter import LandmarkIdFilter #@UnresolvedImport
from landmarknamefilter import LandmarkNameFilter #@UnresolvedImport

def matchString(sourceStr, matchStr, matchFlags):
    '''
    
    @param sourceStr: The source
    @type sourceStr: str
    @param matchStr: The matching string (if)
    @type matchStr: str
    @param matchFlags: LandmarkFilter.MatchFlags "Enum"
    @type matchFlags: int
    @rtype: bool
    '''
    if not (matchFlags & LandmarkFilter.MatchCaseSensitive):
        sourceStr = sourceStr.lower()
        matchStr = matchStr.lower()
    
    if (matchFlags & 3) == LandmarkFilter.MatchEndsWith:
        return sourceStr.endswith(matchStr)
    elif (matchFlags & 3) == LandmarkFilter.MatchStartsWith:
        return sourceStr.startswith(matchStr)
    elif (matchFlags & 3) == LandmarkFilter.MatchContains:
        return (sourceStr.find(matchStr) != -1)
    else:
        return (sourceStr == matchStr)
    
def getLandmarkAttribute(key, landmark):
    '''
    
    @param key: The attribute name
    @type key: str
    @param landmark: Landmark
    @type landmark: Landmark
    @rtype: QVariant
    '''
    if key == "name":
        return landmark.name();
    elif key == "description":
        return landmark.description();
    elif key == "countryCode":
        return landmark.address().countryCode();
    elif key == "country":
        return landmark.address().country();
    elif key == "state":
        return landmark.address().state();
    elif key == "city":
        return landmark.address().city();
    elif key == "district":
        return landmark.address().district();
    elif key == "district":
        return landmark.address().district();
    elif key == "street":
        return landmark.address().street();
    elif key == "postcode":
        return landmark.address().postcode();
    elif key == "phoneNumber":
        return landmark.phoneNumber();
    else:
        return QVariant(); # shouldn't be possible
    
commonLandmarkKeys = ("name", "description", "countryCode", "country", "state",
                      "county", "city", "district", "street", "postcode",
                      "phoneNumber")



class LandmarkManagerEngine(QObject):
    '''
    \brief The QLandmarkManagerEngine class provides the interface for all implementations
    of the landmark manager backend functionality.

        Instances of this class are usually provided by \l QLandmarkManagerEngineFactory, which is loaded
    from a plugin.
    '''
    
    dataChanged = pyqtSignal()
    '''This signal is emitted some time after changes occur to the datastore managed by this
    engine, and the engine is unable to precisely determine which changes occurred, or if the
    engine considers the changes to be radical enough to require clients to reload all data.

    If this signal is emitted, no other signals may be emitted for the associated changes.

    As it is possible that other processes (or other devices) may have caused the
    changes, the timing can not be determined.'''

    landmarksAdded = pyqtSignal(list)
    '''This signal is emitted some time after a set of landmarks has been added to
    the datastore managed by the engine and where the \l dataChanged() signal was not emitted for those changes.
    As it is possible that other processes(or other devices) may
    have added the landmarks, the exact timing cannot be determined.

    There may be one or more landmark identifiers in the \a landmarkIds list.'''
    
    landmarksChanged = pyqtSignal(list)
    '''This signal is emitted some time after a set of landmarks have been modified in
    the datastore managed by this engine and where the \l dataChanged() signal was not emitted for those changes.
    As it is possible that other processes(or other devices) may have modified the landmarks,
    the timing cannot be determined.

    Note that removal of a category will not trigger a \c landmarksChanged signal for landmarks belonging to that category.

    There may be one ore more landmark identifiers in the \a landmarkIds list.'''
    
    landmarksRemoved = pyqtSignal(list)
    '''This signal is emitted some time after a set of landmarks have been removed from the
    datastore managed by this engine and where the \l dataChanged() signal was not emitted for those changes.
    As it is possible that other processes(or other devices) may have removed the landmarks,
    the timing cannot be determined.

    There may be one ore more landmark identifiers in the \a landmarkIds list.'''
    
    categoriesAdded = pyqtSignal(list)
    '''This signal is emitted some time after a set of categories has been added to the datastore
   managed by this engine and where the \l dataChanged() signal was not emitted for those changes.
   As it is possible that other processes(or other devices) may
   have added the landmarks, the exact timing cannot be determined.

   There may be one or more category identifiers in the \a categoryIds list.'''
    
    categoriesChanged = pyqtSignal(list)
    '''This signal is emitted some time after a set of categories have been modified in the datastore
    managed by the engine and where the \l dataChanged() signal was not emitted for those changes.
    As it is possible that other processes(or other devices) may have modified the categories,
    the timing cannot be determined.

    There may be one ore more category identifiers in the \a categoryIds list.'''
    
    categoriesRemoved = pyqtSignal(list)
    '''This signal is emitted some time after a set of categories have been removed from the datastore
    managed by this engine and where the \l dataChanged() signal was not emitted for those changes.
    As it is possible that other processes(or other devices) may have removed the categories,
    the timing cannot be determined.

    There may be one ore more category identifiers in the \a categoryIds list.'''
    
    def __init__(self):
        QObject.__init__(self, None)
    
    def managerName(self):
        '''
        Returns the manager name for this QLandmarkManagerEngine
        
        @rtype: str
        '''
        return "base"
    
    def managerParameters(self):
        '''
        Returns the parameters with which this engine was constructed.  Note that
        the engine may have discarded unused or invalid parameters at the time of
        construction, and these will not be returned.
        
        @rtype: dict
        '''
        return {}
    
    def managerUri(self):
        '''
        Returns the unique URI of this manager, which is built from the manager name and the parameters
        used to construct it.
        
        @rtype: basestring
        '''
        return LandmarkManager.buildUri(self.managerName(),
                                        self.managerParameters(),
                                        self.managerVersion())
    
    def managerVersion(self):
        '''
        Returns the engine backend implementation version number
        
        @rtype: int
        '''
        return 0
    
    def landmarkIds(self, filter_, limit, offset, sortOrders, error=0,
                      errorString=""):
        '''
        Returns a list of landmark identifiers which match the given \a filter and are sorted according to
        the given \a sortOrders. The \a limit defines the maximum number of landmark IDs to return and the
        \a offset defines the index offset of the first landmark ID.
        A \a limit of -1 means that IDs of all matching landmarks should be returned.
    
        Any error which occurs will be saved in \a error and \a errorString.
        
        @param filter_: A filer
        @type filter_: LandmarkFilter
        @param limit: Limit the results
        @type limit: int
        @param offset: Offset
        @type offset: int
        @param sortOrders: A list of SortOrders
        @type sortOrders: list
        @param error: Unused error ref
        @type error: int
        @param errorString: Unused errorString
        @type errorString: str
        @rtype: list
        '''
        return []
    
    def categoryIds(self, limit, offset, nameSort, error=0, errorString=""):
        '''
        Returns a list of category identifiers
        The \a limit defines the maximum number of IDs to return and the \a offset defines the index offset
        of the first ID.  A \a limit of -1 means IDs for all categories should be returned.
        Any error which occurs will be saved in \a error and \a errorString.
        The identifiers are returned in order according to the given \a nameSort.
        
        @param limit: Result limit
        @type limit: int
        @param offset: Offsets the result
        @type offset: int
        @param nameSort: LandmarkSort param
        @type nameSort: LandmarkSort
        @param error: Unused Error param
        @type error: int
        @param errorString: Unused error param
        @type errorString: str
        @rtype: list
        '''
        return []
    
    def landmark(self, landmarkId, error=0, errorString=""):
        '''
        Returns the landmark in the datastore identified by \a landmarkId.

        Any errors encountered are:stored in \a error and \a errorString.
        The \a error is set to QLandmarkManager::LandmarkDoesNotExistError if the landmark could not be found.
        
        @param landmarkId: A landmark
        @type landmarkId: LandmarkId
        @param error: Unused Error param
        @type error: int
        @param errorString: Unused ErrorString param
        @type errorString: str
        @rtype: Landmark
        '''
        return Landmark()
    
    def landmarks(self, idsOrFilter, errorMapOrSortOrder={}, error=0, errorString=""):
        '''
        Returns a list of landmarks which match the given \a landmarkIds.  The engine will populate \a errorMap
        (the map of indices of the \a landmarkIds list to errors) for the indexes where the landmark could not
        be retrieved.
    
        Overall operation errors are stored in \a error and
        \a errorString.  \a error is set to QLandmarkManager::NoError,
        all landmarks were successfully retrieved.
        
        @param landmarkIds: A list/tuple of Ids
        @type landmarkIds: list
        @param errorMap: Unused dict of errors
        @type errorMap: dict
        @param error: Unused Error param
        @type error: int
        @param errorString: Unused errorString param
        @type errorString: str
        @rtype: list
        '''
        return []
    
    def category(self, categoryId, error=0, errorString=""):
        '''
         Returns the category in the datastore identified by \a categoryId.

        Any errors encountered are stored in \a error and \a errorString.
        A QLandmarkManager::CategoryDoesNotExist error is set if the category could not be found.
        
        @param categoryId: The id
        @type categoryId: LandmarkCategoryId
        @rtype: LandmarkCategory
        '''
        return LandmarkCategory()
    
    def categories(self, idsOrLimit, offset=0, nameSort=None, error=0, errorString=""):
        '''
        Returns a list of categories which match the given \a categoryIds.  The engine will populate \a errorMap
        (the map of indices of the \a categoryIds list to errors) for the indexes where the category could not
        be retrieved.
    
        Overall operation errors are stored in \a error and
        \a errorString.  \a error is set to QLandmarkManager::NoError, if
        all categories were successfully retrieved.
        
        @param idsOrLimit: ids or a limit
        @type idsOrLimit: list or ind
        @param offset: An offset
        @type offset: int
        @param nameSort: sortOrder
        @type nameSort: LandmarkSortOrder
        @rtype: list
        '''
        return []
    
    def saveLandmark(self, landmark, error=0, errorString=""):
        '''
        Adds the given \a landmark to the datastore if \a landmark has a
        default-constructed identifer, or an identifier with the manager
        URI set to the URI of this manager and an empty id.
    
        If the manager URI of the identifier of the \a landmark is neither
        empty nor equal to the URI of this manager, or the id member of the
        identifier is not empty, but does not exist in the manager,
        the operation will fail and and \a error will be set to
        \c QLandmarkManager::LandmarkDoesNotExistError.
    
        Alternatively, the function will update the existing landmark in the
        datastore if \a landmark has a non-empty id and currently exists
        within the datastore.
    
        Returns false on failure or true on success.  On successful save
        of a landmark with an empty id, it will be assigned a valid
        id and have its manager URI set to the URI of this manager.
    
        The engine must emit the appropriate signals to inform clients of changes
        to the datastore resulting from this operation.
    
        Any errors encountered during this operation should be stored in
        \a error and \a errorString.
        
        @param landmark: The Landmark
        @type landmark: Landmark
        
        @rtype: bool
        '''
        return False
    
    def saveLandmarks(self, landmarks, errorMap={}, error=0, errorString=""):
        '''
        Adds the list of \a landmarks to the datastore.
        Returns true if the landmarks were saved successfully, otherwise returns
        false.
    
        The engine will populate \a errorMap (the map of indices of the
        \a landmarks list to errors) for every index for which the landmark could not be
        saved.
    
    
        For each newly saved landmark that was successful, the identifier
        of the landmark will be updated with a new value.
    
        The engine emits the appropriate signals to inform clients of changes
        to the datastore resulting from this operation.
    
        Overall operation errors are stored in \a error and
        \a errorString.  \a error is set to QLandmarkManager::NoError,
        if all \a landmarks were successfully saved.
        
        @param landmarks: List of Landmarks
        @type landmarks: list
        @rtype: bool
        '''
        return False
    
    def removeLandmark(self, landmarkId, error=0, errorString=""):
        '''
        Remove the landmark identified by \a landmarkId from the datastore.

        Returns true if the landmark was removed successfully, otherwise
        returnse false.
    
        The engine emits the appropriate signals to inform clients of changes
        to the datastore resulting from this operation.
    
        Any errors encountered during this operation should be stored to
        \a error and \a errorString.
        
        @param landmarkId: The id
        @type landmarkId: LandmarkId
        @rtype: bool
        '''
        return False
    
    def removeLandmarks(self, landmarkIds, errorMap={}, error=0,
                          errorString=""):
        '''
        Removes every landmark whose identifier is contained in the list
        of \a landmarkIds.  Returns true if all landmarks were removed
        successfully, otherwise false.
    
        The engine populates \a errorMap (the map of indices of the
        \a landmarkIds list to errors) for every index for which the landmark could not be
        removed.
    
        The engine also emits the appropriate signals to inform clients of changes
        to the datastore resulting from this operation.
    
        Overall operation errors are stored in \a error and
        \a errorString.  \a error is set to QLandmarkManager::NoError, if
        all landmarks were successfully removed.

        @param landmarkIds: List of Ids
        @type landmarkIds: list
        @rtype: bool
        '''
        return False
    
    def saveCategory(self, category, error=0, errorString=""):
        '''
        Adds the given \a category to the datastore if \a category has a
        default-constructed identifier, or an identifier with the manager
        URI set to the URI of this manager and an empty id.
    
        If the manager URI of the identifier of the \a category is neither
        empty nor equal to the URI  of this manager, or the id member of the
        identifier is not empty, but does not exist in the manager,
        the operation should fail and \a error should be set to
        \c QLandmarkManager::CategoryDoesNotExistError.
    
        Alternatively, the function should update the existing category in the
        datastore if \a category has a non-empty id and currently exists
        within the datastore.
    
        Returns false on failure or true on success.  On successful save
        of a category with an invalid id, it should be assigned a valid
        id and have its manager URI set to the URI of this manager.
    
        The engine returns the appropriate signals to inform clients of changes
        to the datastore resulting from this operation.
    
        Overall operations errors should be stored in \a error and
        \a errorString.
        
        @param category: LandmarkCatgory
        @type category: LandmarkCatgory
        
        @rtype: bool
        '''
        return False
    
    def removeCategory(self, categoryId, error=0, errorString=''):
        '''
        Removes the category identified by \a categoryId from the datastore.

        Returns true if the category was removed successfully, otherwise
        returnse false.
    
        The engine emits the appropriate signals to inform clients of changes
        to the datastore resulting from this operation
    
        Overall operational errors are stored in \a error and
        \a errorString.
        
        @param categoryId: The id
        @type categoryId: LandmarkCategoryId
        @rtype: bool
        '''
        return False
    
    def importLandmarks(self, device, format, option, categoryId, error=0, errorString=""):
        '''
        Reads landmarks from the given \a device and saves them.  The data from the \a device
        is expected to adhere to the provided \a format.  If no \a format is provided,
        the manager engine tries to autodetect the \a format.
    
        The \a option can be used to control whether categories in the imported
        file will be added during the import.  If the \c AttachSingleCategory option is used, then
        all the landmarks in the import file are assigned to the category identified by
        \a categoryId, in all other circumstances \a categoryId is ignored.  If \a categoryId
        doesn't exist when using \c AttachSingleCategory, QLandmarkManager::CategoryDoesNotExist error is returned.  Note that
        some file formats may not support categories at all.
    
        Returns true if all landmarks could be imported, otherwise returns false.
    
        Overall operational errors are stored in \a error and
        \a errorString.
        
        @param device: The device for reading or a string as filename
        @type device: QIODevice
        @param format_: Format String
        @type format_: str
        @param option: Transfer Option @see TransportOption Enum
        @type option: int
        @param categoryId: The CategoryId
        @type categoryId: LandmarkCategoryId
        @rtype: bool
        '''
        return False
    
    def exportLandmarks(self, device, format, landmarkIds, option, error=0,
                         errorString=""):
        '''
        Writes landmarks to the given \a device.  The landmarks will be written
        according to the specified \a format.  If  \a landmarkIds is empty, then
        all landmarks will be exported, otherwise only those landmarks that
        match \a landmarkIds will be exported.
    
        The \a option can be used to control whether categories will be exported or not.
        Note that the \c AttachSingleCategory option has no meaning during
        export and the manager will export as if \a option was \c IncludeCategoryData.
        Also, be aware that some file formats may not support categories at all and for
        these formats, the \a option is always treated as if it was \c ExcludeCategoryData.
    
        Returns true if all specified landmarks were successfully exported,
        otherwise returns false.
    
        Overall operation errors are stored in \a error and
        \a errorString.
        
        @param device: The device for writing or a string as filename
        @type device: QIODevice
        @param format_: Format String
        @type format_: str
        @param option: Transfer Option @see TransportOption Enum
        @type option: int
        @param categoryId: The CategoryId
        @type categoryId: LandmarkCategoryId
        @rtype: bool
        '''
        return False
    
    def supportedFormats(self, operation, error=0, errorString=""):
        '''
        Returns the supported file formats for the given transfer \a operation, i.e. import or export.
        Errors are stored in \a error and \a errorString.
        
        @see: TransferOperation Enum
        @param operation: Type of operation as int
        @type operation: int
        @rtype: list
        '''
        return []
    
    def filterSupportLevel(self, filter_, error=0, errorString=""):
        '''
        Returns the support level the manager engine provides for the given \a filter.  Errors are stored in \a error
        and \a errorString.
        
        @param filter_:
        @type filter_:
        @param error:
        @type error:
        @param errorString:
        @type errorString:
        @rtype: int
        '''
        raise NotImplementedError("Please implement filterSupportLevel()")
    
    def sortOrderSupportLevel(self, sortOrder, error=0, errorString=""):
        '''
        Returns the support level the manager engine provides for the given \a sortOrder.  Errors are stored in \a error
        and \a errorString.
        
        @param sortOrder:
        @type sortOrder:
        @param error:
        @type error:
        @param errorString:
        @type errorString:
        @rtype: int
        '''
        raise NotImplementedError("Please implement sortOrderSupportLevel()")
    
    def isFeatureSupported(self, feature, error=0, errorString=""):
        '''
        Returns true if the manager engine supports the given \a feature, otherwise returns false;   Errors are stored in
        \a error and \a errorString.
        
        @param feature:
        @type feature:
        @param error:
        @type error:
        @param errorString:
        @type errorString:
        @rtype: int
        '''
        raise NotImplementedError("Please implement isFeatureSupported()")
    
    def isReadOnly(self, landmarkOrCategoryId=None, error=0, errorString=""):
        '''
        Returns true if the manager engine is exclusively read only.  Meaning
        landmarks and categories cannot be added, modified or removed.  Errors are stored in \a error and \a errorString.
        
        @param error:
        @type error:
        @param errorString:
        @type errorString:
        @rtype: bool
        '''
        raise NotImplementedError("Please implement isReadOnly()")
    
    def searchableLandmarkAttributeKeys(self, error=0, errorString=""):
        '''
        Returns the list of landmark attribute keys that may be used in a QLandmarkAttributeFilter.
        Errors are stored in \a error and \a errorString.
        '''
        raise NotImplementedError("Please implement searchableLandmarkAttributeKeys()")
        
    
    def requestDestroyed(self, request):
        '''
        Notifies the manager engine that the given \a request has been destroyed.
        
        @param request: The request
        @type request: LandmarkAbstractRequest
        '''
        pass
    
    def startRequest(self, request):
        '''
        Asks the manager engine to begin the given \a request
        which is currently in a re(startable) state.
    
        Returns true if the request was started successfully,
        else returns false.
        
        @param request: The request
        @type request: LandmarkAbstractRequest
        @rtype: bool
        '''
        return False
    
    def cancelRequest(self, request):
        '''
        Asks the manager engine to cancel the given \a request which was
        previously started and is currently in a cancellable state.
        Returns true if cancelation of the request was started successfully,
        otherwise returns false.
        
        @param request: The request
        @type request: LandmarkAbstractRequest
        @rtype: bool
        '''
    
    def waitForRequestFinished(self, request, msecs):
        '''
        Blocks until the manager engine has completed the given \a request
        which was previously started, or until \a msecs milliseconds have passed.
        Returns true if the request was completed, and false if the request was not in the
        \c QLandmarkAbstractRequest::Active state, no progress could be reported or
        if the engine does not support waitForFinished functionality.
        
        @param request: The request
        @type request: LandmarkAbstractRequest
        @param msecs: The milliseconds
        @type msecs: int
        @rtype: bool
        '''
        return False
    
    @staticmethod
    def updateRequestState(req, state):
        '''
        Updates the given asynchronous request \a req by setting the new \a state
        of the request.  If the new state is different, the stateChanged() signal will be emitted
        by the request.
        
        @param req: The request
        @type req: LandmarkAbstractRequest
        @param state: LandmarkAbstractRequest.State Enum
        @type state: int
        '''
        if req:
            ml = QMutexLocker(req._mutex)
            if req._state != state:
                req._state = state
                ml.unlock()
                req.stateChanged.emit(state)
    
    @staticmethod
    def updateLandmarkIdFetchRequest(req, result, error, errorString,
                                         newState, resultProperty='_landmarkIds'):
        '''
        Updates the given QLandmarkIdFetchRequest \a req with the latest \a result,
        and operation \a error and \a errorString.  In addition, the state of the request
        will be changed to \a newState.
    
        It then causes the request to emit its resultsAvailable() signal to notify clients of the
        request progress.
    
        If the new request state is different from the previous state, the stateChanged() signal will
        also be emitted from the request.
        
        @param req: LandmarkIdFetchRequest
        @type req: LandmarkIdFetchRequest
        @param result: List of results
        @type result: list
        @param error: Unused
        @type error: int
        @param errorString: Unused
        @type errorString: str
        @param newState: Unused
        @type newState: int
        '''
        if req:
            ireq = req
            ml = QMutexLocker(req._mutex)
            req._error = error
            req._errorString = errorString
            if resultProperty:
                req.__setattr__(resultProperty, result)
            emitState = (req._state != newState)
            req._state = newState
            ml.unlock()
            req.resultsAvailable.emit()
            if emitState and ireq:
                ireq.stateChanged(newState)
    
    @staticmethod
    def updateLandmarkFetchRequest(req, result, error, errorString,
                                   newState):
        '''
        Updates the given QLandmarkFetchRequest \a req with the latest \a result,
        and operation \a error and \a errorString.  In addition, the state of the request
        will be changed to \a newState.
    
        It then causes the request to emit its resultsAvailable() signal to notify clients of the
        request progress.
    
        If the new request state is different from the previous state, the stateChanged() signal will
        also be emitted from the request.
        
        @param req: LandmarkFetchRequest
        @type req: LandmarkFetchRequest
        @param result: List of results
        @type result: list
        @param error: Unused
        @type error: int
        @param errorString: Unused
        @type errorString: str
        @param newState: Unused
        @type newState: int
        '''
        return LandmarkManagerEngine.updateLandmarkIdFetchRequest(req, result, error,
                                                                  errorString, newState,
                                                                  '_landmarks')
    
    @staticmethod
    def updateLandmarkFetchByIdRequest(req, result, error,
                                           errorString, newState):
        '''
        Updates the given QLandmarkFetchByIdRequest \a req with the latest \a result,
        operation \a error and \a errorString and map of input index to individual errors, \a errorMap.
         In addition, the state of the request
        will be changed to \a newState.
    
        It then causes the request to emit its resultsAvailable() signal to notify clients of the
        request progress.
    
        If the new request state is different from the previous state, the stateChanged() signal will
        also be emitted from the request.
        
        @param req: LandmarkFetchByIdRequest
        @type req: LandmarkFetchByIdRequest
        @param result: List of results
        @type result: list
        @param error: Unused
        @type error: int
        @param errorString: Unused
        @type errorString: str
        @param newState: Unused
        @type newState: int
        '''
        return LandmarkManagerEngine.updateLandmarkIdFetchRequest(req, result, error,
                                                 errorString, newState,
                                                 '_landmarkIds')
    
    @staticmethod
    def updateLandmarkRemoveRequest(req, error, errorString, errorMap,
                                        newState):
        '''
        Updates the given QLandmarkRemoveRequest \a req with the operation \a error and
        \a errorString and map of input index to individual errors, \a errorMap.  In addition,
        the state of the request will be changed to \a newState.
    
        It then causes the request to emit its resultsAvailable() signal to notify clients of the request
        progress.
    
        If the new request state is different from the previous state, the stateChanged() signal will
        also be emitted from the request.
    
        @param req: LandmarkRemoveRequest
        @type req: LandmarkRemoveRequest
        @param result: List of results
        @type result: list
        @param error: Unused
        @type error: int
        @param errorString: Unused
        @type errorString: str
        @param errorMap: Unused
        @type errorMap: dict
        @param newState: Unused
        @type newState: int
        '''
        return LandmarkManagerEngine.updateLandmarkIdFetchRequest(req, None, error,
                                                                  errorString, newState,
                                                                  '')
    
    @staticmethod
    def updateLandmarkSaveRequest(req, result, error, errorString,
                                     errorMap, newState):
        '''
        Updates the given QLandmarkSaveRequest \a req with the latest \a result, operation \a error
        and \a errorString, and map of input index to individual errors, \a errorMap.
        In addition, the state of the request will be changed to \a newState.
    
        It then causes the request to emit its resultsAvailable() signal to notify clients of the request
        progress.
    
        If the new request state is different from the previous state, the stateChanged() signal will
        also be emitted from the request.
        
        @param req: LandmarkSaveRequest
        @type req: LandmarkSaveRequest
        @param result: List of results
        @type result: list
        @param error: Unused
        @type error: int
        @param errorString: Unused
        @type errorString: str
        @param errorMap: Unused
        @type errorMap: dict
        @param newState: Unused
        @type newState: int
        '''
        
        return LandmarkManagerEngine.updateLandmarkIdFetchRequest(req, result, error,
                                                                  errorString, newState,
                                                                  '_landmarks')
    
    @staticmethod
    def updateLandmarkCategoryIdFetchRequest(req, result, error,
                                                  errorString, newState):
        '''
        Updates the given QLandmarkCategoryIdFetchRequest \a req with the latest \a result,
        and operation \a error and \a errorString.  In addition, the state of the request
        will be changed to \a newState.
    
        It then causes the request to emit its resultsAvailable() signal to notify clients of the
        request progress.
    
        If the new request state is different from the previous state, the stateChanged() signal will
        also be emitted from the request.
        
        @param req: LandmarkCategoryIdFetchRequest
        @type req: LandmarkCategoryIdFetchRequest
        @param result: List of results
        @type result: list
        @param error: Unused
        @type error: int
        @param errorString: Unused
        @type errorString: str
        @param newState: Unused
        @type newState: int
        '''
        return LandmarkManager.updateLandmarkIdFetchRequest(req, result, error,
                                                            errorString, newState,
                                                            '_categoryIds')
    
    @staticmethod
    def updateLandmarkCategoryFetchRequest(req, result, error, errorString,
                                                newState):
        '''
        Updates the given QLandmarkCategoryFetchRequest \a req with the latest \a result,
        and operation \a error and \a errorString.  In addition, the state of the request
        will be changed to \a newState.
    
        It then causes the request to emit its resultsAvailable() signal to notify clients of the
        request progress.
    
        If the new request state is different from the previous state, the stateChanged() signal will
        also be emitted from the request.
        
        @param req: LandmarkCategoryFetchRequest
        @type req: LandmarkCategoryFetchRequest
        @param result: List of results
        @type result: list
        @param error: Unused
        @type error: int
        @param errorString: Unused
        @type errorString: str
        @param newState: Unused
        @type newState: int
        '''
        return LandmarkManagerEngine.updateLandmarkIdFetchRequest(req, result,
                                                                  error,
                                                                  errorString,
                                                                  newState,
                                                                  '_categories')
    
    @staticmethod
    def updateLandmarkCategoryFetchByIdRequest(req, result, error,
                                                    errorString, errorMap,
                                                    newState):
        '''
        Updates the given QLandmarkCategoryFetchByIdRequest \a req with the latest \a result,
        and operation \a error and \a errorString, and map of input index to individual errors, \a errorMap.
       In addition, the state of the request will be changed to \a newState.
    
        It then causes the request to emit its resultsAvailable() signal to notify clients of the
        request progress.
    
        If the new request state is different from the previous state, the stateChanged() signal will
        also be emitted from the request.
        
        @param req: LandmarkCategoryFetchByIdRequest
        @type req: LandmarkCategoryFetchByIdRequest
        @param result: List of results
        @type result: list
        @param error: Unused
        @type error: int
        @param errorString: Unused
        @type errorString: str
        @param errorMap: Unused
        @type errorMap: dict
        @param newState: Unused
        @type newState: int
        '''
        return LandmarkManagerEngine.updateLandmarkIdFetchRequest(req, result,
                                                                  error,
                                                                  errorString,
                                                                  newState,
                                                                  '_categories')
    
    @staticmethod
    def updateLandmarkCategoryRemoveRequest(req, error, errorString,
                                                 errorMap, newState):
        '''
        Updates the given QLandmarkCategoryRemoveRequest \a req with the operation \a error and
        \a errorString and map of input index to individual errors, \a errorMap.  In addition,
        the state of the request will be changed to \a newState.
    
        It then causes the request to emit its resultsAvailable() signal to notify clients of the request
        progress.
    
        If the new request state is different from the previous state, the stateChanged() signal will
        also be emitted from the request.
        
        @param req: LandmarkCategoryFetchByIdRequest
        @type req: LandmarkCategoryFetchByIdRequest
        @param result: List of results
        @type result: list
        @param error: Unused
        @type error: int
        @param errorString: Unused
        @type errorString: str
        @param errorMap: Unused
        @type errorMap: dict
        @param newState: Unused
        @type newState: int
        '''
        return LandmarkManagerEngine.updateLandmarkIdFetchRequest(req, None,
                                                                  error,
                                                                  errorString,
                                                                  newState,
                                                                  '')
    
    @staticmethod
    def updateLandmarkCategorySaveRequest(req, result, error, errorString,
                                            errorMap, newState):
        '''
        Updates the given QLandmarkSaveCategoryRequest \a req with the latest \a result, operation error \a error
        and \a errorString, and map of input index to individual errors, \a errorMap.
        In addition, the state of the request will be changed to \a newState.
    
        It then causes the request to emit its resultsAvailable() signal to notify clients of the request
        progress.
    
        If the new request state is different from the previous state, the stateChanged() signal will
        also be emitted from the request.
        
        @param req: LandmarkCategorySaveRequest
        @type req: LandmarkCategorySaveRequest
        @param result: List of results
        @type result: list
        @param error: Unused
        @type error: int
        @param errorString: Unused
        @type errorString: str
        @param errorMap: Unused
        @type errorMap: dict
        @param newState: Unused
        @type newState: int
        '''
        return LandmarkManagerEngine.updateLandmarkIdFetchRequest(req, result,
                                                                  error,
                                                                  errorString,
                                                                  newState,
                                                                  '_categories')
    
    @staticmethod
    def updateLandmarkImportRequest(req, result, error, errorString,
                                        newState):
        '''
        Updates the given QLandmarkImportRequest \a req with the operation \a error and \a errorString.
        In addition the state of the request is changed to \a newState.  This function may also be used
        to update the \a ids of the landmarks which have been imported.
    
        It then causes the request to emit its resultsAvailable() signal to notify the clients of the request
        progress.
    
        If the new request state is different from the previous state, the stateChanged() signal will
        also be emitted from the request.
        
        @param req: LandmarkImportRequest
        @type req: LandmarkImportRequest
        @param result: List of results
        @type result: list
        @param error: Unused
        @type error: int
        @param errorString: Unused
        @type errorString: str
        @param errorMap: Unused
        @type errorMap: dict
        @param newState: Unused
        @type newState: int
        '''
        return LandmarkManagerEngine.updateLandmarkIdFetchRequest(req, result,
                                                                  error,
                                                                  errorString,
                                                                  newState,
                                                                  '_landmarkIds')
    
    @staticmethod
    def updateLandmarkExportRequest(req, error, errorString, newState):
        '''
        Updates the given QLandmarkExportRequest \a req with the operation \a error and \a errorString.
        In addition the state of the request is changed to \a newState.
    
        It then causes the request to emit its resultsAvailable() signal to notify the clients of the request
        progress.
    
        If the new request state is different from the previous state, the stateChanged() signal will
        also be emitted from the request.
        
        @param req: LandmarkExportRequest
        @type req: LandmarkExportRequest
        @param result: List of results
        @type result: list
        @param error: Unused
        @type error: int
        @param errorString: Unused
        @type errorString: str
        @param errorMap: Unused
        @type errorMap: dict
        @param newState: Unused
        @type newState: int
        '''
        
        return LandmarkManagerEngine.updateLandmarkIdFetchRequest(req, None,
                                                                  error,
                                                                  errorString,
                                                                  newState,
                                                                  '')
    
    @staticmethod
    def compareLandmark(a, b, sortOrders):
        '''
        Compares two landmarks (\a a and \a b) using the given list of \a sortOrders.  Returns a negative number if \a a should appear
        before \a b according to the sort order, a positive number if \a a should appear after \a b according to the sort order,
        and zero if the two are unable to be sorted.
        
        @param a: Landmark 1
        @type a: Landmark
        @param b: Landmark 2
        @type b: Landmark
        @param sortOrders: List of LandmarkSortOrder Objects
        @type sortOrders: list
        @rtype: int
        '''
        comparison = 0
        for sortOrder in sortOrders:
            if sortOrder.type_() == LandmarkSortOrder.NameSort:
                comparison = LandmarkManagerEngine.compareName(a, b, sortOrder)
                break
            else:
                comparison = 0
                
            if comparison != 0:
                break
        return comparison
        
    @staticmethod
    def compareName(a, b, nameSort):
        '''
        Compares two landmarks (\a a and \a b) by name.

        Returns a negative number if \a a should appear before \a b according to the \a nameSort,
        a positive number if \a a should appear after \a b according to the \a nameSort,
        and zero if the two are unable to be sorted.
    
        Assuming an ascending order sort, an integer less than, equal to, or greater than zero
        is returned if \a a is less than, equal to or greater than \a b.
    
        \a nameSort specifies whether an ascending or descending order is used and whether
        the sort is case sensitive or not.
        
        @param a: Landmark 1
        @type a: Landmark
        @param b: Landmark 2
        @type b: Landmark
        @param nameSort: LandmarkNameSort
        @type nameSort: LandmarkNameSort
        @rtype: int
        '''
        
        result = QString.compare(QString.fromUtf8(a.name()),
                                 QString.fromUtf8(b.name()),
                                 nameSort.caseSensitivity())
        
        if nameSort.direction() == Qt.DescendingOrder:
            result *= -1
        
        return result
    
    @staticmethod
    def addSorted(sorted_, landmark, sortOrders):
        '''
        Performs an insertion sort \a landmark into the \a sorted list, according to the provided \a sortOrders list.
        The first QLandmarkSortOrder in the list has the highest priority; if the \a landmark is deemed equal to another
        in the \a sorted list, the second QLandmarkSortOrder in the list is used (and so on until either the landmark is inserted
        or there are no more sort order objects in the list).
        
        @param sorted_: The sorted list of Landmark(s)
        @type sorted_: list
        @param landmark: the landmark which will be inserted
        @type landmark: Landmark
        @param sortOrders: list of sortOrders
        @type sortOrders: LandmarkSortOrder
        '''
        if len(sortOrders) > 0:
            for i in range(len(sorted_)):
                comparison = LandmarkManagerEngine.compareLandmark(sorted_[i],
                                                                   landmark,
                                                                   sortOrders)
                if comparison > 0:
                    sorted_.insert(i, landmark)
                    return
        #hasn't been inserted yet?  append to the list.
        sorted_.append(landmark)
    
    @staticmethod
    def testFilter(filter_, landmark):
        '''
        Returns true if the supplied \a landmark matches the supplied \a filter.
        
        @param filter_: The filter to matches
        @type filter_: LandmarkFilter
        @param landmark: The landmark to test
        @type landmark: Landmark
        @rtype: bool
        '''
        filterType = filter_.type_()
        if filterType == LandmarkFilter.DefaultFilter:
            return True
        elif filterType == LandmarkFilter.AttributeFilter:
            filterKeys = filter_.attributeKeys()
            
            if filter_.operationType() == LandmarkAttributeFilter.AndOperation: 
                lmAttributeValue = QVariant()
                
                for filterKey in filterKeys:
                    if filterKey in commonLandmarkKeys:
                        lmAttributeValue = getLandmarkAttribute(filterKey,
                                                                landmark)
                        if lmAttributeValue.type() == QVariant.String:
                            lmString = lmAttributeValue.toString()
                            attribString = filter_.attribute(filterKey).toString()
                            if matchString(lmString, attribString,
                                           filter_.matchFlags(filterKey)):
                                continue
                        elif filter_.attribute(filterKey) == lmAttributeValue:
                            continue
                        return False
                    else:
                        return False
                return True
            else: #Must be Or Operation
                lmAttributeValue = QVariant()
                
                for filterKey in filterKeys:
                    if filterKey in commonLandmarkKeys:
                        lmAttributeValue = getLandmarkAttribute(filterKey,
                                                                landmark)
                        if lmAttributeValue.type() == QVariant.String:
                            lmString = lmAttributeValue.toString()
                            attribString = filter_.attribute(filterKey).toString()
                            if matchString(lmString, attribString,
                                           filter_.matchFlags(filterKey)):
                                return True
                        elif filter_.attribute(filterKey) == lmAttributeValue:
                            return True
                return False
        elif filterType == LandmarkFilter.BoxFilter:
            
            if not filter_.boundingBox().isValid():
                return False
            
            tly = filter_.boundingBox().topLeft().latitude()
            bry = filter_.boundingBox().bottomRight().latitude()
            tlx = filter_.boundingBox().topLeft().longitude()
            brx = filter_.boundingBox().bottomRight().longitude()
            
            latWrap = (tly < bry)
            longWrap = (tlx > brx)
            
            if latWrap:
                return False
            
            #check if landmark is outside the box's latitudes
            if landmark.coordinate().latitude() < bry and landmark.coordinate().latitude() > tly:
                return False
            
            lmx = landmark.coordinate().longitude()
            if longWrap:
                if ((lmx > 0.0) and (lmx<= tlx)) or ((lmx < 0.0) and (lmx >= brx)):
                    return False
            else:
                if lmx < tlx or lmx > brx:
                    return False;
            
            #landmark must be within the bounds to reach here.
            return True
        
        elif filterType == LandmarkFilter.CategoryFilter:
            categories = landmark.categoryIds()
            for categoryId in categories:
                if filter_.categoryId() == categoryId:
                    return True
            
            return False
        
        elif filterType == LandmarkFilter.IntersectionFilter:
            terms = filter_.filters()
            if len(terms) == 0:
                return False
            
            for term in terms:
                if not LandmarkManagerEngine.testFilter(term, landmark):
                    return False
            return True
        
        elif filterType == LandmarkFilter.LandmarkIdFilter:
            ids = filter_.landmarkIds()
            for id_ in ids:
                if id_ == landmark.landmarkId():
                    return True
            return False
        
        elif filterType == LandmarkFilter.InvalidFilter:
            return False
        
        elif filterType == LandmarkFilter.NameFilter:
            return matchString(landmark.name(), filter_.name(),
                               filter_.matchFlags())
        
        elif filterType == LandmarkFilter.ProximityFilter:
            distance = filter_.center().distanceTo(landmark.coordinate())
            if distance < filter_.radius() or distance == filter_.radius():
                return True
            else:
                return False
        
        elif filterType == LandmarkFilter.UnionFilter:
            terms = filter_.filters()
            if len(terms) == 0:
                return False
            else:
                for term in terms:
                    if LandmarkManagerEngine.testFilter(filter_, landmark):
                        return True
                return False
        return False
    
    @staticmethod
    def sortLandmarks(landmarks, sortOrders):
        '''
        Sorts the given list of \a landmarks according to the provided \a sortOrders
        
        @param landmarks: The landmarks 
        @type landmarks: list
        @param sortOrders: The orders
        @type sortOrders: list
        @return: A List with LandmarkIds!
        @rtype: list
        '''
        landmarkIds = []
        sortedLandmarks = []
        
        if len(sortOrders):
            for landmark in landmarks:
                LandmarkManagerEngine.addSorted(sortedLandmarks, landmark,
                                                sortOrders)
            
            for landmark in sortedLandmarks:
                landmarkIds.append(landmark)
        else:
            for landmark in landmarks:
                landmarkIds.append(landmark.landmarkId())
        
        return landmarkIds
    