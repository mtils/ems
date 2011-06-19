'''
Created on 19.06.2011

@author: michi
'''

from PyQt4.QtGui import QComboBox

from sqlalchemy.orm import object_mapper

from base import BaseStrategy

class Many2OneComboStrategy(BaseStrategy):
    def map(self, widget, prototype, property):
        if isinstance(widget, QComboBox):
            objMapper = object_mapper(prototype)
            rProperty = objMapper.get_property(property)
            print "Ich mache im Moment ersma nuescht"
        else:
            raise TypeError("Many2OneComboStrategy can only handle QCombobox")