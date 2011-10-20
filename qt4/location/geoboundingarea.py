'''
Created on 13.10.2011

@author: michi
'''

class GeoBoundingArea(object):
    '''
    The QGeoBoundingArea class defines a geographic area.

    This class is the base class for classes which specify a geographic
    area.

    For the sake of consistency, subclasses should describe the specific
    details of the associated areas in terms of QGeoCoordinate instances
    and distances in metres.
    '''
    
    'Describes the type of a bounding area.'
    BoxType = 0
    #A box shaped bounding area.
    CircleType = 1
    #A circular bounding area.
    
    def type_(self):
        '''
        Returns the type of this area.
        
        @return: int
        '''
        raise NotImplementedError('Please implement type_')
    
    def isValid(self):
        '''
        Returns whether this bounding area is valid.

        An area is considered to be invalid if some of the data that is required to
        unambiguously describe the area has not been set or has been set to an
        unsuitable value.
        
        @return: bool
        '''
        raise NotImplementedError('Please implement isValid()')
    
    def isEmpty(self):
        '''
        Returns whether this bounding area is empty.

        An empty area is a region which has a geometrical area of 0.
        
        @return: bool
        '''
        raise NotImplementedError('Please implement isEmpty()')
    
    def contains(self, coordinate):
        '''
        Returns whether the coordinate coordinate is contained within this
        area.
        
        @param coordinate: The coordinate to test
        @type coordinate: GeoCoordinate
        @return: bool
        '''
        raise NotImplementedError('Please implement contains(GeoCoordinate coordinate)')
    
