'''
Created on 16.11.2011

@author: michi
'''
from PyQt4.QtCore import pyqtSlot, QDateTime
from PyQt4.QtNetwork import QNetworkReply, QNetworkRequest

from ems.qt4.location.maps.tiled.geotiledmapreply import GeoTiledMapReply

class GeoMapReplyNokia(GeoTiledMapReply):
    
    _m_reply = QNetworkReply
    
    def __init__(self, reply, request, parent=None):
        '''
        @param reply: QNetworkReply
        @type reply: QNetworkReply
        @param request: GeoTiledMapRequest
        @type request: GeoTiledMapRequest
        @param parent: Parent QObject
        @type parent: QObject
        '''
        GeoTiledMapReply.__init__(self, request, parent=parent)
        
        self._m_reply = reply
        self._m_reply.setParent(self)
        self._m_reply.finished.connect(self._networkFinished)
        self._m_reply.error.connect(self._networkError)
        self._m_reply.destroyed.connect(self._replyDestroyed)
    
    def networkReply(self):
        '''
        @rtype: QNetworkReply
        '''
        return self._m_reply
    
    def abort(self):
        if not self._m_reply:
            return
        self._m_reply.abort()
    
    @pyqtSlot()
    def _replyDestroyed(self):
        self._m_reply = None
    
    @pyqtSlot()
    def _networkFinished(self):
        if not self._m_reply:
            return
        
        if self._m_reply.error() != QNetworkReply.NoError:
            return
        
        fromCache = self._m_reply.attribute(QNetworkRequest.SourceIsFromCacheAttribute)
        self._setCached(fromCache.toBool())
        
        if not self.isChached():
            cache = self._m_reply.manager().cache()
            if cache:
                metaData = cache.metaData(self._m_reply.url())
                exp = QDateTime.currentDateTime()
                exp = exp.addDays(14)
                metaData.setExpirationDate(exp)
                cache.updateMetaData(metaData)
        
        self._setMapImageData(self._m_reply.readAll())
        self.setMapImageFormat("PNG")
        self._setFinished(True)
        
        self._m_reply.deleteLater()
        self._m_reply = None
    
    def _networkError(self, error):
        if not self._m_reply:
            return
        
        if error != QNetworkReply.OperationCanceledError:
            self._setError(GeoTiledMapReply.CommunicationError,
                           self._m_reply.errorString())
        self._setFinished(True)
        self._m_reply.deleteLater()
        self._m_reply = None