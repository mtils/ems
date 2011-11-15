'''
Created on 15.11.2011

@author: michi
'''
class GeoRouteRequest(object):
    
    'TravelMode Enum'
    
    CarTravel = 0x0001
    PedestrianTravel = 0x0002
    BicycleTravel = 0x0004
    PublicTransitTravel = 0x0008
    TruckTravel = 0x0010