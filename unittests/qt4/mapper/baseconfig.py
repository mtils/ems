'''
Created on 25.04.2012

@author: michi
'''
from PyQt4.QtCore import QString

from ems.qt4.gui.mapper.base import MapperDefaults #@UnresolvedImport
from ems.qt4.gui.mapper.strategies.string_strategy import StringStrategy #@UnresolvedImport
from ems.qt4.gui.mapper.strategies.bool_strategy import BoolStrategy #@UnresolvedImport
from ems.qt4.gui.mapper.strategies.number_strategy import NumberStrategy #@UnresolvedImport
from ems.qt4.gui.mapper.strategies.date_strategy import DateStrategy #@UnresolvedImport
from ems.qt4.gui.mapper.strategies.listofdicts_strategy import ListOfDictsStrategy #@UnresolvedImport
from ems.qt4.gui.mapper.strategies.oneofalist_strategy import OneOfAListStrategy #@UnresolvedImport

#Configure MapperDefaults
mapperDefaults = MapperDefaults.getInstance()
mapperDefaults.addStrategy(StringStrategy())
boolStrategy = BoolStrategy()
boolStrategy.valueNames = {True:QString.fromUtf8('True'),
                           False:QString.fromUtf8('False'),
                           None: QString.fromUtf8('Unknown')}
mapperDefaults.addStrategy(boolStrategy)
mapperDefaults.addStrategy(NumberStrategy())
mapperDefaults.addStrategy(DateStrategy())
mapperDefaults.addStrategy(ListOfDictsStrategy())
mapperDefaults.addStrategy(OneOfAListStrategy())