'''
Created on 24.10.2011

@author: michi
'''
from PyQt4.QtCore import QObject, QMutexLocker

from landmarkabstractrequest import LandmarkAbstractRequest  #@UnresolvedImport
from landmarkfilter import LandmarkFilter #@UnresolvedImport

class LandmarkFetchRequest(LandmarkAbstractRequest):
    '''
    The QLandmarkFetchRequest class allows a client to asynchronously
    request a list of landmarks from a landmark manager.

    For a QLandmarkFetchRequest, the resultsAvailable() signal will be emitted when the resultant
    landmarks (which may be retrieved by calling landmarks()) are updated, as well as if
    the overall operation error (which may be retrieved by calling error()) is updated.

    Please see the class documentation for QLandmarkAbstractRequest for more information about
    the usage of request classes and ownership semantics.
    
    '''
    def __init__(self, manager, parent=None):
        '''
        Creates a new landmark fetch request object with the given \a manager \a parent.
        
        @param manager: The given manager
        @type manager: LandmarkManager
        @param parent: A parent Object
        @type parent: QObject
        '''
        try:
            super(LandmarkFetchRequest, self).__init__(manager, parent)
        except NotImplementedError:
            pass
        
        self._filter = LandmarkFilter()
        self._sorting = []
        self._limit = -1
        self._offset = 0
        self._landmarks = []
        
    def filter_(self):
        '''
        Returns the filter which will be used to select the landmarks.

        By default, the filter's type will be a QLandmarkFilter::DefaultFilter
        and thus match all landmarks.
        
        @rtype: LandmarkFilter
        '''
        ml = QMutexLocker(self._mutex)
        return self._filter
    
    def setFilter(self, filter_):
        '''
        Sets the \a filter which will be used to select landmarks.
        
        @param filter: The filter
        @type filter: LandmarkFilter
        '''
        ml = QMutexLocker(self._mutex)
        self._filter = filter_
    
    def sorting(self):
        '''
        Returns the sort ordering which is used to sort the result.  By default
        the sort order list is empty, thus no sorting will take place.
        
        @rtype: list
        '''
        ml = QMutexLocker(self._mutex)
        return self._sorting
    
    def setSorting(self, sorting):
        '''
        Sets the sort ordering of the request to \a sorting.  This
        function will only have an effect on the results if invoked
        prior to calling \l QLandmarkAbstractRequest::start().
        
        @param sorting: The sorting as a list
        @type sorting: list
        '''
        ml = QMutexLocker(self._mutex)
        if isinstance(sorting, list):
            self._sorting = sorting
        else:
            self._sorting = [sorting,]
    
    def limit(self):
        '''
        Returns the maximum number of landmarks to be returned.  By default the limit
        is -1 indicating that all landmarks matching the filter sould be retrieved.
        
        @rtype: int
        '''
        ml = QMutexLocker(self._mutex)
        return self._limit
        
    
    def setLimit(self, limit):
        '''
        Sets the maximum number of landmarks to be returned to \a limit.

        A limit of -1 will retrieve all landmarks that match the filter.
    
        (A limit of 0 will retrieve no landmarks.)
        
        @param limit: The limit
        @type limit: int
        '''
        ml = QMutexLocker(self._mutex)
        self._limit = limit
    
    def offset(self):
        '''
         Returns the index offset for the request.  By default the offset is set to 0.
        The offset determines the first index which is retrieved, it is generally
        used in conjunction with limit() to facilitate paging.
    
        For example, if there are 10 landmarks in the landmark store, setting the offset
        to 2 and limit to 5 will retrieve the 3rd to 7th landmarks inclusively.  (The order
        of the landmarks is specified by the sorting field).
        
        @rtype: int
        '''
        ml = QMutexLocker(self._mutex)
        return self._offset
    
    def setOffset(self, offset):
        '''
        Sets the index \a offset for the request.
        
        @param offset: Offset
        @type offset: int
        '''
        ml = QMutexLocker(self._mutex)
        self._offset = offset
    
    def landmarks(self):
        '''
        Returns the list of landmarks which matched the
        filter.
        
        @rtype: list
        '''
        ml = QMutexLocker(self._mutex)
        return self._landmarks