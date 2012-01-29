'''
Created on 24.10.2011

@author: michi
'''
from PyQt4.QtCore import QObject, pyqtSignal
from ems.qt4.location.geoboundingarea import GeoBoundingArea


class GeoSearchReply(QObject):
    '''
    \brief The QGeoSearchReply class manages an operation started by an
    instance of QGeoSearchManager.


    \inmodule QtLocation
    \since 1.1

    \ingroup maps-places

    Instances of QGeoSearchReply manage the state and results of these
    operations.

    The isFinished(), error() and errorString() methods provide information
    on whether the operation has completed and if it completed successfully.

    The finished() and error(QGeoSearchReply::Error,QString)
    signals can be used to monitor the progress of the operation.

    It is possible that a newly created QGeoSearchReply may be in a finished
    state, most commonly because an error has occurred. Since such an instance
    will never emit the finished() or
    error(QGeoSearchReply::Error,QString) signals, it is
    important to check the result of isFinished() before making the connections
    to the signals. The documentation for QGeoSearchManager demonstrates how
    this might be carried out.

    If the operation completes successfully the results will be able to be
    accessed with places().
    '''
    
    'enum Error'
    NoError = 0
    'No error has occurred.'
    
    EngineNotSetError = 1
    'The search manager that was used did not have a QGeoSearchManagerEngine instance associated with it.'
    
    CommunicationError = 2
    'An error occurred while communicating with the service provider.'
    
    ParseError = 3
    'The response from the service provider was in an unrecognizable format.'
    
    UnsupportedOptionError = 4
    '''The requested operation or one of the options for the operation are not
        supported by the service provider.'''
    
    CombinationError = 5
    'An error occurred while results where being combined from multiple sources.'
    
    UnknownError = 6
    'An error occurred which does not fit into any of the other categories.'
    
    _error = 0
    
    _errorString = ""
    _isFinished = False

    _viewport = None
    _places = []

    _limit = -1
    _offset = 0
    
    finished = pyqtSignal()
    '''This signal is emitted when this reply has finished processing.

    If error() equals QGeoSearchReply::NoError then the processing
    finished successfully.

    This signal and QGeoSearchManager::finished() will be
    emitted at the same time.

    \note Do no delete this reply object in the slot connected to this
    signal. Use deleteLater() instead.'''
    
    errorOccured = pyqtSignal(int, str)
    '''This signal is emitted when an error has been detected in the processing of
    this reply. The finished() signal will probably follow.

    The error will be described by the error code \a error. If \a errorString is
    not empty it will contain a textual description of the error.

    This signal and QGeoSearchManager::error() will be emitted at the same time.

    \note Do no delete this reply object in the slot connected to this
    signal. Use deleteLater() instead.'''
    
    def __init__(self, errorOrParent=None, errorString=None, parent=None):
        '''
        GeoSearchReply(parent):
        Constructs a search reply with the specified \a parent.
        
        GeoSearchReply(error, errorString, parent):
        Constructs a search reply with a given \a error and \a errorString and the specified \a parent.
        
        @param errorOrParent: error Or parent object
        @type errorOrParent: int|QObject
        @param errorString: the errorString, if any
        @type errorString: basestring
        @param parent: Parent QObject (optional)
        @type parent: QObject
        '''
        if isinstance(errorOrParent, QObject):
            parent = errorOrParent
            
        elif isinstance(errorOrParent, int):
            self._error = errorOrParent
            self._errorString = errorString
        self._places = []
        QObject.__init__(self, parent)
        
    def _setFinished(self, finished):
        '''
        Sets whether or not this reply has finished to \a finished.

        If \a finished is true, this will cause the finished() signal to be
        emitted.
    
        If the operation completed successfully, QGeoSearchReply::setPlaces()
        should be called before this function. If an error occurred,
        QGeoSearchReply::setError() should be used instead.
        
        @param finished: Finished -> true
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
        
        @param error: The error code
        @type error: int
        @param errorString: The error message, dev readable
        @type errorString: basestring
        '''
        self._error = error
        self._errorString = errorString
        self.errorOccured.emit(error, errorString)
        self._setFinished(True)
    
    def error(self):
        '''
        Returns the error state of this reply.

        If the result is QGeoSearchReply::NoError then no error has occurred.
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
        QGeoSearchReply::error() is equal to QGeoSearchReply::NoError.
        @rtype: basestring
        '''
        return self._errorString
    
    def _setViewport(self, viewport):
        '''
        Sets the viewport which contains the results to \a viewport.
        
        @param viewport: The viewport
        @type viewport: GeoBoundingArea
        '''
        self._viewport = viewport
    
    def viewport(self):
        '''
        Returns the viewport which contains the results.

        This function will return 0 if no viewport bias
        was specified in the QGeoSearchManager function which created this reply.
        @rtype: GeoBoundingArea
        '''
        return self._viewport
    
    def places(self):
        '''
        Returns a list of places.

        The places are the results of the operation corresponding to the
        QGeoSearchManager function which created this reply.
        @rtype: list
        '''
        return self._places
    
    def addPlace(self, place):
        '''
        Adds \a place to the list of places in this reply.
        
        @param place: An place added to result
        @type place: GeoPlace
        '''
        self._places.append(place)
    
    def _setPlaces(self, places):
        '''
        Sets the list of \a places in the reply.
        
        @param places: The new places (list of GeoPlace objects)
        @type places: list
        '''
        self._places = places
    
    def abort(self):
        '''
        Cancels the operation immediately.

        This will do nothing if the reply is finished.
        '''
        if not self._isFinished:
            self._setFinished(True)
    
    def limit(self):
        '''
        Returns the limit on the number of responses from each data source.

        If no limit was set this function will return -1.
    
        This may be more than places().length() if the number of responses
        was less than the number requested.
    
        If QGeoSearchManager::search() is used along with
        QGeoSearchManager::setAdditionalLandmarkManagers the number of results can
        be as high as limit * (1 + number of additional landmark managers).
        @rtype: int
        '''
        return self._limit
    
    def offset(self):
        '''
        Returns the offset into the entire result set at which to start
        fetching results.
        @rtype: int
        '''
        return self._offset
    
    def _setLimit(self, limit):
        '''
        Sets the limit on the number of responses from each data source to \a limit.

        If \a limit is -1 then all available responses will be returned.
        
        @param limit: The limit for result
        @type limit: int
        '''
        self._limit = limit
    
    def _setOffset(self, offset):
        '''
        Sets the offset in the entire result set at which to start
        fetching result to \a offset.
        
        @param offset: The offset
        @type offset: int
        '''
        self._offset = offset
    
    
    
    