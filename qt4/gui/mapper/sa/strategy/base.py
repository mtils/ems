'''
Created on 19.06.2011

@author: michi
'''
from PyQt4.QtCore import QObject
from PyQt4.QtGui import QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, \
    QAbstractSlider, QDoubleSpinBox, QLabel

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
    
    def getWidget(self, prototype, property):
        objMapper = object_mapper(prototype)
        rProperty = objMapper.get_property(property)
        try:
            colType = self.extractType(rProperty)
        except TypeError:
            return QLabel("?")
        
        if isinstance(colType, Integer):
            widget = QSpinBox()
            self.setSpinBoxOptions(widget, rProperty, colType)
            self._setQWidgetParams(widget, rProperty)
            return widget
            
        elif isinstance(colType, Float):
            widget = QDoubleSpinBox()
            self.setDoubleSpinBoxOptions(widget, rProperty, colType)
            self._setQWidgetParams(widget, rProperty)
            return widget
        
        else:
            widget = QLineEdit()
            self.setLineEditOptions(widget, rProperty)
            self._setQWidgetParams(widget, rProperty)
            return widget
    
    def getColInfos(self, rProperty):
        cols = rProperty.columns
        if len(cols) == 1:
            col = cols[0]
        return col.info
    
    def setSpinBoxOptions(self, spinbox, rProperty, colType=None):
        if colType is None:
            colType = self.extractType(rProperty)
        
        colInfo = self.getColInfos(rProperty)
        if colInfo is not None:
            if colInfo.has_key('unit'):
                spinbox.setSuffix(self.trUtf8(colInfo['unit']))
        
    
    def setDoubleSpinBoxOptions(self, spinbox, rProperty, colType=None):
        if colType is None:
            colType = self.extractType(rProperty)
        
        colInfo = self.getColInfos(rProperty)
        
        if colInfo is not None:
            if colInfo.has_key('unit'):
                spinbox.setSuffix(self.trUtf8(u" %s" % colInfo['unit']))
        
        pass
    
    def setAbstractSliderOptions(self, spinbox, rProperty, colType=None):
        if colType is None:
            colType = self.extractType(rProperty)
        pass
    
    def setLineEditOptions(self, lineEdit, rProperty, colType=None):
        if colType is None:
            colType = self.extractType(rProperty)
        lineEdit.setMaxLength(colType.length)
    
    def extractType(self, rProperty):
        if isinstance(rProperty, ColumnProperty):
            cols = rProperty.columns
            if len(cols) == 1:
                col = cols[0]
                colType = col.type
                if isinstance(colType, AbstractType):
                    if isinstance(colType, String):
                        return colType
                    elif isinstance(colType, Integer):
                        return colType
                    elif isinstance(colType, Float):
                        return colType
                    elif isinstance(colType, Boolean):
                        raise NotImplementedError("Bools are currently not implemented")
                        
                else:
                    raise TypeError("Could not determine Type of %s" % \
                                    (property))
            else:
                raise NotImplementedError("ColumnProperties with more than " +
                                          "one Column are not supported")
        else:
            raise TypeError("BaseStrategy can only handle ColumnProperties")

    def map(self, widget, prototype, property):
        objMapper = object_mapper(prototype)
        rProperty = objMapper.get_property(property)
        colType = self.extractType(rProperty)
        
        if isinstance(colType, String):
            if isinstance(widget, (QLineEdit, QTextEdit,
                                   QPlainTextEdit)):
                columnIndex = self.mapper.model.getIndexByPropertyName(property)
                self.mapper.dataWidgetMapper.addMapping(widget,
                                                        columnIndex)
                if isinstance(widget, QLineEdit):
                    self.setLineEditOptions(widget, rProperty)
                self._setQWidgetParams(widget, rProperty)
            else:
                raise TypeError("Could not map Widget %s to String" % \
                                widget)
        elif isinstance(colType, Integer):
            if isinstance(widget, (QSpinBox, QAbstractSlider)):
                columnIndex = self.mapper.model.getIndexByPropertyName(property)
                self.mapper.dataWidgetMapper.addMapping(widget,
                                                        columnIndex)
                
                if isinstance(widget, QSpinBox):
                    self.setSpinBoxOptions(widget, rProperty, colType)
                if isinstance(widget, QAbstractSlider):
                    self.setAbstractSliderOptions(widget, rProperty, colType)
                self._setQWidgetParams(widget, rProperty)
                
            else:
                raise TypeError("Could not map Widget %s to Int" % \
                                widget)
        elif isinstance(colType, Float):
            if isinstance(widget, QDoubleSpinBox):
                self.setDoubleSpinBoxOptions(widget, rProperty, colType)
                self._setQWidgetParams(widget, rProperty)
                columnIndex = self.mapper.model.getIndexByPropertyName(property)
                self.mapper.dataWidgetMapper.addMapping(widget,
                                                        columnIndex)
            else:
                raise TypeError("Floats needs a QDoubleSpinBox")
        elif isinstance(colType, Boolean):
            raise NotImplementedError("Bools are currently not implemented")
                        
        
        
    def _setQWidgetParams(self, widget, rProperty):
        col = rProperty.columns[0]
        if col.doc is not None:
            widget.setToolTip(self.trUtf8(col.doc))