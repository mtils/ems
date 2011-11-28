'''
Created on 17.11.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtNetwork import QNetworkReply

from ems.qt4.location.maps.georoutereply import GeoRouteReply #@UnresolvedImport
from ems.qt4.location.plugins.nokia.georoutexmlparser import GeoRouteXmlParser #@UnresolvedImport

class GeoRouteReplyNokia(GeoRouteReply):
    
    _m_reply = QNetworkReply
    
    def __init__(self, request, reply, parent=None):
        '''
        @param request: QGeoRouteRequest
        @type request: QGeoRouteRequest
        @param reply: QNetworkReply
        @type reply: QNetworkReply
        @param parent: Parent QObject
        @type parent: QObject
        '''
        self._m_reply = reply
        GeoRouteReply.__init__(self, request, parent=parent)
        self._m_reply.finished.connect(self._networkFinished)
        self._m_reply.error.connect(self._networkError)
    
    def abort(self):
        if not self._m_reply:
            return
        self._m_reply.abort()
        
        self._m_reply.deleteLater()
        self._m_reply = None
    
    @pyqtSlot()
    def _networkFinished(self):
        if not self._m_reply:
            return
        
        if self._m_reply.error() != QNetworkReply.NoError:
            #Removed because this is already done in networkError, which previously caused _two_ errors to be raised for every error.
            #setError(QGeoRouteReply::CommunicationError, m_reply->errorString());
            #m_reply->deleteLater();
            #m_reply = 0;
            return
        parser = GeoRouteXmlParser(self.request())
        if parser.parse(self._m_reply):
            self._setRoutes(parser.results())
            self._setFinished(True)
        else:
            self._setError(GeoRouteReply.ParseError,
                           "The response from the service was not in a recognisable format.")
        
        self._m_reply.deleteLater()
        self._m_reply = None
    
    def _networkError(self, error):
        if not self._m_reply:
            return
        
        self._setError(GeoRouteReply.CommunicationError,
                       self._m_reply.errorString())
        
        self._m_reply.deleteLater()
        self._m_reply = None