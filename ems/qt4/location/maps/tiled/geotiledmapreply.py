'''
Created on 03.11.2011

@author: michi
'''
from PyQt4.QtCore import QObject, pyqtSignal
from geotiledmaprequest import GeoTiledMapRequest #@UnresolvedImport

class GeoTiledMapReply(QObject):
    '''
    \brief The QGeoTiledMapReply class manages a tile fetch operation started
    by an instance of QGeoTiledManagerEngine.

    \inmodule QtLocation

    \ingroup maps-impl-tiled

    \since 1.2

    Instances of QGeoTiledMapReply manage the state and results of these
    operations.

    The isFinished(), error() and errorString() methods provide information
    on whether the operation has completed and if it completed successfully.

    The finished() and error(QGeoTiledMapReply::Error,QString)
    signals can be used to monitor the progress of the operation.

    It is possible that a newly created QGeoTiledMapReply may be in a finished
    state, most commonly because an error has occurred. Since such an instance
    will never emit the finished() or
    error(QGeoTiledMapReply::Error,QString) signals, it is
    important to check the result of isFinished() before making the connections
    to the signals.

    If the operation completes successfully the results will be able to be
    accessed with mapImageData() and mapImageFormat().
    '''
    
    "Error Enum"
    NoError = 0
    'No error has occurred.'
    
    CommunicationError = 1
    'An error occurred while communicating with the service provider.'
    
    ParseError = 2
    '''The response from the service provider was in an unrecognizable format.
       supported by the service provider.'''
    
    UnknownError = 3
    'An error occurred which does not fit into any of the other categories.'
    
    finished = pyqtSignal()
    '''This signal is emitted when this reply has finished processing.

    If error() equals QGeoTiledMapReply::NoError then the processing
    finished successfully.

    This signal and QGeoRoutingManager::finished() will be
    emitted at the same time.

    \note Do no delete this reply object in the slot connected to this
    signal. Use deleteLater() instead.

    \fn void QGeoTiledMapReply::error(QGeoTiledMapReply::Error error, const QString &errorString)

    This signal is emitted when an error has been detected in the processing of
    this reply. The finished() signal will probably follow.

    The error will be described by the error code \a error. If \a errorString is
    not empty it will contain a textual description of the error.

    This signal and QGeoRoutingManager::error() will be emitted at the same time.

    \note Do no delete this reply object in the slot connected to this
    signal. Use deleteLater() instead.'''
    
    errorOccured = pyqtSignal(int, str)
    '''This signal is emitted when an error has been detected in the processing of
    this reply. The finished() signal will probably follow.

    The error will be described by the error code \a error. If \a errorString is
    not empty it will contain a textual description of the error.

    \note Do no delete this reply object in the slot connected to this
    signal. Use deleteLater() instead.'''
    
    def __init__(self, requestOrError, errorStringOrParent=None, parent=None):
        self._request = None
        if isinstance(requestOrError, GeoTiledMapRequest):
            self._request = requestOrError
            if isinstance(errorStringOrParent, QObject):
                parent = errorStringOrParent
            self._error = GeoTiledMapReply.NoError
            self._errorString = ""
        else:
            self._error = requestOrError
            self._errorString = errorStringOrParent
        
        QObject.__init__(self, parent)
        self._isFinished = False
        self._isCached = False
        self._mapImageData = ""
        self._mapImageFormat = 0
    
    def _setFinished(self, finished):
        self._isFinished = finished
        if self._isFinished:
            self.finished.emit()
    
    def isFinished(self):
        return self._isFinished
    
    def _setError(self, error, errorString):
        '''
        Sets the error state of this reply to \a error and the textual
        representation of the error to \a errorString.
    
        This wil also cause error() and finished() signals to be emitted, in that
        order.
        
        @param error: The error
        @type error: int
        @param errorString: An error string
        @type errorString: str
        '''
        self._error = error
        self._errorString = errorString
        
        self.errorOccured.emit(error, errorString)
        self._setFinished(True)
    
    def error(self):
        '''
        Returns the error state of this reply.

        If the result is QGeoTiledMapReply::NoError then no error has occurred.
        
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
        QGeoTiledMapReply::error() is equal to QGeoTiledMapReply::NoError.
        @rtype: str
        '''
        return self._errorString
    
    def isChached(self):
        '''
        Returns whether the reply is coming from a cache.
        @rtype: bool
        '''
        return self._isCached
    
    def _setCached(self, cached):
        '''
        Sets whether the reply is coming from a cache to \a cached.
        
        @param cached: Sets if cached
        @type cached: bool
        '''
        self._isCached = cached
    
    def request(self):
        '''
        Returns the request which corresponds to this reply.
        @rtype: GeoTiledMapReply
        '''
        return self._request
    
    def mapImageData(self):
        '''
        Returns the tile image data.
        '''
        return self._mapImageData
    
    def _setMapImageData(self, data):
        '''
        Sets the tile image data to \a data.
        
        @param data: The data
        @type data: str
        '''
        self._mapImageData = data
    
    def mapImageFormat(self):
        '''
        Returns the format of the tile image.
        @rtype: int
        '''
        return self._mapImageFormat
    
    def setMapImageFormat(self, format_):
        '''
        Sets the format of the tile image to \a format.
        
        @param format: The format of the tile image
        @type format: int
        '''
        self._mapImageFormat = format_
    
    def abort(self):
        '''
        Cancels the operation immediately.

        This will do nothing if the reply is finished.
        '''
        if not self._isFinished:
            self._setFinished(True)
    
    