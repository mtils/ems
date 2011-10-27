'''
Created on 24.10.2011

@author: michi
'''
import re

from PyQt4.QtCore import QObject, QFile, QString, SIGNAL, pyqtSignal
from landmark import Landmark #@UnresolvedImport
from landmarkid import LandmarkId #@UnresolvedImport
from landmarkcategory import LandmarkCategory #@UnresolvedImport
from landmarknamesort import LandmarkNameSort #@UnresolvedImport
from landmarkcategoryid import LandmarkCategoryId #@UnresolvedImport
from landmarksortorder import LandmarkSortOrder #@UnresolvedImport
from landmarkfilter import LandmarkFilter #@UnresolvedImport

class LandmarkManager(QObject):
    '''
    \brief The QLandmarkManager class provides an interface for storage
    and retrieval of landmarks from a landmark store.

    The QLandmarkManager is the starting class to use when working with landmarks.
    It effectively represents a landmark datastore and it provides the synchronous operations for the
    creation, retrieval, updating and deletion of both landmarks and categories.  For asynchronous operations
    use the \l {Asynchronous Landmark Requests} {request classes} which use the manager as a parameter.
    The manager provides notifications whenever landmarks or categories are added, updated or removed.

    Each manager is identified by a manager name which typically takes the form of a reverse domain string
    such as \c com.nokia.qt.landmarks.engines.sqlite.  However every supported platform provides a default
    manager which may be instantiated without having to provide a name like so:
    \snippet doc/src/snippets/qtlandmarksdocsample/qtlandmarksdocsample.cpp Instantiate default QLandmarkManager

    \section1 Retrieval Operations

    To retrieve a set of landmarks we provide may provide a QLandmarkFilter, QLandmarkSortOrder and limit and offset as necessary.
    The QLandmarkFilter defines the criteria for selecting landmarks; for example, a QLandmarkCategoryFilter may be used
    to choose landmarks that belong to a certain category.  A QLandmarkSortOrder order defines how the results should
    be sorted.  (Note that if you wish to sort by distance, you should use a proxmity filter, see QLandmarkProximityFilter).
    The limit allows specification of the maximum number of items to
    return and the offset defines the index of the first item.  The following demonstrates how to search for the first 100
    landmarks belonging to a given category, sorted by name.

    \snippet doc/src/snippets/qtlandmarksdocsample/qtlandmarksdocsample.cpp Retrieve landmarks by category synchronously

    The set of parameters described above are not always necessary as defaults are provided, if we wanted to retrieve
    all landmarks, then the appropriate call is:

    \snippet doc/src/snippets/qtlandmarksdocsample/qtlandmarksdocsample.cpp Retrieve all landmarks synchronously
    \note Landmark retrieval is potentially a long operation, the synchronous API provided by the manager
    is subject to blocking.  It is generally recommended that the QLandmarkFetchRequest be used because
    it behaves asynchronously.

    Categories may be retrieved in a similar manner:
    \snippet doc/src/snippets/qtlandmarksdocsample/qtlandmarksdocsample.cpp Retrieve categories synchronously simple

    \section1 Saving and Deleting

    Saving and deleting landmarks and categories are fairly straightforward.  To add a new landmark or category
    simply instantiate a QLandmark or QLandmarkCategory, set its data fields (e.g., name, coordinate, etc.) and pass
    a pointer to the appropriate save operation.  For example:

    \snippet doc/src/snippets/qtlandmarksdocsample/qtlandmarksdocsample.cpp Add landmark synchronously simple

    We pass the landmark by pointer bcause it will be assigned a new QLandmarkId when the function call is done.
    Saving a landmark with a valid id already set will update the existing landmark.

    Removal of landmark may be done as follows:
    \snippet doc/src/snippets/qtlandmarksdocsample/qtlandmarksdocsample.cpp Remove landmark synchronously simple

    \section1 Importing and Exporting

    Import and export are potentially long operations, to perform these operations asynchronously
    see QLandmarkImportRequest and QLandmarkExportRequest.  The simplest way to perform an import
    is to supply a file name while an export will need both a file name and format.

    \snippet doc/src/snippets/qtlandmarksdocsample/qtlandmarksdocsample.cpp ImportExport landmark simple

    The formats supported for import and export can be found by calling the
    supportedFormats() function with the type of operation to be performed,
    either ImportOperation or ExportOperation.
    '''
    
    'Error Enum: Defines the possible errors for the landmark manager.'
    NoError = 0
    'No error occurred'
    
    DoesNotExistError = 1
    'The most recent operation failed due to an item not being found, usually an import file.'
    
    LandmarkDoesNotExistError = 2
    'The most recent operation failed due to a specified landmark not being found.'
    
    CategoryDoesNotExistError = 3
    'The most recent operation faied due to a specified category not being found.'
    
    AlreadyExistsError = 4
    'The most recent operation failed because the specified landmark or category already exists.'
    
    LockedError = 5
    'The most recent operation failed because the datastore specified is currently locked.'
    
    PermissionsError = 6
    'The most recent operation failed because the caller does not have permission to perform the operation.'
    
    OutOfMemoryError = 7
    'The most recent operation failed due to running out of memory.'
    
    VersionMismatchError = 8
    'The most recent operation failed because the backend of the manager is not of the required version.'
    
    NotSupportedError = 9
    'The most recent operation failed because the requested operation is not supported by the manager.'
    
    BadArgumentError = 10
    'The most recent operation failed because one or more of the parameters to the operation were invalid.'
    
    InvalidManagerError = 11
    '''The most recent operation failed because the manager failed to initialize correctly and is invalid.
    This could be due using a manager name that is not recognised/available. A landmark request object will return this error if
    if is assigned a null manager pointer.'''
    
    ParsingError = 12
    'The most recent operation failed because the imported file could not be parsed.'
    
    CancelError = 13
    'The most recent operation failed to complete due to user cancelation.'
    
    UnknownError = 14
    'The most recent operation failed for an unknown reason.'
    
    'SupportLevel Enum: Defines the possible support levels the manager can provide for a given filter or sort order list.'
    NativeSupport = 0
    'The manager natively supports the filter or sort order list.'
    
    EmulatedSupport = 1
    '''The manager emulates the behaviour of the filter or sort order list.
       Emulated behaviour will inherently be slower than a natively supported implementation.'''
    
    NoSupport = 2
    'The manager does not support the filter or sort order list at all.'
    
    
    'ManagerFeature Enum: Defines the possible features the landmark manager can support.'
    ImportExportFeature = 0
    'The manager supports import and/or export operations'
    
    NotificationsFeature = 1
    '''The manager will emit notification signals when landmarks/categories have
                         been added/modified/removed from the datastore it manages.'''
    
    'TransferOption Enum: Defines the possible options when transferring landmarks during import or export.'
    IncludeCategoryData = 0
    '''During an import, category data is included.  If an imported category doesn't exist
       the category is created.  If the imported category name matches an existing
       category name, then the landmark is added to that category.  For exports, categories
       are included in the exported file if the file format allows it.'''
    
    ExcludeCategoryData = 1
    'Landmarks are imported or exported without any categories assigned to the landmarks.'
    
    AttachSingleCategory = 2
    '''Only relevant for import operations.  When landmarks are imported they are
       all assigned to a given category.'''
    
    'TransferOperation Enum: Defines the type of transfer.'
    ImportOperation = 0
    'Landmarks are being copied from a file to the device.'
    
    ExportOperation = 1
    'Landmarks are being copied from the device to a file.'
    
    Gpx = 'Gpx'
    'The format constant to define using the gpx format in the import and export functions.'
    
    Lmx = 'Lmx'
    'The format constant to define using the lmx format in the import and export functions.'
    
    Kml = 'Kml'
    'The format constant to define using the kml format in the import and export functions.'
    
    Kmz = 'Kmz'
    'The format constant to define using the kmz format in the import and export functions.'
    
    
    QTLANDMARKS_IMPLEMENTATION_VERSION_NAME = "com.nokia.qtmobility.landmarks.implementation.version"
    
    URI_PREFIX = 'qtlandmarks'
    'The prefix for calls with an uri @see parseUri'
    
    dataChanged = pyqtSignal()
    '''This signal is emitted by the manager if its internal state changes and it is unable to precisely determine
    the changes which occurred, or if the manager considers the changes to be radical enough to require clients to reload
    all data.  If the signal is emitted, no other signals will be emitted for the associated changes.'''

    landmarksAdded = pyqtSignal(list)
    '''This signal is emitted when landmarks (identified by \a landmarkIds) have been added to the datastore managed by this manager.
    This signal is not emitted if the dataChanged() signal was previously emitted for these changes.'''
    
    landmarksChanged = pyqtSignal(list)
    '''This signal is emitted when landmarks (identified by \a landmarkIds) have been modified in the datastore managed by this manager.
    This signal is not emitted if the dataChanged() signal was previously emitted for these changes.  Note that removal
    of a category will not trigger a \c landmarksChanged signal for landmarks belonging to that category.'''
    
    landmarksRemoved = pyqtSignal(list)
    '''This signal is emitted when landmarks (identified by \a landmarkIds) have been removed from the datastore managed by this manager.
    This signal is not emitted if the dataChanged() signal was previously emitted for these changes.'''
    
    categoriesAdded = pyqtSignal(list)
    '''This signal is emitted when categories (identified by \a categoryIds) have been added to the datastore managed by this manager.
    This signal is not emitted if the dataChanged() signal was previously emitted for these changes.'''
    
    categoriesChanged = pyqtSignal(list)
    '''This signal is emitted when categories (identified by \a categoryIds) have been modified in the datastore managed by this manager.
    This signal is not emitted if the dataChanged() signal was previously emitted for these changes.'''
    
    categoriesRemoved = pyqtSignal(list)
    '''This signal is emitted when categories (identified by \a categoryIds) have been removed from the datastore managed by this manager.
    This signal is not emitted if the dataChanged() signal was previously emitted for these changes.'''
    
    _factories = {}
    
    def __init__(self, managerName, parameters, parent=None):
        '''
        Constructs a QLandmarkManager. The default manager implementation for the platform will be used.

        The \a parent QObject will be used as the parent of this QLandmarkManager.
        
        @param managerName: The name of the manager
        @type managerName: str
        @param parameters: Parameters for engine
        @type parameters: dict
        @param parent: The parent
        @type parent: QObject
        '''
        QObject.__init__(self, parent)
        self.__engine = None
        self.__createEngine(managerName, parameters)
        self._errorCode = 0
        self._errorString = ""
        self._errorMap = {}
        self.__isConnected = False
    
    def __del__(self):
        '''
        Frees the memory used by the QLandmarkManager
        '''
        if self.__engine:
            del self.__engine
    
    def saveLandmark(self, landmark):
        '''
        Adds the given \a landmark to the database if \a landmark has a
        default-constructed identifer, or an identifier with the manager
        URI set to the URI of this manager and an empty id.
    
        If the manager URI of the identifier of the \a landmark is neither
        empty nor equal to the URI of this manager, or the id member of the
        identifier is not empty, but does not exist in the manager,
        the operation will fail and calling error() will return
        \c QLandmarkManager::LandmarkDoesNotExistError.
    
        Alternatively, the function will update the existing landmark in the
        database if \a landmark has a non-empty id and currently exists
        within the database.
    
        Returns false on failure or true on success.  On successful save
        of a landmark with an empty id, it will be assigned a valid
        id and have its manager URI set to the URI of this manager.
        
        @param landmark: The landmark to save
        @type landmark: Landmark
        @rtype: bool
        '''
        if not self.__engine:
            return False
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        return self.__engine.saveLandMark(landmark, self._errorCode, 
                                          self._errorString)
        
    def saveLandmarks(self, landmarks):
        '''
        Adds the list of \a landmarks to the database.
        Returns true if the landmarks were saved successfully, otherwise returns
        false.
    
        This function will set per-input errors in the QLandmarkManager::errorMap().
    
        The QLandmarkManager::error() function will only return \c
        QLandmarkManager::NoError if all landmarks were saved successfully.
    
        For each new landmark that was successfully saved, a landmark identifier
        is assigned to that landmark.
        
        @param landmarks: The landmarks
        @type landmarks: list
        @rtype: bool
        '''
        if not self.__engine:
            return False
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        return self.__engine.saveLandmarks(landmarks, self._errorMap,
                                           self._errorCode, self._errorString)
    
    def removeLandmark(self, landmarkOrId):
        '''
        Remove the landmark identified by \a landmarkId from the database.

        Returns true if the landmark was removed successfully, otherwise
        returnse false.
        
        @param landmarkId: The Landmark id
        @type landmarkId: LandmarkId
        @rtype: bool
        '''
        if not self.__engine:
            return False
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        if isinstance(landmarkOrId, Landmark):
            landmarkOrId = landmarkOrId.landmarkId()
            
        return self.__engine.removeLandmark(landmarkOrId, self._errorCode,
                                            self._errorString)
    
    def removeLandmarks(self, landmarks):
        '''
        Removes every landmark whose identifier is contained in the list
        of \a landmarkIds.  Returns true if all landmarks were removed
        successfully, otherwise false.
    
        This batch function will set per-input errors in the QLandmarkManager::errorMap().
    
        The QLandmarkManager::error() function will only return
        \c QLandmarkManager::NoError if all landmarks were removed successfully.
        
        @param landmarks: The landmarks to remove
        @type landmarks: list
        @rtype: bool
        '''
        if not self.__engine:
            return False
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        if len(landmarks) and isinstance(landmarks[0], Landmark):
            landmarkIds = []
            for mark in landmarks:
                landmarkIds.append(mark.landmarkId())
            
            return self.__engine.removeLandmarks(landmarkIds, self._errorMap,
                                             self._errorCode, self._errorString)
            
        return self.__engine.removeLandmarks(landmarks, self._errorMap,
                                             self._errorCode, self._errorString)
    
    
    def saveCategory(self, category):
        '''
        Adds the given \a category to the database if \a category has a
        default-constructed identifier, or an identifier with the manager
        URI set to the URI of this manager and an empty id.
    
        If the manager URI of the identifier of the \a category is neither
        empty nor equal to the URI  of this manager, or the id member of the
        identifier is not empty, but does not exist in the manager,
        the operation will fail and calling error() will return
        \c QLandmarkManager::CategoryDoesNotExistError.
    
        Alternatively, the function will update the existing category in the
        database if \a category has a non-empty id and currently exists
        within the database.
    
        Returns false on failure or true on success.  On successful save
        of a category with an invalid id, it will be assigned a valid
        id and have its manager URI set to the URI of this manager.
        
        @param category: The category
        @type category: LandmarkCategory
        @rtype: bool
        '''
        if not self.__engine:
            return False
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        return self.__engine.saveCategory(category, self._errorCode,
                                          self._errorString)
    
    def removeCategory(self, category):
        '''
        Remove the category identified by \a categoryId from the database.

        Returns true if the category was removed successfully, otherwise
        returnse false.
        
        @param category: The category
        @type category: LandmarkCategory
        '''
        if not self.__engine:
            return False
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        if isinstance(category, LandmarkCategory):
            category = category.categoryId()
        
        return self.__engine.removeCategory(category, self._errorCode,
                                            self._errorString)
    
    
    def category(self, categoryId):
        '''
        Returns the cateory in the database identified by \a categoryId.
        
        @param categoryId: The id
        @type categoryId: LandmarkCategoryId
        @rtype: LandmarkCategory
        '''
        if not self.__engine:
            return LandmarkCategory()
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        return self.__engine.category(categoryId, self._errorCode,
                                      self._errorString)
    
    def categories(self, categoryIdsOrLimit, offset=0, nameSort=None):
        '''
        Returns a list of categories which match the given \a categoryIds.

         This batch function will set per-input errors in the QLandmarkManager::errorMap();
    
        The QLandmarkManager::error() function will only return \c QLandmarkManager::NoError if
        all categories were successfully retrieved.
        
        @param categoryIds: Ids of categories
        @type categoryIds: list
        '''
        
        if not self.__engine:
            return [LandmarkCategory()]
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        if isinstance(categoryIdsOrLimit, list):
            return self.__engine.categories(categoryIdsOrLimit, self._errorCode,
                                            self._errorString)
        
        if nameSort is None:
            nameSort = LandmarkNameSort()
            
        cats = self.__engine.categories(categoryIdsOrLimit, offset, 
                                      nameSort, self._errorCode,
                                      self._errorString)
        
        if self._errorCode != LandmarkManager.NoError:
            return [LandmarkCategory()]
        
        return cats
    
    def categoriyIds(self, limit, offset=0, nameSort=None):
        '''
        Returns a list of categories which match the given \a categoryIds.

         This batch function will set per-input errors in the QLandmarkManager::errorMap();
    
        The QLandmarkManager::error() function will only return \c QLandmarkManager::NoError if
        all categories were successfully retrieved.
        
        @param categoryIds: Ids of categories
        @type categoryIds: list
        '''
        
        if not self.__engine:
            return [LandmarkCategoryId()]
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        if nameSort is None:
            nameSort = LandmarkNameSort()
            
        ids = self.__engine.categoryIds(limit, offset, nameSort,
                                         self._errorCode, self._errorString)
        
        if self._errorCode != LandmarkManager.NoError:
            return [LandmarkCategoryId()]
        
        return ids
    
    def landmark(self, landmarkId):
        '''
        Returns the landmark in the database identified by \a landmarkId
        
        @param landmarkId: The landmarkId
        @type landmarkId: LandmarkId
        @rtype: Landmark
        '''
        
        if not self.__engine:
            return Landmark()
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
            
        lm = self.__engine.landmark(landmarkId, self._errorCode,
                                       self._errorString)
        
        if self._errorCode != LandmarkManager.NoError:
            return Landmark()
        
        return lm
    
    def landmarks(self, filter_=None, limit=-1, offset=0, sortOrders=None):
        '''
        Returns a list of landmarks which match the given \a filter and are sorted according to the \a sortOrders.
        The \a limit defines the maximum number of landmarks to return and the \a offset defines the index offset
        of the first landmark.  A \a limit of -1 means all matching landmarks should be returned.
        
        @param filter_: The filter to use
        @type filter_: LandmarkFilter
        @param limit: Limit
        @type limit: int
        @param offset: Offset
        @type offset: int
        @param sortOrders: Sortorders
        @type sortOrders: list
        @rtype: list
        '''
        if not self.__engine:
            return [Landmark()]
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        if filter_ is None:
            filter_ = LandmarkFilter()
        
        if sortOrders is None:
            sortOrders = [LandmarkSortOrder()]
            
        if isinstance(sortOrders, LandmarkSortOrder):
            sortOrders = [sortOrders]
            
        lms = self.__engine.landmarks(filter_, limit, offset, sortOrders,
                                     self._errorCode, self._errorString)
        
        if self._errorCode != LandmarkManager.NoError:
            return [Landmark()]
        
        return lms
    
    
    def landmarkIds(self, filter_=None, limit=-1, offset=0, sortOrders=None):
        '''
        Returns a list of landmark identifiers which match the given \a filter and are sorted according to
        the given \a sortOrders. The \a limit defines the maximum number of landmark ids to return and the
        \a offset defines the index offset of the first landmark id.
        A \a limit of -1 means that ids of all matching landmarks should be returned.  Note that
        a limit of 0 will return zero landmark ids.
        
        @param filter_: The filter to use
        @type filter_: LandmarkFilter
        @param limit: Limit
        @type limit: int
        @param offset: Offset
        @type offset: int
        @param sortOrders: Sortorders
        @type sortOrders: list
        @rtype: list
        '''
        
        if not self.__engine:
            return [LandmarkId()]
        
        if filter_ is None:
            filter_ = LandmarkFilter()
        
        if sortOrders is None:
            sortOrders = [LandmarkSortOrder()]
            
        if isinstance(sortOrders, LandmarkSortOrder):
            sortOrders = [sortOrders]
        
        ids = self.__engine.landmarkIds(filter_, limit, offset, sortOrders,
                                        self._errorCode, self._errorString)
        
        if self._errorCode != LandmarkManager.NoError:
            return [LandmarkId()]
        
        return ids
    
    def importLandmarks(self, deviceOrFileName, format_="", option=None,
                          categoryId=None):
        '''
        Reads landmarks from the given \a device and saves them.  The data from the \a device
        is expected to adhere to the provided \a format.  If no \a format is provided,
        the manager tries to auto detect the \a format.
    
        The \a option can be used to control whether categories in the imported
        file will be added during the import.  If the \c AttachSingleCategory option is used, then
        all the landmarks in the import file are assigned to the category identified by
        \a categoryId, in all other circumstances \a categoryId is ignored.  If \a categoryId
        doesn't exist when using \c AttachSingleCategory, QLandmarkManager::CategoryDoesNotExistError is set.  Note that
        some file formats may not support categories at all.
    
        Returns true if all landmarks could be imported, otherwise
        returns false.
    
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
        if not self.__engine:
            return False
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        if isinstance(deviceOrFileName, basestring) or \
            isinstance(deviceOrFileName, QString):
            if deviceOrFileName:
                deviceOrFileName = QFile(deviceOrFileName)
        
        if option is None:
            option = self.IncludeCategoryData
        
        if categoryId is None:
            categoryId = LandmarkCategoryId()
        
            
        return self.__engine.importLandmarks(deviceOrFileName, format_,
                                           option,
                                           categoryId,
                                           self._errorCode,
                                           self._errorString)
        
    
    def exportLandmarks(self, deviceOrFileName, format_, landmarkIds=None,
                          option=None):
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
        otherwise returns false.  It may be possible that only a subset
        of landmarks are exported.
        
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
        if not self.__engine:
            return False
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        if isinstance(deviceOrFileName, basestring) or \
            isinstance(deviceOrFileName, QString):
            if deviceOrFileName:
                deviceOrFileName = QFile(deviceOrFileName)
        
        if option is None:
            option = self.IncludeCategoryData
        
        if landmarkIds is None:
            landmarkIds = [LandmarkId()]
        
        
            
        return self.__engine.exportLandmarks(deviceOrFileName, format_,
                                             landmarkIds,
                                             option,
                                             self._errorCode,
                                             self._errorString)
    
    def supportedFormats(self, operation):
        '''
        Returns the file formats supported for the given transfer \a operation. ie import or export.
        
        @see: TransferOperation Enum
        @param operation: Type of operation as int
        @type operation: int
        @rtype: list
        '''
        
        if not self.__engine:
            return []
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        
        return self.__engine.supportedFormats(operation, self._errorCode,
                                              self._errorString)
    
    def error(self):
        '''
        Returns the error code of the most recent operation.  All functions will modify the error based on whether the
        operation successfully or not.
        
        @rtype: int
        '''
        return self._errorCode
    
    def errorString(self):
        '''
        Returns a short human-readable description of the error that occurred
        in the most recent operation.  The error string is intended to be used
        by developers and is not suitable for showing to end users.
        
        @rtype: str
        '''
        return self._errorString
    
    def errorMap(self):
        '''
        Returns per-input error codes for the most recent operation. This function only
        returns meaningful information if the most recent operation was a batch
        operation.  The keys in the map correspond to the index of the input list.
        The error map is only populated for indexes at which an error occurred.
        Eg If we saved 5 landmarks and an error occurred at index 3, the error map
        will have only a single key for index 3.
        
        @rtype: dict
        '''
        return self._errorMap
    
    def isFeatureSupported(self, feature):
        '''
        Returns whether the manager supports the given \a feature.
        
        @param feature: The queried feature
        @type feature: int
        @rtype: bool
        '''
        if not self.__engine:
            return False
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        
        return self.__engine.isFeatureSupported(feature, self._errorCode,
                                                self._errorString)
    
    def filterSupportLevel(self, filter_):
        '''
        Returns the support level the manager provides for the given \a filter.  For the case
        of intersection and union filters, whether the elements will be individually processed
        is dependent on the particular manager implementation.
        
        @param filter_: The queried filter
        @type filter_: LandmarkFilter
        @rtype: int
        @see: LandmarkManager.Supportlevel Enum
        '''
        if not self.__engine:
            return LandmarkManager.NoSupport
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        
        return self.__engine.filterSupportLevel(filter_, self._errorCode,
                                                self._errorString)
    
    def sortOrderSupportLevel(self, sortOrder):
        '''
        Returns the support level the manager provides for the given \a sortOrder.
        
        @param sortOrder: The queried sortOrder
        @type sortOrder: LandmarkSortOrder
        @rtype: int
        @see LandmarkManager.SupportLevel Enum
        '''
        if not self.__engine:
            return LandmarkManager.NoSupport
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        
        return self.__engine.filterSupportLevel(sortOrder, self._errorCode,
                                                self._errorString)
    
    def isReadOnly(self, item=None):
        '''
        Returns true if the manager is entirely read-only.  Meaning
        landmarks and categories cannot be added, modified or removed.
        
        @param item: None for whole manager, LandmarkId or LandmarkCategoryId 
        @rtype: bool
        '''
        if not self.__engine:
            return LandmarkManager.NoSupport
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        
        return self.__engine.isReadOnly(item, self._errorCode, self._errorString)
    
    def searchableLandmarkAttributeKeys(self):
        '''
        Returns a list of landmark attribute keys that may be used in a
        QLandmarkAttributeFilter.
        
        @rtype: list
        '''
        if not self.__engine:
            return []
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        
        return self.__engine.searchableLandmarkAttributeKeys(self._errorCode,
                                                             self._errorString)
    
    def managerName(self):
        '''
        Returns the manager name for this QLandmarkManager.

        The manager name usually takes the format of a reverse domain string.  An example
        of a manager name is \c com.nokia.qt.landmarks.engines.sqlite
        
        @rtype: str
        '''
        if not self.__engine:
            return ""
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        return self.__engine.managerName()
    
    def managerParameters(self):
        '''
        Return the parameters relevant to the creation of this QLandmarkManager.

        The parameters may be viewed as a set of key-value pairs.  Each manager
        may have a different set of parameters depending upon its backend implementation.
        
        @rtype: dict
        '''
        if not self.__engine:
            return {}
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        return self.__engine.managerParameters()
    
    def managerUri(self):
        '''
        Return the uri describing this QLandmarkManager, consisting of the manager name and any parameters.
        @rtype: str
        '''
        if not self.__engine:
            return ""
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        return self.__engine.managerUri()
    
    def managerVersion(self):
        '''
        Returns the engine backend implementation version number.
        @rtype: int
        '''
        if not self.__engine:
            return 0
        
        self._errorCode = LandmarkManager.NoError
        self._errorString = ""
        self._errorMap.clear()
        
        return self.__engine.managerVersion()
    
    @staticmethod
    def availableManagers():
        '''
        Returns a list of available manager names that can
        be used when constructing a QLandmarkManager
        @rtype: list
        '''
        return LandmarkManager._factories.keys()
    
    @staticmethod
    def addFactory(factory):
        '''
        Adds a factory
        
        @param factory: LandmarkManagerEngineFactory
        @type factory:
        '''
        LandmarkManager._factories[factory.managerName()] = factory
    
    @staticmethod
    def buildUri(managerName, params, implementationVersion=-1):
        '''
        Returns a URI that completely describes a manager implementation/datastore,
        and the parameters with which to instantiate the manager,
        from the given \a managerName, \a params and an optional \a implementationVersion
        
        @param managerName: The name of the manager
        @type managerName: str
        @param params: Params
        @type params: dict
        @param implementationVersion: Optional version, defaults to -1
        @type implementationVersion: int
        '''
        escapedParams = []
        
        for key in params.keys():
            arg = params[key]
            arg = unicode(arg).replace('&','&amp;').replace('=', '&equ;')
            key = unicode(key).replace('&','&amp;').replace('=', '&equ;')
            escapedParams.append(key + '=' + arg)
        
        if implementationVersion != -1:
            versionString = LandmarkManager.QTLANDMARKS_IMPLEMENTATION_VERSION_NAME
            versionString = u"{0}{1}{2}".format(versionString.format,'=',
                                                implementationVersion)
            escapedParams.append(versionString)
        
        return u"{0}:{1}:{2}".format(LandmarkManager.URI_PREFIX, managerName,
                                     u"&".join(escapedParams))
    
    @staticmethod
    def fromUri(storeUri, parent=None):
        '''
        Constructs a QLandmarkManager whose implementation, store and parameters are specified in the given \a storeUri,
        and whose parent object is \a parent.
        
        @param storeUri: The uri for the manager
        @type storeUri: str
        @param parent: Parent object
        @type parent: QObject
        @rtype: LandmarkManager
        '''
        
        if not storeUri:
            return LandmarkManager("",{},parent)
        
        id = ""
        parsed = LandmarkManager.parseUri(storeUri)
        if isinstance(parsed, dict) and parsed.has_key('managerName') and\
            parsed.has_key('params'):
            return LandmarkManager(parsed['managerName'],parsed['parameters'],
                                   parent)
        else:
            return None 
        
    @staticmethod
    def parseUri(uri, managerName=None, params=None):
        '''
        Splits the given \a uri into the manager name and parameters that it describes, and places the information
        into the memory addressed by \a pManagerName and \a pParams respectively.  Returns true if \a uri could be split successfully,
        otherwise returns false
        
        Format: qtlandmarks:<managerid>:<key>=<value>&<key>=<value>
        it is assumed the prefix(qtlandmarks) and managerid cannot contain ':'
        it is assumed keys and values do not contain '=' or '&'
        but can contain &amp; and &equ;
        
        @param uri: The uri as string "qtlandmarks:<managerid>:<key>=<value>&<key>=<value>"
        @type uri: str
        @param managerName: unused, only for compatiblity reasons
        @type managerName: str
        @param params: unused, only for compatiblity reasons
        @type params: dict
        @rtype: dict
        '''
        
        colonSplit = uri.split(':')
        prefix = colonSplit[0]
        
        if prefix != LandmarkManager.URI_PREFIX:
            return False
        
        managerName = colonSplit[1]
        
        if not managerName.strip():
            return False
        
        firstParts = prefix + ':' + managerName + ':'
        paramString = colonSplit[2]
        params = paramString.split()
        rParams = {}
        
        if paramString:
            for part in re.split('&(?!(amp;|equ;))', params):
                if part is not None:
                    chunk = part.split('=')
                    if len(chunk != 2):
                        return False
                    arg = chunk[0]
                    param = chunk[1]
                    
                    arg = arg.replace('&equ;','=').replace('&amp;','&')
                    param = param.replace('&equ;','=').replace('&amp;','&')
                    rParams[arg] = param
        return {'managerName':managerName, 'parameters':rParams}
    
    def connectNotify(self, signal):
        if self.__isConnected or not self.__engine:
            return
        if signal in (unicode(SIGNAL('landmarksAdded(PyQt_PyObject)')),
                      unicode(SIGNAL('landmarksChanged(PyQt_PyObject)')),
                      unicode(SIGNAL('landmarksRemoved(PyQt_PyObject)')),
                      unicode(SIGNAL('categoriesAdded(PyQt_PyObject)')),
                      unicode(SIGNAL('categoriesChanged(PyQt_PyObject)')),
                      unicode(SIGNAL('categoriesRemoved(PyQt_PyObject)')),
                      unicode(SIGNAL('dataChanged()'))):
            
            self.__engine.landmarksAdded.connect(self.landmarksAdded)
            self.__engine.landmarksChanged.connect(self.landmarksChanged)
            self.__engine.landmarksRemoved.connect(self.landmarksRemoved)
            self.__engine.categoriesAdded.connect(self.categoriesAdded)
            self.__engine.categoriesChanged.connect(self.categoriesChanged)
            self.__engine.categoriesRemoved.connect(self.categoriesRemoved)
            self.__isConnected = True
            
        return QObject.connectNotify(self, signal)
    
    def disconnectNotify(self, signal):
        if not self.__isConnected or not self.__engine:
            return
        
        if signal in (unicode(SIGNAL('landmarksAdded(PyQt_PyObject)')),
                      unicode(SIGNAL('landmarksChanged(PyQt_PyObject)')),
                      unicode(SIGNAL('landmarksRemoved(PyQt_PyObject)')),
                      unicode(SIGNAL('categoriesAdded(PyQt_PyObject)')),
                      unicode(SIGNAL('categoriesChanged(PyQt_PyObject)')),
                      unicode(SIGNAL('categoriesRemoved(PyQt_PyObject)')),
                      unicode(SIGNAL('dataChanged()'))):
            
            self.__engine.landmarksAdded.disconnect(self.landmarksAdded)
            self.__engine.landmarksChanged.disconnect(self.landmarksChanged)
            self.__engine.landmarksRemoved.disconnect(self.landmarksRemoved)
            self.__engine.categoriesAdded.disconnect(self.categoriesAdded)
            self.__engine.categoriesChanged.disconnect(self.categoriesChanged)
            self.__engine.categoriesRemoved.disconnect(self.categoriesRemoved)
            self.__isConnected = False
            
        return QObject.disconnectNotify(self, signal)
    
    def __createEngine(self, managerName, parameters):
        '''
        Creates the engine
        
        @param managerName: The name of the manager
        @type managerName: str
        @param parameters: params
        @type parameters: dict
        '''
        if managerName not in self.availableManagers():
            self._errorCode = LandmarkManager.InvalidManagerError
            self._errorString = 'The landmark manager, {0}, was not found'.format(managerName)
            self.__engine = None
            return
        
        factory = LandmarkManager._factories[managerName]
        
        if parameters.has_key(self.QTLANDMARKS_IMPLEMENTATION_VERSION_NAME):
            implementationVersion = int(parameters[self.QTLANDMARKS_IMPLEMENTATION_VERSION_NAME])
            raise NotImplementedError("Currently no version handling supported")
        else:
            implementationVersion = -1
        
        self.__engine = factory.engine(parameters, self._errorCode,
                                       self._errorString)
        if not self.__engine:
            if self._errorCode == LandmarkManager.NoError:
                self._errorCode = LandmarkManager.InvalidManagerError
                self._errorString = 'The landmark manager could not return the requested engine instance'
    
    @staticmethod
    def getEngine(manager):
        if manager.getEngine():
            return manager.getEngine()
        return None
    
    @staticmethod
    def loadFactories():
        pass
    
    @staticmethod
    def factories(reload=False):
        return LandmarkManager._factories
    
    
    
    
        
        
    