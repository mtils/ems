'''
Created on 24.10.2011

@author: michi
'''
from PyQt4.QtCore import QObject, pyqtSignal
from ems.qt4.location.maps.georoutingmanagerengine import GeoRoutingManagerEngine #@UnresolvedImport

class GeoRoutingManager(QObject):
    '''
    \brief The QGeoRoutingManager class provides support for geographic routing
    operations.


    \inmodule QtLocation
    \since 1.1

    \ingroup maps-routing

    The calculateRoute() and updateRoute() methods function QGeoRouteReply
    objects, which manage these operations and report on the result of the
    operations and any errors which may have occurred.

    The calculateRoute() function is used to find a route (or routes) that
    follows a set of waypoints and matches various other criteria.  The
    QGeoRouteRequest class is used to specify this information.

    If supportsRouteUpdates() returns true then the QGeoRoutingManager
    supports updating route information based on position updates.  This
    will cause the travel time and distance estimates to be updated, and
    any QGeoRouteSegments already traversed to be removed from the route.

    The updates can be triggered with the updateRoute() function, which makes
    use of the QGeoPositionInfo instances emitted as position updates by
    QGeoPositionInfoSource.

    Instances of QGeoRoutingManager can be accessed with
    QGeoServiceProvider::routingManager().

    A small example of the usage of QGeoRoutingManager and QGeoRouteRequests
    follows:

    \code
class MyRouteHandler : public QObject
{
    Q_OBJECT
public:
    MyRouteHandler(QGeoRoutingManager *routingManager,
                   const QGeoCoordinate &origin,
                   const QGeoCoordinate &destination) {

        QGeoRouteRequest request(origin, destination);

        // The request defaults to the fastest route by car, which is
        // equivalent to:
        // request.setTravelMode(QGeoRouteRequest::CarTravel);
        // request.setRouteOptimization(QGeoRouteRequest::FastestRoute);

        request.setAvoidFeatureTypes(QGeoRouteRequest::AvoidTolls);
        request.setAvoidFeatureTypes(QGeoRouteRequest::AvoidMotorPoolLanes);

        QGeoRouteRequest::AvoidFeaturesTypes avoidableFeatures = routingManager->supportedAvoidFeatureTypes();

        if (!(avoidableFeatures & request.avoidFeatureTypes())) {
            // ... inform the user that the routing manager does not
            // provide support for avoiding tolls and/or motor pool lanes ...
            return;
        }

        QGeoRouteReply *reply = routingManager->calculateRoute(request);

        if (reply->isFinished()) {
            if (reply->error() == QGeoRouteReply::NoError) {
                routeCalculated(reply);
            } else {
                routeError(reply, reply->error(), reply->errorString());
            }
            return;
        }

        connect(routingManager,
                SIGNAL(finished(QGeoRouteReply*)),
                this,
                SLOT(routeCalculated(QGeoRouteReply*)));

        connect(routingManager,
                SIGNAL(error(QGeoRouteReply*,QGeoRouteReply::Error,QString)),
                this,
                SLOT(routeError(QGeoRouteReply*,QGeoRouteReply::Error,QString)));
    }

private slots:
    void routeCalculated(QGeoRouteReply *reply)
    {
        // A route request can ask for several alternative routes ...
        if (reply->routes().size() != 0) {

            // ... but by default it will only get a single route
            QGeoRoute route = reply->routes().at(0);

            //... now we have to make use of the route ...
        }

        reply->deleteLater();
    }

    void routeError(QGeoRouteReply *reply, QGeoRouteReply:Error error, const QString &errorString)
    {
        // ... inform the user that an error has occurred ...
        reply->deleteLater();
    }
};
    \endcode
    '''
    
    _engine = GeoRoutingManagerEngine
    
    finished = pyqtSignal()
    '''This signal is emitted when \a reply has finished processing.

    If reply::error() equals QGeoRouteReply::NoError then the processing
    finished successfully.
    
    This signal and QGeoRouteReply::finished() will be emitted at the same time.
    
    \note Do no delete the \a reply object in the slot connected to this signal.
    Use deleteLater() instead.'''
    
    error = pyqtSignal(int, str)
    '''This signal is emitted when an error has been detected in the processing of
    \a reply.  The QGeoRoutingManager::finished() signal will probably follow.
    
    The error will be described by the error code \a error.  If \a errorString is
    not empty it will contain a textual description of the error.
    
    This signal and QGeoRouteReply::error() will be emitted at the same time.
    
    \note Do no delete the \a reply object in the slot connected to this signal.
    Use deleteLater() instead.'''
    
    def __init__(self, engine, parent=None):
        '''
        Constructs a new manager with the specified \a parent and with the
        implementation provided by \a engine.
    
        This constructor is used internally by QGeoServiceProviderFactory. Regular
        users should acquire instances of QGeoRoutingManager with
        QGeoServiceProvider::routingManager();
        
        @param engine: The GeoRoutingManagerEngine object
        @type engine: GeoRoutingManagerEngine
        @param parent: parent QObject
        @type parent: QObject
        '''
        self._engine = engine
        QObject.__init__(self, parent)
        if self._engine:
            self._engine.setParent(self)
            self._engine.finished.connect(self.finished)
            self._engine.error.connect(self.error)
        else:
            raise TypeError("No valid engine passed")
    
    
    def managerName(self):
        '''
        Returns the name of the engine which implements the behaviour of this
        routing manager.
    
        The combination of managerName() and managerVersion() should be unique
        amongst the plugin implementations.
        @rtype: basestring
        '''
        return self._engine.managerName()
    
    def managerVersion(self):
        '''
        Returns the version of the engine which implements the behaviour of this
        routin manager.
    
        The combination of managerName() and managerVersion() should be unique
        amongst the plugin implementations.
        @rtype: basestring
        '''
        return self._engine.managerVersion()
    
    def calculateRoute(self, request):
        '''
        Begins the calculation of the route specified by \a request.

        A QGeoRouteReply object will be returned, which can be used to manage the
        routing operation and to return the results of the operation.
    
        This manager and the returned QGeoRouteReply object will emit signals
        indicating if the operation completes or if errors occur.
    
        Once the operation has completed, QGeoRouteReply::routes can be used to
        retrieve the calculated route or routes.
    
        If \a request includes features which are not supported by this manager, as
        reported by the methods in this manager, then a
        QGeoRouteReply::UnsupportedOptionError will occur.
    
        The user is responsible for deleting the returned reply object, although
        this can be done in the slot connected to QGeoRoutingManager::finished(),
        QGeoRoutingManager::error(), QGeoRouteReply::finished() or
        QGeoRouteReply::error() with deleteLater().
        
        @param request: The request
        @type request: GeoRouteRequest
        @rtype: GeoRouteReply
        '''
        return self._engine.calculateRoute(request)
    
    def updateRoute(self, route, position):
        '''
        Begins the process of updating \a route based on the current position \a
        position.
    
        A QGeoRouteReply object will be returned, which can be used to manage the
        routing operation and to return the results of the operation.
    
        This manager and the returned QGeoRouteReply object will emit signals
        indicating if the operation completes or if errors occur.
    
        If supportsRouteUpdates() returns false an
        QGeoRouteReply::UnsupportedOptionError will occur.
    
        Once the operation has completed, QGeoRouteReply::routes can be used to
        retrieve the updated route.
    
        The returned route could be entirely different to the original route,
        especially if \a position is far away from the initial route.
        Otherwise the route will be similar, although the remaining time and
        distance will be updated and any segments of the original route which
        have been traversed will be removed.
    
        The user is responsible for deleting the returned reply object, although
        this can be done in the slot connected to QGeoRoutingManager::finished(),
        QGeoRoutingManager::error(), QGeoRouteReply::finished() or
        QGeoRouteReply::error() with deleteLater().
        
        @param route: the old route
        @type route: GeoRoute
        @param position: The new position
        @type position: GeoCoordinate
        @rtype: GeoRouteReply
        '''
        return self._engine.updateRoute(route, position)
    
    def supportsRoutesUpdates(self):
        '''
        Returns whether this manager supports updating routes.
        @rtype: bool
        '''
        return self._engine.supportsRoutesUpdates()
    
    def supportsAlternativeRoutes(self):
        '''
        Returns whether this manager supports request for alternative routes.
        @rtype: bool
        '''
        return self._engine.supportsAlternativeRoutes()
    
    def supportsExcludeAreas(self):
        '''
        Returns whether this engine supports the exclusion of areas from routes.
        @rtype: bool
        '''
        return self._engine.supportsExcludeAreas()
    
    def supportedTravelModes(self):
        '''
        Returns the travel modes supported by this manager.
        @rtype: int
        '''
        return self._engine.supportedTravelModes()
    
    def supportedFeatureTypes(self):
        '''
        Returns the types of features that this manager can take into account
        during route planning.
        @rtype: int
        '''
        return self._engine.supportedFeatureTypes()
    
    def featureWeights(self):
        '''
        Returns the weightings which this manager can apply to different features
        during route planning.
        @rtype: dict
        '''
        return self._engine.featureWeights()
    
    def supportedRouteOperations(self):
        '''
        Returns the route optimizations supported by this manager.
        @rtype: int
        '''
        return self._engine.supportedRouteOperations()
    
    def supportedSegmentDetails(self):
        '''
        Returns the levels of detail for routing segments which can be requested
        with this manager.
        @rtype: int
        '''
        return self._engine.supportedSegmentDetails()
    
    def supportedManeuverDetails(self):
        '''
        Returns the levels of detail for navigation maneuvers which can be
        requested by this manager.
        @rtype: int
        '''
        return self._engine.supportedManeuverDetails()
    
    def setLocale(self, locale):
        '''
        Sets the locale to be used by the this manager to \a locale.

        If this routing manager supports returning addresses and instructions
        in different languages, they will be returned in the language of \a locale.
    
        The locale used defaults to the system locale if this is not set.
        
        @param locale: The new locale
        @type locale: QLocale
        '''
        self._engine.setLocale(locale)
    
    def locale(self):
        '''
        Returns the locale used to hint to this routing manager about what
        language to use for addresses and instructions.
        @rtype: QLocale
        '''
        return self._engine.locale()
    
    