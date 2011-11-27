'''
Created on 18.11.2011

@author: michi
'''
from PyQt4.QtNetwork import QNetworkReply

from ems.qt4.location.maps.geosearchreply import GeoSearchReply
from ems.qt4.location.plugins.nokia.georoutexmlparser import GeoRouteXmlParser
from ems.qt4.location.plugins.nokia.geocodexmlparser import GeoCodeXmlParser

class GeoSearchReplyNokia(GeoSearchReply):
    
    _m_reply = QNetworkReply
    
    def __init__(self, reply, limit, offset, viewport, parent=None):
        GeoSearchReply.__init__(self, parent=parent)
        self._m_reply = reply
        
        self._m_reply.finished.connect(self._networkFinished)
        self._m_reply.error.connect(self._networkError)
        
        self._setLimit(limit)
        self._setOffset(offset)
        self._setViewport(viewport)
        
    
    def abort(self):
        if not self._m_reply:
            return
        self._m_reply.abort()
        
        self._m_reply.deleteLater()
        self._m_reply = None
    
    def _networkFinished(self):
        if not self._m_reply:
            return
        
        if self._m_reply.error() != QNetworkReply.NoError:
            return
        
        #parser = GeoRouteXmlParser()
        parser = GeoCodeXmlParser()
        if parser.parse(self._m_reply):
            places = parser.results()
            bounds = self.viewport();
            if bounds:
                for i in range(len(places)):
                    if not bounds.contains(places[i].coordinate()):
                        places.remove(i)

            self._setPlaces(places)
            self._setFinished(True);
        else:
            self._setError(GeoSearchReply.ParseError, parser.errorString())
        
    
        self._m_reply.deleteLater()
        self._m_reply = 0
    
    def _networkError(self, error):
        if not self._m_reply:
            return
        self._setError(GeoSearchReply.CommunicationError,
                       self._m_reply.errorString())
        
        self._m_reply.deleteLater()
        self._m_reply = 0