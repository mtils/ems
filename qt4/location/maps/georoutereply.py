'''
Created on 15.11.2011

@author: michi
'''
from PyQt4.QtCore import QObject, pyqtSignal
from ems.qt4.location.maps.georouterequest import GeoRouteRequest #@UnresolvedImport

class GeoRouteReply(QObject):
    '''
     \brief The QGeoRouteReply class manages an operation started by an instance
    of QGeoRoutingManager.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps-routing

    Instances of QGeoRouteReply manage the state and results of these
    operations.

    The isFinished(), error() and errorString() methods provide information
    on whether the operation has completed and if it completed successfully.

    The finished() and error(QGeoRouteReply::Error,QString)
    signals can be used to monitor the progress of the operation.

    It is possible that a newly created QGeoRouteReply may be in a finished
    state, most commonly because an error has occurred. Since such an instance
    will never emit the finished() or
    error(QGeoRouteReply::Error,QString) signals, it is
    important to check the result of isFinished() before making the connections
    to the signals. The documentation for QGeoRoutingManager demonstrates how
    this might be carried out.

    If the operation completes successfully the results will be able to be
    accessed with routes().
    '''
    
    'Error Enum'
    NoError = 0
    'No error has occurred.'
    
    EngineNotSetError = 1
    'The routing manager that was used did not have a QGeoRoutingManagerEngine instance associated with it.'
    
    CommunicationError = 2
    'An error occurred while communicating with the service provider.'
    
    ParseError = 3
    'The response from the service provider was in an unrecognizable format.'
    
    UnsupportedOptionError = 4
    '''The requested operation or one of the options for the operation are not
        supported by the service provider.'''
    
    UnknownError = 5
    'An error occurred which does not fit into any of the other categories.'
    
    finished = pyqtSignal()
    '''This signal is emitted when this reply has finished processing.

    If error() equals QGeoRouteReply::NoError then the processing
    finished successfully.

    This signal and QGeoRoutingManager::finished() will be
    emitted at the same time.

    \note Do no delete this reply object in the slot connected to this
    signal. Use deleteLater() instead.'''
    
    errorOccured = pyqtSignal(int, str)
    '''This signal is emitted when an error has been detected in the processing of
    this reply. The finished() signal will probably follow.

    The error will be described by the error code \a error. If \a errorString is
    not empty it will contain a textual description of the error.

    This signal and QGeoRoutingManager::error() will be emitted at the same time.

    \note Do no delete this reply object in the slot connected to this
    signal. Use deleteLater() instead.'''
    
    _error = 0
    
    _errorString = ""
    
    _isFinished = False
    
    _request = GeoRouteRequest
    
    _routes = []
    
    def __init__(self, requestOrError, parentOrErrorString=None, parent=None):
        '''
        Constructs a route reply object based on \a request, with the specified \a parent.
        
        @param request: The request
        @type request: GeoRouteRequest
        @param parent: parent QObject
        @type parent: QObject
        '''
        if isinstance(requestOrError, int):
            self._error = requestOrError
            self._errorString = parentOrErrorString
            self._isFinished = True
        else:
            self._request = requestOrError
            if isinstance(parentOrErrorString, QObject):
                parent = parentOrErrorString
        QObject.__init__(self, parent)
    
    def _setFinished(self, finished):
        '''
        Sets whether or not this reply has finished to \a finished.

        If \a finished is true, this will cause the finished() signal to be
        emitted.
    
        If the operation completed successfully, QGeoRouteReply::setRoutes() should
        be called before this function. If an error occurred,
        QGeoRouteReply::setError() should be used instead.
        
        @param finished: Finished or not
        @type finished: bool
        '''
        self._isFinished = finished
        if self._isFinished:
            self.finished.emit()
    
    def isFinished(self):
        '''
        Return true if the operation completed successfully or encountered an
        error which cause the operation to come to a halt.
        @rtype: bool
        '''
        return self._isFinished
    
    def _setError(self, error, errorString):
        '''
        Sets the error state of this reply to \a error and the textual
        representation of the error to \a errorString.
    
        This wil also cause error() and finished() signals to be emitted, in that
        order.
        
        @param error: The error number
        @type error: int
        @param errorString: The errorstring (dev errorstring, not public)
        @type errorString: basestring
        '''
        self._error = error
        self._errorString = errorString
        self.errorOccured.emit(error, errorString)
        self._setFinished(True)
    
    def error(self):
        '''
        Returns the error state of this reply.

        If the result is QGeoRouteReply::NoError then no error has occurred.
        @rtype: int
        '''
        return self._error
    
    def errorString(self):
        '''
        Returns the textual representation of the error state of this reply.

        If no error has occurred this will return an empty string.  It is possible
        that an error occurred which has no associated textual representation, in
        which case this will also return an empty string.
    
        To determine whether an error has occurred, check to see if
        QGeoRouteReply::error() is equal to QGeoRouteReply::NoError.
        @rtype: basestring
        '''
        return self._errorString
    
    def request(self):
        '''
        Returns the route request which specified the route.
        @rtype: GeoRouteRequest
        '''
        return self._request
    
    def routes(self):
        '''
        Returns the list of routes which were requested.
        @rtype: list
        '''
        return self._routes
    
    def _setRoutes(self, routes):
        '''
        Sets the list of routes in the reply to \a routes.
        @param routes: List of GeoRoute
        @type routes: list
        '''
        self._routes = routes
    
    def abort(self):
        '''
        Cancels the operation immediately.

        This will do nothing if the reply is finished.
        '''
        if not self.isFinished():
            self._setFinished(True)
    
    
    
        