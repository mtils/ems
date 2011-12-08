'''
Created on 20.10.2011

@author: michi
'''

class LocationUtils(object):
    @staticmethod
    def isValidLat(lat, projection=None):
        if projection is None:
            projection = "wgs84"
        if projection == "wgs84":
            return lat >= -90 and lat <= 90
        elif projection == "utm":
            #Only germany at the moment 
            return lat >= 280000 and lat <= 1150000
    
    @staticmethod
    def isValidLong(lng, projection=None):
        if projection is None:
            projection = "wgs84"
        if projection == "wgs84":
            return lng >= -180 and lng <= 180
        elif projection == "utm":
            #Only germany at the moment 
            return lng >= 5236000 and lng <= 6106000