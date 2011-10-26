'''
Created on 20.10.2011

@author: michi
'''
from PyQt4.QtCore import QObject, pyqtSignal
from geomapobject import GeoMapObject #@UnresolvedImport
from ems.qt4.location.geoboundingbox import GeoBoundingBox #@UnresolvedImport

class GeoMapGroupObject(GeoMapObject):
    '''
    The QGeoMapGroupObject class is a QGeoMapObject used to
    manager a group of other map objects.

    The QGeoMapGroupObject class can be used to quickly add and remove
    groups of objects to a map.

    The map objects contained in the group will be ordered relative to
    one another in the usual manner, such that objects with higher z-values
    will be drawn over objects with lower z-values and objects with
    equal z-values will be drawn in insertion order.

    This ordering of the objects will be independent of the other
    objects that are added to the map, since the z-value and insertion
    order of the QGeoMapGroupObject is used to determine where the
    group is placed in the scene.
    '''
    
    childAdded = pyqtSignal(GeoMapObject)
    '''This signal will be emitted when the map object \a childObject
    is added to the group.'''
    
    childRemoved = pyqtSignal(GeoMapObject)
    '''This signal will be emitted when the map object \a childObject
    is removed from the group.'''
    
    childUpdated = pyqtSignal(GeoMapObject)
    '''This signal will be emitted when the map object \a childObject
    belonging to the group is updated.'''
    
    _children = []
    
    def __init__(self):
        '''
        Constructs a new group object.
        '''
        QObject.__init__(self, None)
        self._children = []
    
    def type_(self):
        '''
        reimplemented
        '''
        return GeoMapObject.GroupType
    
    def boundingBox(self):
        '''
        Returns a bounding box which contains this map object.

        If this map object has children, the bounding box will be large
        enough to contain both this map object and all of its children.
        
        @return: GeoBoundingBox
        '''
        bounds = GeoBoundingBox()
        if len(self._children) == 0:
            return bounds
        
        bounds <<= self._children[0].boundingBox()
        
        for i in range(len(self._children)):
            bounds <<= bounds.united(self._children[i].boundingBox())
        
        return bounds
    
    def contains(self, coordinate):
        '''
        Returns whether coordinate is contained with the boundary of this
        map object.
    
        If this map object has children, this function will return whether
        coordinate is contained within the boundary of this map object or
        within the boundary of any of its children.
        
        @param coordinate: The coord
        @type coordinate: GeoCoordinate
        @return: bool
        '''
        for child in self._children:
            if child.contains(coordinate):
                return True
            
        return False
    
    def mapObjectLessThan(self, op1, op2):
        '''
        Returns if left is less than right
        
        @param op1: Left Operand
        @type op1: GeoMapObject
        @param op2: Right Operand
        @type op2: GeoMapObject
        '''
        return op1 < op2
    
    def addChildObject(self, childObject):
        '''
        Adds childObject to the list of children of this map object.

        The children objects are drawn in order of the QGeoMapObject::zValue()
        value.  Children objects having the same z value will be drawn
        in the order they were added.
    
        The map object will take ownership of childObject.
        
        @param childObject: The GeoMapObject
        @type childObject: GeoMapObject
        '''
        if not childObject or (childObject in self._children):
            return
        
        childObject.setMapData(self.mapData())
        childObject.serial = (self.serial + 1)
        self._children.append(childObject)
        
        childObject.zValueChanged.connect(self._childChangedZValue)
        self.childAdded.emit(childObject)
    
    def removeChildObject(self, childObject):
        '''
        Removes childObject from the list of children of this map object.

        The map object will release ownership of childObject.
        
        @param childObject: The childobject
        @type childObject: GeoMapObject
        '''
        if not childObject:
            return
        
        try:
            self._children.remove(childObject)
            childObject.zValueChanged.disconnect(self._childChangedZValue)
            self.childRemoved.emit(childObject)
            childObject.setMapData(None)
        except ValueError:
            pass
            
    
    def childObjects(self):
        '''
        Returns the children of this object.
        
        @return: QList
        '''
        return self._children
    
    def clearChildObjects(self):
        '''
        Clears the children of this object.

        The child objects will be deleted.
        '''
        for child in self._children:
            self.removeChildObject(child)
            del child
        self._children = []
    
    def setVisible(self, visible):
        '''
        Sets whether this group of objects is visible to visible.
        
        @param visible: Visibility
        @type visible: bool
        '''
        for child in self._children:
            child.setVisible()
        
        super(GeoMapGroupObject, self).setVisible(visible)
    
    def setMapData(self, mapData):
        '''
        remplemented
        
        @param mapData: The mapdata
        @type mapData: GeoMapData
        '''
        for child in self._children:
            child.setMapData(mapData)
            if mapData:
                self.childAdded.emit(child)
        super(GeoMapGroupObject, self).setMapData(mapData)
    
    def _childChangedZValue(self, zValue):
        '''
        Receives child zValue updates
        
        @param zValue: The new zValue
        @type zValue: int
        '''
        child = self.sender()
        
        if not child:
            return
        
        try:
            self._children.remove(child)
            self._children.append(child)
            self.childUpdated.emit(child)
        except ValueError:
            pass
            