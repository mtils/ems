'''
Created on 24.02.2011

@author: michi
'''
from ems.converter import Converter
try:
    from ems.converter.readers.dbase import DBase
except ImportError:
    pass
from ems.converter.readers.dbdump import DBDump
from ems.converter.readers.excel import Excel
from ems.converter.readers.csv import CSVReader #@UnresolvedImport
try:
    from ems.converter.writers.alchemycore import AlchemyCore
except ImportError:
    pass
from ems.converter.writers.csv import CSV
from ems.converter.writers.dummy import Dummy
from ems.converter.writers.excel import Excel as ExcelWriter #@UnresolvedImport
from ems.converter.preprocessors.attributeset import AttributeSet 
from ems.converter.tags.foreach import ForEach
from ems.converter.tags.valueof import ValueOf
from ems.converter.tags.element import Element
from ems.converter.tags.modifier import Modifier
from ems.converter.tags.variable import Variable
from ems.converter.modifiers.replace import Replace
from ems.converter.modifiers.concat import Concat
from ems.converter.modifiers.join import Join #@UnresolvedImport
from ems.converter.modifiers.generatecacheid import GenerateCacheId
from ems.converter.modifiers.substring import Substring
from ems.converter.plugin import Plugin


def getPreConfigured(plugins=()):
    converter = Converter()
    converter.addPlugin(Converter.preprocessor,AttributeSet())
    try:
        converter.addPlugin(Converter.reader,DBase())
    except ImportError:
        pass
    converter.addPlugin(converter.reader,DBDump())
    converter.addPlugin(Converter.reader,Excel())
    converter.addPlugin(Converter.reader,CSVReader())
    try:
        converter.addPlugin(Converter.writer,AlchemyCore())
    except NameError:
        pass
    converter.addPlugin(Converter.writer,CSV())
    converter.addPlugin(Converter.writer,Dummy())
    converter.addPlugin(Converter.writer,ExcelWriter())
    converter.addPlugin(Converter.tag,ForEach())
    converter.addPlugin(Converter.tag,ValueOf())
    converter.addPlugin(Converter.tag,Element())
    converter.addPlugin(Converter.tag,Modifier())
    converter.addPlugin(Converter.tag,Variable())
    converter.addPlugin(Converter.modifier,Replace())
    converter.addPlugin(Converter.modifier,Concat())
    converter.addPlugin(Converter.modifier,Join())
    converter.addPlugin(Converter.modifier,GenerateCacheId())
    converter.addPlugin(Converter.modifier,Substring())
    
    return converter