'''
Created on 04.03.2012

@author: michi
'''

from abc import ABCMeta, abstractmethod, abstractproperty

class XType:
    
    __metaclass__ = ABCMeta
    
    CUSTOM = 1
    NUMBER = 2
    STRING = 3
    
    
    def __init__(self, canBeNone=None):
        if canBeNone is None:
            canBeNone = True
        self.canBeNone = True
    
    @abstractproperty
    def group(self):
        pass
    
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
    
    @property
    def group(self):
        return XType.STRING
    
    def value2String(self, value):
        return value

class UnitType(NumberType):
    
    PREPEND = 1
    APPEND = 2
    VALUE_2_UNIT_SPACE = ' '
    
    def __init__(self, unit=None, pyTypeOfNumber=float):
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
        
