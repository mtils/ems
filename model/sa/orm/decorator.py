'''
Created on 20.06.2011

@author: michi
'''

from sqlalchemy.orm import object_mapper
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.hybrid import hybrid_property

def friendly_name(classProperty):
    if isinstance(classProperty, InstrumentedAttribute):
        if hasattr(classProperty.class_,'__ormDecorator__'):
            deco = classProperty.class_.__ormDecorator__()
            return deco.getPropertyFriendlyName(classProperty.key)
    elif hasattr(classProperty, '__ormDecorator__'):
        return classProperty.__ormDecorator__().\
            getReprasentiveString(classProperty)

class OrmDecorator(object):
    def __init__(self, cls):
        self._class = cls
        self._shownProperties = []
        self._objectMapper = None
        self._valueFormatOptions = {}
        self._rProperties = {}
        self._colInfos = {}
    
    def getObjectMapper(self):
        if self._objectMapper is None:
            self._objectMapper = object_mapper(self._class())
        return self._objectMapper
        
    objectMapper = property(getObjectMapper)
    
    def getReprasentiveString(self, obj, view='default'):
        if hasattr(self._class,'__reprasentive_column__'):
            return obj.__getattribute__(self._class.__reprasentive_column__)
        return repr(obj)
    
    def getFriendlyName(self, obj=None, view='default'):
        if hasattr(self._class, "__friendlyName__"):
            return self._class.__friendlyName__
        return self._class.__name__
    
    def getPropertyFriendlyName(self, propertyName):
        if hasattr(self._class, "__propertyFriendlyNames__"):
            notDottedProperty = str(propertyName).split('.')[-1:][0]
            if self._class.__propertyFriendlyNames__.has_key(notDottedProperty):
                return self._class.__propertyFriendlyNames__[notDottedProperty]

        return propertyName
    
    def getShownProperties(self):
        if not len(self._shownProperties):
            if hasattr(self._class,'__shownProperties__'):
                self._shownProperties = self._class.__shownProperties__
            else:
                for prop in self.objectMapper.iterate_properties:
                    self._shownProperties.append(prop.key)
        
        return self._shownProperties
    
    def getDefaultOrderByProperty(self, obj):
        if hasattr(self._class,'__reprasentive_column__'):
            return self._class.__reprasentive_column__
    
    def getDefaultAllQuery(self, session):
        return session.query(self._class).order_by(self.getDefaultOrderByProperty(None))
    
    def getAll(self, session):
        return self.getDefaultAllQuery(session).all()
    
    def getFullTextQuery(self, session, text):
        return None
    
    def valueToFormattedString(self, propertyName, value):
        if hasattr(value, '__ormDecorator__'):
            dec = value.__ormDecorator__()
            return dec.getReprasentiveString(value)
        formatOption = self.getValueFormatOption(propertyName)
        newString = "%s%s%s" % (unicode(formatOption['prefix']),
                                unicode(formatOption['textFormat']).format((value)),
                                unicode(formatOption['suffix'])
                                )
        return newString
    
    def getValueFormatOption(self, propertyName):
        prefix = u''
        suffix = u''
        textFormat = u'{0}'
        
        try:
            colInfo = self.getColInfo(propertyName)
            if colInfo.has_key('unit'):
                suffix = " " + unicode(colInfo['unit'])
        except AttributeError:
            pass
        
        
        return {
                'prefix':prefix,
                'suffix':suffix,
                'textFormat':textFormat
                }
    
    def getColInfo(self, propertyName):
        if not self._colInfos.has_key(propertyName):
            cols = self.getRProperty(propertyName).columns
            if len(cols) == 1:
                col = cols[0]
            self._colInfos[propertyName] = col.info
        return self._colInfos[propertyName]
    
    def getRProperty(self, propertyName):
        if not self._rProperties.has_key(propertyName):
            try:
                self._rProperties[propertyName] = self.objectMapper.\
                    get_property(propertyName)
            except InvalidRequestError:
                clsProp = self._class.__getattribute__(self._class, propertyName)
                if isinstance(clsProp, hybrid_property):
                    functionName = clsProp.fget.__name__
                    self._rProperties[propertyName] = clsProp

        return self._rProperties[propertyName]
        