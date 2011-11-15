'''
Created on 05.11.2011

@author: michi
'''
from ems.qt4.location.geocoordinate import GeoCoordinate

class GeoManeuver(object):
    '''
    \brief The QGeoManeuver class represents the information relevant to the
    point at which two QGeoRouteSegments meet.

    \inmodule QtLocation
    \since 1.1

    \ingroup maps-routing

    QGeoRouteSegment instances can be thought of as edges on a routing
    graph, with QGeoManeuver instances as optional labels attached to the
    vertices of the graph.

    The most interesting information help in a QGeoManeuver instance is
    normally the textual navigation to provide and the position at which to
    provide it, accessible by instructionText() and position() respectively.

    It is also possible to determine if a routing waypoint has been passed by
    checking if waypoint() returns a valid QGeoCoordinate.
    '''
    
    
    '''InstructionDirection Enum
       Describes the change in direction associated with the instruction text
       that is associated with a QGeoManaeuver.
    '''
    
    NoDirection = 0
    'There is no direction associated with the instruction text.'
    
    DirectionForward = 1
    'The instruction indicates that the direction of travel does not need to change.'
    
    DirectionBearRight = 2
    'The instruction indicates that the direction of travel should bear to the right.'
    
    DirectionLightRight = 3
    'The instruction indicates that a light turn to the right is required.'
    
    DirectionRight = 4
    'The instruction indicates that a turn to the right is required.'
    
    DirectionHardRight = 5
    'The instruction indicates that a hard turn to the right is required.'
    
    DirectionUTurnRight = 6
    'The instruction indicates that a u-turn to the right is required.'
    
    DirectionUTurnLeft = 7
    'The instruction indicates that a u-turn to the left is required.'
    
    DirectionHardLeft = 8
    'The instruction indicates that a hard turn to the left is required.'
    
    DirectionLeft = 9
    'The instruction indicates that a turn to the left is required.'
    
    DirectionLightLeft = 10
    'The instruction indicates that a light turn to the left is required.'
    
    DirectionBearLeft = 11
    'The instruction indicates that the direction of travel should bear to the left.'
    
    _valid = False
    _id = ""
    _position = GeoCoordinate()
    _text = ""
    _direction = 0
    _timeToNextInstruction = 0
    _distanceToNextInstruction = 0
    _waypoint = GeoCoordinate()
    
    def __init__(self, other=None):
        '''
        Constructs a invalid maneuver object.

        The maneuver will remain invalid until one of
        setPosition(), setInstructionText(), setDirection(),
        setTimeToNextInstruction(), setDistanceToNextInstruction() or
        setWaypoint() is called.
        '''
        if isinstance(other, GeoManeuver):
            self.__ilshift__(other)
    
    def __ilshift__(self, other):
        '''
        self <<= other
        Replacement for C++ = operator overloading
         
        @param other: Right operand
        @type other: GeoManeuver
        @rtype: GeoManeuver
        '''
        for prop in ('_valid','_position','_text','_direction',
                     '_timeToNextInstruction','_distanceToNextInstruction',
                     '_waypoint'):
            self.__setattr__(prop, other.__getattribute__(prop))
        return self
    
    def __eq__(self, other):
        '''
        self == other
        
        @param other: Right operand
        @type other: GeoManeuver
        @rtype: bool
        '''
        for prop in ('_valid','_position','_text','_direction',
                     '_timeToNextInstruction','_distanceToNextInstruction',
                     '_waypoint'):
            if self.__getattribute__(prop) != other.__getattribute__(prop):
                return False
        return True
    
    def __ne__(self, other):
        '''
        self != other
        
        @param other: Right operand
        @type other: GeoManeuver
        @rtype: bool
        '''
        return not self.__eq__(other)
    
    def isValid(self):
        '''
        Returns whether this maneuver is valid or not.

        Invalid maneuvers are used when there is no information
        that needs to be attached to the endpoint of a QGeoRouteSegment instance.
        @rtype: bool
        '''
        return self._valid
    
    def setPosition(self, position):
        '''
        Sets the position where instructionText() should be displayed to \a
        position.
        
        @param position: The position
        @type position: GeoCoordinate
        '''
        self._valid = True
        self._position = position
    
    def position(self):
        '''
        Returns the position where instructionText() should be displayed.
        @rtype: GeoCoordinate
        '''
        return self._position
    
    def setInstructionText(self, instructionText):
        '''
        Sets the textual navigation instructions to \a instructionText.
        
        @param instructionText: The text
        @type instructionText: basestring
        '''
        self._valid = True
        self._text = instructionText
    
    def instructionText(self):
        '''
        Returns the textual navigation instructions.
        @rtype: basestring
        '''
        return self._text
    
    def setDirection(self, direction):
        '''
        Sets the direction associated with the associated instruction to \a
        direction.
        
        @param direction: The direction
        @type direction: int
        '''
        self._valid = True
        self._direction = direction
    
    def direction(self):
        '''
         Returns the direction associated with the associated instruction.
         @rtype: int
        '''
        return self._direction
    
    def setTimeToNextInstruction(self, secs):
        '''
        Sets the estimated time it will take to travel from the point at which the
        associated instruction was issued and the point that the next instruction
        should be issued, in seconds, to \a secs.
        
        @param secs: Seconds until next instruction
        @type secs: int
        '''
        self._valid = True
        self._timeToNextInstruction = secs
    
    def timeToNextInstruction(self):
        '''
        Returns the estimated time it will take to travel from the point at which
        the associated instruction was issued and the point that the next
        instruction should be issued, in seconds.
        @rtype: int
        '''
        return self._timeToNextInstruction
    
    def setDistanceToNextInstruction(self, distance):
        '''
        Sets the distance, in metres, between the point at which the associated
        instruction was issued and the point that the next instruction should be
        issued to \a distance.
        
        @param distance: The distance
        @type distance: int
        '''
        self._valid = True
        self._distanceToNextInstruction = distance
    
    def distanceToNextInstruction(self):
        '''
        Returns the distance, in metres, between the point at which the associated
        instruction was issued and the point that the next instruction should be
        issued.
        @rtype: int
        '''
        return self._distanceToNextInstruction
    
    def setWaypoint(self, coordinate):
        '''
        Sets the waypoint associated with this maneuver to \a coordinate.
        
        @param coordinate: The next waypoint
        @type coordinate: GeoCoordinate
        '''
        self._valid = True
        self._waypoint = coordinate
    
    def waypoint(self):
        '''
        Returns the waypoint associated with this maneuver.

        If there is not waypoint associated with this maneuver an invalid
        QGeoCoordinate will be returned.
        @rtype: GeoCoordinate
        '''
        return self._waypoint
    