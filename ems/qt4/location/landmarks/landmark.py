'''
Created on 26.10.2011

@author: michi
'''
from PyQt4.QtCore import QUrl, qFuzzyCompare

from ems.qt4.location.geoplace import GeoPlace #@UnresolvedImport
from landmarkid import LandmarkId #@UnresolvedImport
from ems.qt4.location.geocoordinate import GeoCoordinate #@UnresolvedImport
from ems.qt4.location.geoboundingbox import GeoBoundingBox #@UnresolvedImport

class Landmark(GeoPlace):
    '''
    \brief The QLandmark class represents a point of interest.


    Each QLandmark represents a location with a number of attributes  or properties
    such as name, description, phone number etc. Each QLandmark may also be associated with zero or more categories.
    A category  defines a type of landmark such as restaurant or
    cinema.  To set the category that a landmark belongs to, use
    the setCategoryIds() or addCategoryId() functions.  A landmark may
    be removed from a category by using the removeCategoryId() function.

    Some landmarks may be designated as read-only, e.g. a publically accessible
    landmark server may not want some of its content to be editable.
    Note, localization is only possible for landmarks that are read-only.

    Each QLandmark is an in memory representation of a landmark;
    it does not reflect the actual landmark state in persistent
    storage until the appropriate synchronization method is called
    on the QLandmarkManager(e.g. \l {QLandmarkManager::saveLandmark()} {saveLandmark()},
    \l {QLandmarkManager::removeLandmark()} {removeLandmark()}).

    Note that QLandmark inherits from QGeoPlace and thus has a viewport data field.
    Most managers usually however ignore this field when saving the landmark.
    
    '''
    
    
    'Pseudo Private Things'
    _type = GeoPlace.LandmarkType
    
    _name = ""
    
    _categoryIds = []
    _description = ""
    _iconUrl = QUrl()
    _radius = 0.0
    _phoneNumber = ""
    _url = QUrl()
    _id = LandmarkId()
    
    def __init__(self, otherLandmark=None):
        '''
        Constructs a new landmark from \a other.

        If \a other is not a landmark, the coordinates, address and viewport
        get copied into the newly created landmark.
    
        If \a other is a landmark, this function is equivalent to calling
        QLandmark(const QLandmark &other).
    
        This constructor allows (1) and c to take place.
        /code
        QGeoPlace geoPlace = lm1; //lm1 is a QLandmark
        ...
        QLandmark lm2 = geoPlace; //(1)lm2 is equivalent to lm1
    
        QGeoPlace ordinaryPlace;
        QLandmark lm3 = ordinarPlace; //(2)lm3 has the details of ordinaryPlace's coordinate, address and viewport.
        /endcode
        
        @param otherLandmark: Another landmark which will then be copied (optional)
        @type otherLandmark: Landmark
        '''
        if isinstance(otherLandmark, Landmark):
            self.__ilshift__(otherLandmark)
            
    
    def __ilshift__(self, other):
        '''
        self <<= other
        
        In C++ this is the = operator, I solved this is python with an
        <<= operator
        
        @param other: Right operand
        @type other: Landmark
        @return Landmark
        '''
        self._name = other.name()
        self._categoryIds = other.categoryIds()
        self._description = other.description()
        self._iconUrl = other.iconUrl()
        self._radius = other.radius()
        self._phoneNumber = other.phoneNumber()
        self._url = other.url()
        self._id = other.landmarkId()
        return self
    
    def __eq__(self, other):
        '''
        self == other
        
        @param other: Right operand
        @type other: Landmark
        @rtype: bool
        '''
        radiusIsMatch = False
        if not self._radius and not other.radius():
            radiusIsMatch = True
        elif qFuzzyCompare(1 + self._radius, 1 + other.radius()):
            radiusIsMatch = True
        else:
            radiusIsMatch = False
            
        return ((self._name == other.name())
                and (self._description == other.description())
                and (self._iconUrl == other.iconUrl())
                and (radiusIsMatch)
                and (self._phoneNumber == other.phoneNumber())
                and (self._url == other.url())
                and (self._categoryIds == other.categoryIds())
                and (self._id == other.id))
    
    def __ne__(self, other):
        '''
        self != other
        
        @param other: Right operand
        @type other: Landmark
        '''
        return not self.__eq__(other)
    
    def name(self):
        '''
        Returns the name of the landmark.
        
        @rtype: unicode
        '''
        return self._name
    
    def setName(self, name):
        '''
        Sets the \a name of the landmark.

        Using the default manager on the Symbian platform, the name is restricted to a length of 256 characters.
        
        @param name: The name
        @type name: basestring
        '''
        self._name = name
        
    def categoryIds(self):
        '''
        Returns a of list identifiers of categories that this landmark
        belongs to.
        
        @rtype: list
        '''
        return self._categoryIds
    
    def setCategoryIds(self, categoryIds):
        '''
        Sets the categories that this landmark belongs to via
        a list of \a categoryIds.
        
        @param categoryIds: The categoryIds
        @type categoryIds: list
        '''
        self._categoryIds = categoryIds
    
    def addCategoryId(self, categoryId):
        '''
        Adds another category that this landmark will be associated
        with via its \a categoryId.
        
        @param categoryId: The new CategoryId
        @type categoryId: LandmarkCategoryId
        '''
        if not categoryId in self._categoryIds:
            self._categoryIds.append(categoryId)
    
    def removeCategoryId(self, categoryId):
        '''
        Removes a category from a landmark, by using its \a categoryId.

        \sa addCategoryId(), categoryIds()
        
        @param categoryId: the categoryId
        @type categoryId: LandmarkCategoryId
        '''
        self._categoryIds.remove(categoryId)
    
    def description(self):
        '''
        Returns a description of the landmark.
        
        @rtype: basestring
        '''
        return self._description
    
    def setDescription(self, description):
        '''
        Sets the \a description of the landmark.

        Using the default manager on the Symbian platform, the description is restricted to a length of 4096 characters.
        
        @param description: The description
        @type description: basestring
        '''
    
    def iconUrl(self):
        '''
        Returns the url of the landmark's icon.
        
        @rtype: QUrl
        '''
        return self._iconUrl
    
    def setIconUrl(self, url):
        '''
        Sets the \a url of the landmark's icon.
        
        @param url: Icon Url
        @type url: QUrl
        '''
        self._iconUrl = url
    
    def radius(self):
        '''
        Returns the coverage radius of the landmark.  The unit of the radius is meters.

        The coverage radius is relevant for large landmarks
        such as cities.  Note that landmark searches over a given area
        do not factor in the coverage radius.
        
        @rtype: float
        '''
        return self._radius
    
    def setRadius(self, radius):
        '''
        Sets the coverage \a radius of the landmark.  The unit of the \a radius
        is meters.
        
        @param radius: The new radius
        @type radius: float
        '''
        if isinstance(radius, float) and radius >= 0.0:
            self._radius = radius
        else:
            self._radius = 0.0
    
    def phoneNumber(self):
        '''
        Returns the phone number of the landmark.
        
        @rtype: basestring
        '''
        return self._phoneNumber
    
    def setPhoneNumber(self, phoneNumber):
        '''
        Sets the \a phoneNumber of the landmark.
        
        @param phoneNumber: The phoneNumber
        @type phoneNumber: basestring
        '''
        self._phoneNumber = phoneNumber
    
    def url(self):
        '''
        Returns the url of the landmark.
        
        @rtype: QUrl
        '''
        return self._url
    
    def setUrl(self, url):
        '''
        Sets the \a url of the landmark.
        
        @param url: The url
        @type url: QUrl
        '''
        self._url = url
    
    def landmarkId(self):
        '''
        Returns the identifier of the landmark.
        
        @rtype: LandmarkId
        '''
        return self._id
    
    def setLandmarkId(self, landmarkId):
        '''
        Sets the \a id of the landmark.

        Note that saving a new landmark using a QLandmarkManager
        will automatically assign the landmark a valid identifier.
        
        @param landmarkId: The landmarkId
        @type landmarkId: LandmarkId
        '''
        self._id = landmarkId
    
    def clear(self):
        self._address.clear()
        self._coordinate = GeoCoordinate()
        self._viewport = GeoBoundingBox()
        self._name = ""
        self._categoryIds = []
        self._description = ""
        self._iconUrl.clear()
        self._radius =0.0
        self._phoneNumber = ""
        self._url.clear()
        self._id = LandmarkId()