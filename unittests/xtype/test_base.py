#coding=utf-8
'''
Created on 04.03.2012

@author: michi
'''

from ems.xtype.base import UnitType #@UnresolvedImport
from ems.xtype.base import StringType #@UnresolvedImport

meters = UnitType(float)
meters.unit = 'm²'
meters.value2UnitSpace = 1
meters.decimalsCount = 2
meters.thousandsSeparator = '.'
meters.decimalsSeparator = ','
print meters.value2String(3456813354.24457)


euros = UnitType(float)
euros.unit = '€'
euros.value2UnitSpace = 1
euros.decimalsCount = 2
euros.unitStrPosition = UnitType.PREPEND
euros.thousandsSeparator = '.'
euros.decimalsSeparator = ','

print euros.value2String(14456845.78)

message = StringType()
print message.value2String("Hallo wie sinnlos")