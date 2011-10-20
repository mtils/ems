'''
Created on 20.10.2011

@author: michi
'''

class LocationUtils(object):
    @staticmethod
    def isValidLat(lat):
        return lat >= -90 and lat <= 90
    
    @staticmethod
    def isValidLong(lng):
        return lng >= -180 and lng <= 180