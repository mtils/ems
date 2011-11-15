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
    
    errorOccured = pyqtSignal(int, str)
    
    _error = 0
    
    _errorString = basestring()
    
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
            pass
        QObject.__init__(self, parent)
        
        