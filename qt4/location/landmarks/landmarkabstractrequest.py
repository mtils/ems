'''
Created on 24.10.2011

@author: michi
'''
from PyQt4.QtCore import QObject, QMutexLocker, QMutex, pyqtSignal
from ems.qt4.location.landmarks.landmarkmanager import LandmarkManager #@UnresolvedImport

class LandmarkAbstractRequest(QObject):
    '''
    The QLandmarkAbstractRequest class provides the interface
    from which all asynchronous request classes inherit.

    It allows a client to asynchronously request some functionality of a
    particular LandmarkManager. Instances of the class will emit signals when
    the state of the request changes, or when more results become available.

    Clients should not attempt to create instances of this class directly, but
    should instead use the use-case-specific classes derived from this class.

    All such request classes have a similar interface: clients set the
    parameters of the asynchronous call, then call the start() slot of the request. The manager
    will then enqueue or begin to process the request, at which point the
    request's state will transition from the \c InactiveState to \c ActiveState.
    After any state transition, the request will emit the stateChanged()
    signal. The manager may (if it supports it)
    periodically update the request with results, at
    which point the request will emit the resultsAvailable() signal. These
    results are not guaranteed to have a stable ordering. Error information is
    considered a result, so some requests will emit the resultsAvailable()
    signal even if no results are possible from the request (for example, a
    landmark remove request) when the manager updates the request with
    information about any errors which may have occurred.

    Clients can choose which signals they wish to handle from a request. If the
    client is not interested in interim results, they can choose to handle only
    the stateChanged() signal, and in the slot to which that signal is
    connected, check whether the state has changed to the \c FinishedState
    (which signifies that the manager has finished handling the request, and
    that the request will not be updated with any more results).  If the client
    is not interested in any results (including error information), they may
    choose to delete the request after calling \l start(), or simply may not
    connect the the request's signals to any slots.  (Please see the note
    below if you are working on Symbian with QtMobility 1.1.0)

    If the request is allocated via operator new, the client must delete the
    request when they are no longer using it in order to avoid leaking memory.
    That is, the client retains ownership of the request.

    The client may delete a heap-allocated request in various ways: by deleting
    it directly (but not within a slot connected to a signal emitted by the
    request), or by using the deleteLater() slot to schedule the request for
    deletion when control returns to the event loop (from within a slot
    connected to a signal emitted by the request, for example \l
    stateChanged()).

    An active request may be deleted by the client, but the client will
    not receive notifications about whether the request succeeded or not,
    nor the results of the request.

    Because clients retain ownership of any request object, and may delete a
    request object at any time, the manager engine,  implementers must be
    careful to ensue that they do not assume that a request has not been
    deleted at some time point during processing of a request, particularly
    if the engine has a multithreaded implementation.
    '''
    
    'State Enum: Defines the possible types of asynchronous requests.'
    InactiveState = 0
    'Operation not yet started.'
    
    ActiveState = 1
    'Operation started, not yet finished.'
    
    FinishedState = 2
    '''Operation completed.  (Can be mean either successful or
            unsuccessful completion)'''
    
    
    'Request Type Enum'
    InvalidRequest = 0
    'An invalid request'
    
    LandmarkIdFetchRequest = 1
    'A request to fetch a list of landmark identifiers.'
    
    CategoryIdFetchRequest = 2
    'A request to fetch a list of catgory identifiers.'
    
    LandmarkFetchRequest = 3
    'A request to fetch a list of landmarks'
    
    LandmarkFetchByIdRequest = 4
    'A request to fetch a list of landmarks by id.'
    
    CategoryFetchRequest = 5
    'A request to fetch a list of categories'
    
    CategoryFetchByIdRequest = 6
    'A request to fetch a list of categories by id'
    
    LandmarkSaveRequest = 7
    'A request to save a list of landmarks.'
    
    LandmarkRemoveRequest = 8
    'A request to remove a list of landmarks.'
    
    CategorySaveRequest = 9
    'A request to save a list of categories'
    
    CategoryRemoveRequest = 10
    'A request to remove a list of categories.'
    
    ImportRequest = 11
    'A request import landmarks.'
    
    ExportRequest = 12
    'A request export landmarks.'
    
    resultsAvailable = pyqtSignal()
    '''This signal is emitted when new results are available.  Results
      can include the operation error which may be accessed via error(),
      or derived-class specific results which are accessible through
      the derived class API.'''
    
    stateChanged = pyqtSignal(int)
    '''This signal is emitted when the state of the request is changed.  The new state of
    the request will be contained in \a newState.'''
    
    
    
    @staticmethod
    def _notifyEngine(request):
        '''
        @param request: The LandmarkRequest
        @type request: LandmarkAbstractRequest 
        '''
        ml = QMutexLocker(request._mutex)
        engine = request.getEngine(request.getEngine(request.manager()))
        ml.lock()
        if engine:
            engine.requestDestroyed(request)
        
    
    def __init__(self, manager, parent=None):
        '''
        Constructs a new, invalid asynchronous request with the given manager and parent.
        
        @param manager: The given manager
        @type manager: LandmarkManager
        @param parent: A parent Object
        @type parent: QObject
        '''
        self.__manager = manager
        self._type = LandmarkAbstractRequest.InvalidRequest
        self._state = LandmarkAbstractRequest.InactiveState
        self._error = 0
        self._errorString = ""
        self._mutex = QMutex()
        QObject.__init__(self, parent)
        raise NotImplementedError("This is a pseudo-abstract class. Don't " +
                                  "instanciate this class directly and if " + 
                                  "calling 'super().init(), catch this " +
                                  "exception")
    
    def __del__(self):
        '''
        Destroys the asynchronous request.  Because the request object is effectiely a handle to a
        request operation, the operation may continue or it may just be canceled, depending upon
        the enine implementation, even though the request itself has been destroyed.
        The sqlite engine continues the operation behind the scenes if the
        request is destroyed whilst active.  For the symbian engine see the note below.
        '''
        LandmarkAbstractRequest._notifyEngine(self)
    
    def type_(self):
        '''
        Returns the type of this asynchronous request.
        @rtype: int
        '''
        ml = QMutexLocker(self._mutex)
        return self._type
    
    def state(self):
        '''
        Returns the state of the request
        '''
        ml = QMutexLocker(self._mutex)
        return self._state
    
    def isInactive(self):
        '''
        Returns true if the request is in the \c QLandmarkAbstractRequest::Inactive state;
        otherwise, returns false.
        
        @rtype: bool
        '''
        ml = QMutexLocker(self._mutex)
        return (self._state == LandmarkAbstractRequest.InactiveState)
    
    def isActive(self):
        '''
        Returns true if the request is in the \c QLandmarkAbstractRequest::Active state;
        otherwise, returns false.
        
        @rtype: bool
        '''
        ml = QMutexLocker(self._mutex)
        return (self._state == LandmarkAbstractRequest.ActiveState)
    
    def isFinished(self):
        '''
        Returns true if the request is in the \c QLandmarkAbstractRequest::Finished state;
        otherwise, returns false.
        
        @rtype: bool
        '''
        ml = QMutexLocker(self._mutex)
        return (self._state == LandmarkAbstractRequest.FinishedState)
    
    def error(self):
        '''
        Returns the overall error of the most recent asynchronous operation.
        
        @return: LandmarkManager.Error Enum
        @rtype: int
        '''
        ml = QMutexLocker(self._mutex)
        return self._error
    
    def errorString(self):
        '''
        Returns a human readable string of the last error
        that occurred.  This error string is intended to be used
        by developers only and should not be seen by end users.
        
        @rtype: str
        '''
        ml = QMutexLocker(self._mutex)
        return self._errorString
    
    def manager(self):
        '''
        Returns a pointer to the landmark manager which
        this request operates on.
        
        @rtype: LandmarkManager
        '''
        ml = QMutexLocker(self._mutex)
        return self.__manager
    
    def setManager(self, manager):
        '''
        Sets the \a manager which this request operates on.

        Note that if a NULL manager is set, the functions
        start(), cancel() and waitForFinished() will return false and
        error will be set to QLandmarkManager::InvalidManagerError.
    
        A manager cannot be assigned while the request is in the
        QLandmarkAbstractRequest::ActiveState.
        
        @param manager: The landmark manager
        @type manager: LandmarkManager
        '''
        ml = QMutexLocker(self._mutex)
        if self._state == LandmarkAbstractRequest.ActiveState and self.__manager:
            return
        self.__manager = manager
    
    def start(self):
        '''
        Attempts to start the request.

        Returns true if the request was started, otherwise false. Trying to start a
        request that is already active returns false.
        \sa cancel().
        
        @rtype: bool
        '''
        ml = QMutexLocker(self._mutex)
        if not self.__manager:
            self._error = LandmarkManager.BadArgumentError
            self._errorString = 'No manager assigned to landmark request object'
            return False
        
        engine = self.__manager.engine()
        if not engine:
            self._error = LandmarkManager.InvalidManagerError
            self._errorString = "The manager is invalid"
            return False
        
        if self._state != LandmarkAbstractRequest.ActiveState:
            ml.unlock()
            return engine.startRequest(self)
        else:
            return False
    
    def cancel(self):
        '''
        Notifies the request that it should be canceled.

        Returns true if the request was successfully notified
        that it should be canceled.  The request may or may not honor
        the cancel notification.  Returns false if the notification
        could not be made or the request is not in the
        QLandmarkManager::Active state.
        
        @rtype: bool
        '''
        ml = QMutexLocker(self._mutex)
        if not self.__manager:
            self._error = LandmarkManager.BadArgumentError
            self._errorString = "No manager assigned to landmark request object"
            return False
        
        engine = self.__manager.engine()
        
        if self._state == LandmarkAbstractRequest.ActiveState:
            ml.unlock()
            return engine.cancelRequest(self)
        else:
            return False
    
    def waitForFinished(self, msecs):
        '''
        Blocks until the request has been completed or until \a msecs milliseconds
        has elapsed.  If \a msecs is zero or negative, this function will block indefinitely.
    
        Returns true if the request was canceled or completed
        within the given period, otherwise returns false.  Some backends may be unable
        to support this  operation safely and will return false immediately.
    
        (Note: This function is not supported for an import request
        with the symbian manager which always returns false.  As of
        Qt Mobility 1.1.1 waitForFinished() is supported using the sqlite manager).
    
        Note that any signals generated while waiting for the request to be complete
        may be queued and delivered sometime after this function has returned, when
        the calling thread's event loop is dispatched.  If your code depends on
        your slots being invoked, you may need to process events after calling
        this function.
        
        @param msecs: The milliseconds
        @type msecs: int
        '''
        ml = QMutexLocker(self._mutex)
        
        if not self.__manager:
            self._error = LandmarkManager.BadArgumentError
            self._errorString = "No manager assigned to landmark request object"
            return False
        
        engine = self.__manager.engine()
        
        if self._state == LandmarkAbstractRequest.ActiveState:
            ml.unlock()
            return engine.waitForRequestFinished(self, msecs)
        elif self._state == LandmarkAbstractRequest.FinishedState:
            return True
        else:
            return False
    
    
        
    
    