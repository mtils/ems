'''
Created on 19.09.2011

@author: michi
'''

from ems.qt4.gui.itemdelegate import UnitDelegate
from base import MapperDelegate #@UnresolvedImport

class UnitColumnDelegate(UnitDelegate, MapperDelegate):
    def __init__(self, mapper, propertyName, prefix="",suffix="",
                  numberformat=None, parent=None):
        UnitDelegate.__init__(self, prefix, suffix, numberformat, parent)
        MapperDelegate.__init__(self, mapper, propertyName, parent)
