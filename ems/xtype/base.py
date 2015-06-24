'''
Created on 04.03.2012

@author: michi
'''
from datetime import date
from abc import ABCMeta, abstractmethod, abstractproperty
import datetime

class XType:
    
    __metaclass__ = ABCMeta
    
    CUSTOM = 1
    NUMBER = 2
    STRING = 3
    BOOL = 4
    COMPLEX = 5
    TEMPORAL = 6
    MIXED = 7
    
    
    def __init__(self, canBeNone=None, defaultValue=None):
        if canBeNone is None:
            canBeNone = True
        self.canBeNone = canBeNone
        self.defaultValue = defaultValue
        self.canBeEdited = True
        self.forceInteraction = False
    
    @abstractproperty
    def group(self):
        pass
    
    def value2String(self, value):
        return unicode(value)
    

class BoolType(XType):

    def __init__(self, boolNames=None):
        XType.__init__(self)
        self.defaultValue = False

    @property
    def group(self):
        return XType.BOOL

    @staticmethod
    def castToBool(value):
        if isinstance(value, (float, int)):
            return bool(value)
        if isinstance(value, basestring):
            if value.lower() in ('true','yes'):
                return True
            if value.lower() in ('false','no'):
                return False
            try:
                numeric = float(value)
                return bool(numeric)
            except ValueError:
                pass
        if value:
            return True
        return False
    
class NumberType(XType):
    
    def __init__(self, pyTypeOfNumber):
        XType.__init__(self)
        self.pyType = pyTypeOfNumber
        self.strNumberFormat = ''
        self.strPrefix = ''
        self.strSuffix = ''
        self.minValue = -100000
        self.maxValue = 100000
        self.decimalsSeparator = '.'
        self.thousandsSeparator = None
        self.decimalsCount = None
        if self.pyType is float:
            self.defaultValue = 0.0
        if self.pyType is int:
            self.defaultValue = 0
        
    
    def value2String(self, value):
        if self.strNumberFormat:
            number = ('{0:' + self.strNumberFormat + '}').format(value)
        else:
            number = NumberType.formatNumber(value,
                                             self.decimalsCount,
                                             self.decimalsSeparator,
                                             self.thousandsSeparator)
            
        return  (self.strPrefix + number + self.strSuffix)
    
    @property
    def group(self):
        return XType.NUMBER
    
    @staticmethod
    def intWithThousandsSeparator(x, sep=None):
        if sep is None:
            sep = ','
        if type(x) not in [type(0), type(0L)]:
            raise TypeError("Parameter must be an integer.")
        if x < 0:
            return '-' + NumberType.intWithThousandsSeparator(-x, sep)
        result = ''
        while x >= 1000:
            x, r = divmod(x, 1000)
            result = "%s%03d%s" % (sep, r, result)
        return "%d%s" % (x, result)

    def viewToModel(self, viewValue):
        return viewValue

    def modelToView(self, modelValue):
        return modelValue

    @staticmethod
    def formatNumber(x, decimalsCount=None, decimalsSeparator=None,
                     thousandsSeparator=None, zeroFill=None, decimalsZeroFill=None):
        
        if not isinstance(x, (float, int)):
            raise TypeError("formatNumber needs float|int")
        
        if zeroFill is not None or decimalsZeroFill is not None:
            raise NotImplementedError("Zerofill and decimalsZeroFill currently not supported")
        
        preDecimals = '0'
        decimals = ''
        
        if decimalsCount is None:
            strVersion = str(x)
        else:
            strVersion = ("{0:." + str(decimalsCount) + "f}").format(x)
        
        
        if "." in strVersion:
            preDecimals, decimals = strVersion.split('.')
        else:
            preDecimals = strVersion
        
        if decimalsCount is None:
            decimalsCount = 0
        
        if decimalsSeparator is None:
            decimalsSeparator = '.'
            
        if thousandsSeparator:
            preDecimals = NumberType.intWithThousandsSeparator(int(preDecimals),
                                                                   thousandsSeparator)
        
        if not decimals:
            return preDecimals
        else:
            return "{0}{1}{2}".format(preDecimals,decimalsSeparator,decimals)
        

class StringType(XType):
    def __init__(self):
        XType.__init__(self)
        self.minLength = 0
        self.maxLength = 10000000
        self.defaultValue = unicode()
        self.hints = []
    
    @property
    def group(self):
        return XType.STRING
    
    def value2String(self, value):
        return value

class FilesystemPathType(StringType):
    def __init__(self):
        super(FilesystemPathType, self).__init__()
        self.mustExist = False

class FilePathType(FilesystemPathType):
    pass

class DirectoryPathType(FilesystemPathType):
    pass

class UnitType(NumberType):
    
    PREPEND = 1
    APPEND = 2
    VALUE_2_UNIT_SPACE = ' '
    
    def __init__(self, unit=None, pyTypeOfNumber=None):
        if pyTypeOfNumber is None:
            pyTypeOfNumber = float
        super(UnitType, self).__init__(pyTypeOfNumber)
        self._unit = unit
        self._unitStrPosition = UnitType.APPEND
        self._value2UnitSpace = 0
        
        if unit is not None:
            self.unit = unit
        
    @property
    def unit(self):
        return self._unit
    
    @unit.setter
    def unit(self, unit):
        self._unit = unit
        if self._unitStrPosition == UnitType.APPEND:
            self.strPrefix = ''
            self.strSuffix = self.getUnitString(unit, self._value2UnitSpace,
                                                self._unitStrPosition)
        elif self._unitStrPosition == UnitType.PREPEND:
            self.strSuffix = ''
            self.strPrefix = self.getUnitString(unit, self.value2UnitSpace,
                                                self._unitStrPosition)
    
    @staticmethod
    def getUnitString(unit,value2UnitSpace, position):
        if value2UnitSpace == 0:
            return unit
        if position == UnitType.APPEND:
            parts = []
            for i in range(value2UnitSpace):
                parts.append(' ')
            parts.append(unit)
        else:
            parts = []
            parts.append(unit)
            for i in range(value2UnitSpace):
                parts.append(' ')
        return unicode("").join(parts)
    
    @property
    def unitStrPosition(self):
        return self._unitStrPosition
    
    @unitStrPosition.setter
    def unitStrPosition(self, position):
        self._unitStrPosition = position
        self.unit = self.unit
    
    @property
    def value2UnitSpace(self):
        return self._value2UnitSpace
    
    @value2UnitSpace.setter
    def value2UnitSpace(self, space):
        self._value2UnitSpace = space
        self.unit = self.unit

class DateType(XType):
    def __init__(self):
        XType.__init__(self)
        self.minDate = None
        self.maxDate = None
        self.defaultValue = date.today()
    
    @property
    def group(self):
        return XType.TEMPORAL
    
    def value2String(self, value):
        return unicode(value)


class ComplexType(XType):
    def __init__(self, canBeNone=None, defaultValue=None):
        XType.__init__(self, canBeNone=canBeNone, defaultValue=defaultValue)
    
    @property
    def group(self):
        return XType.COMPLEX

class OneOfAListType(XType):
    def __init__(self, canBeNone=None, defaultValue=None):
        XType.__init__(self, canBeNone=canBeNone, defaultValue=defaultValue)
        self.possibleValues = ()
        self.xTypeOfItems = None

    @property
    def group(self):
        return XType.MIXED

    @property
    def itemType(self):
        if self.xTypeOfItems:
            return self.xTypeOfItems
        return native2XType(self.possibleValues[0])


class NamedFieldType(ComplexType):
    def __init__(self, canBeNone=None, defaultValue=None):
        ComplexType.__init__(self, canBeNone=canBeNone,
                               defaultValue=defaultValue)
        self.defaultValue = {}
        self.__xTypeMap = {}
        self.__keys = []

    def addKey(self, name, xType):
        self.__keys.append(name)
        self.__xTypeMap[self.__keys.index(name)] = xType

    def keyType(self, key):
        if isinstance(key, basestring):
            return self.__xTypeMap[self.__keys.index(key)]
        elif isinstance(key, int):
            return self.__xTypeMap[key]

    def keys(self):
        return self.__keys

    def keyName(self, index):
        return self.__keys[index]

    @property
    def xTypeMap(self):
        return self.__xTypeMap

    def __getitem__(self, key):
        return self.__xTypeMap[self.__keys.index(key)]

    def __setitem__(self, name, xType):
        self.__keys.append(name)
        self.__xTypeMap[self.__keys.index(name)] = xType

    def __contains__(self, item):
        if isinstance(item, XType):
            return item in self.__xTypeMap
        return item in self.__keys

    def __len__(self):
        return len(self.__keys)

    def __iter__(self):
        return self.__keys.__iter__()

    @classmethod
    def create(cls, keys=None, **kwargs):

        keys = kwargs if keys is None else keys

        xtype = cls.__new__(cls)
        xtype.__init__()

        for key in keys:
            xtype.addKey(key, keys[key])
        return xtype

class SequenceType(ComplexType):
    def __init__(self, itemType, canBeNone=None, defaultValue=None):
        ComplexType.__init__(self, canBeNone=canBeNone,
                               defaultValue=defaultValue)
        self.defaultValue = []
        self.maxLength = None
        self.minLength = None
        self.defaultLength = 0
        self.defaultItem = None
        self.itemType = itemType

class DictType(NamedFieldType):
    pass

class ObjectInstanceType(NamedFieldType):
    def __init__(self, cls,  canBeNone=None, defaultValue=None):
        NamedFieldType.__init__(self, canBeNone=canBeNone,
                               defaultValue=None)
        self.cls = cls
        
def native2XType(type_):
    if type_ in (int, float):
        return NumberType(type_)
    if type_ is bool:
        return BoolType()
    if type_ in (str, unicode):
        return StringType()
    if type_ in (dict, list, tuple, set):
        return ComplexType()
    if type_ in (datetime.datetime, datetime.date):
        return DateType()