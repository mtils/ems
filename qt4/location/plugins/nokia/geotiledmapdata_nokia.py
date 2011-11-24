'''
Created on 16.11.2011

@author: michi
'''
from PyQt4.QtCore import QRect, QUrl
from PyQt4.QtGui import QPixmap
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest

from ems.qt4.location.maps.tiled.geotiledmapdata import GeoTiledMapData

class GeoTiledMapDataNokia(GeoTiledMapData):
    
    _watermark = QPixmap
    
    _lastCopyRight = QPixmap
    
    _lastCopyRightText = ""
    
    _lastViewport = QRect
    
    _lastCopyRightRect = QRect
    
    _m_networkManager = QNetworkAccessManager
    
    _copyrights = {}
    
    _netUrl = "http://maptile.maps.svc.ovi.com/maptiler/v2/copyright/newest"
    
    def __init__(self, engine):
        '''
        @param engine: GeoMappingManagerEngineNokia
        @type engine: GeoMappingManagerEngineNokia
        '''
        GeoTiledMapData.__init__(self, engine)
        self._m_networkManager = QNetworkAccessManager(self)
        self._m_networkManager.finished.connect(self._copyrightReplyFinished)
        
        self._m_networkManager.get(QNetworkRequest(QUrl(self._netUrl)))
        
    
    def _copyrightReplyFinished(self, reply):
        pass
        