'''
Created on 19.06.2011

@author: michi
'''
from PyQt4.QtCore import QObject
from PyQt4.QtGui import QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, \
    QAbstractSlider

from sqlalchemy.types import AbstractType, String, Integer, Float, Boolean
from sqlalchemy.orm import object_mapper
from sqlalchemy.orm.properties import ColumnProperty


class BaseStrategy(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self._mapper = None
    
    def getMapper(self):
        return self._mapper
    
    def setMapper(self, mapper):
        self._mapper = mapper
    
    mapper = property(getMapper, setMapper)

    def map(self, widget, prototype, property):
        objMapper = object_mapper(prototype)
        rProperty = objMapper.get_property(property)
        if isinstance(rProperty, ColumnProperty):
            cols = rProperty.columns
            if len(cols) == 1:
                col = cols[0]
                colType = col.type
                if isinstance(colType, AbstractType):
                    if isinstance(colType, String):
                        if isinstance(widget, (QLineEdit, QTextEdit,
                                               QPlainTextEdit)):
                            columnIndex = self.mapper.model.getIndexByPropertyName(property)
                            self.mapper.dataWidgetMapper.addMapping(widget,
                                                                    columnIndex)
                            if isinstance(widget, QLineEdit):
                                widget.setMaxLength(colType.length)
                            self._setQWidgetParams(widget, rProperty)
                        else:
                            raise TypeError("Could not map Widget %s to String" % \
                                            widget)
                    elif isinstance(colType, Integer):
                        if isinstance(widget, (QSpinBox, QAbstractSlider)):
                            columnIndex = self.mapper.model.getIndexByPropertyName(property)
                            self.mapper.dataWidgetMapper.addMapping(widget,
                                                                    columnIndex)
                            self._setQWidgetParams(widget, rProperty)
                            
                        else:
                            raise TypeError("Could not map Widget %s to Int" % \
                                            widget)
                    elif isinstance(colType, Float):
                        raise NotImplementedError("Floats are currently not implemented")
                    elif isinstance(colType, Boolean):
                        raise NotImplementedError("Bools are currently not implemented")
                        
                else:
                    raise TypeError("Could not determine Type of %s.%s" % \
                                    (prototype.__class__.__name__,property))
            else:
                raise NotImplementedError("ColumnProperties with more than " +
                                          "one Column are not supported")
        else:
            raise TypeError("SAMapperStrategy can only handle ColumnProperties")
        
    def _setQWidgetParams(self, widget, rProperty):
        print "Isch bin dranne"
        col = rProperty.columns[0]
        if col.doc is not None:
            widget.setToolTip(self.trUtf8(col.doc))