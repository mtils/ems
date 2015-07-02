
from ems.xtype.base import NumberType, StringType, BoolType, UnitType, DictType
from ems.xtype.base import SequenceType


nameType = StringType()
nameType.minLength=1
nameType.maxLength=12

ageType = UnitType('Jahre', int)
ageType.minValue = 0
ageType.maxValue = 140
ageType.value2UnitSpace = 1

weightType = UnitType('kg', float)
weightType.minValue = 1
weightType.maxValue = 300
weightType.value2UnitSpace = 1
weightType.decimalsCount = 1
weightType.thousandsSeparator = '.'
weightType.decimalsSeparator = ','

moneyType = UnitType('$', float)
moneyType.minValue = 100.0
moneyType.maxValue = 15000.0
moneyType.value2UnitSpace = 1
moneyType.decimalsCount = 2
moneyType.thousandsSeparator = '.'
moneyType.decimalsSeparator = ','

marriedType = BoolType()

itemType = DictType()
itemType.addKey('forename', nameType)
itemType.addKey('surname', nameType)
itemType.addKey('age', ageType)
itemType.addKey('weight', weightType)
itemType.addKey('income', moneyType)
itemType.addKey('married', marriedType)
itemType.maxLength = 8
itemType.minLength = 1

listType = SequenceType(itemType)


testData = [{'forename':'Michael','surname':'Tils','age':4,'weight':104.9,'income': 850.0, 'married':False},
            {'forename':'Carol','surname':'Sample','age':31,'weight':68.9,'income':1450.0,'married':False},
            {'forename':'Thorsten','surname':'Real','age':29,'weight':72.9,'income':2850.0,'married':False},
            {'forename':'Christine','surname':'Clinton','age':28,'weight':65.9,'income':450.0,'married':True},
            {'forename':'Sponge','surname':'Bob','age':29,'weight':79.6,'income':3850.0,'married':False}]