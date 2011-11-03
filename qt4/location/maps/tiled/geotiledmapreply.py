'''
Created on 03.11.2011

@author: michi
'''
from PyQt4.QtCore import QObject

class GeoTiledMapReply(QObject):
    "Error Enum"
    NoError = 0
    CommunicationError = 1
    ParseError = 2
    UnknownError = 3