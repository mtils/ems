'''
Created on 19.06.2011

@author: michi
'''
from PyQt4.QtCore import QObject
from PyQt4.QtGui import QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, \
    QAbstractSlider, QDoubleSpinBox, QLabel, QComboBox

from sqlalchemy.types import AbstractType, String, Integer, Float, Boolean
from sqlalchemy.orm import object_mapper
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.ext.hybrid import hybrid_property, Comparator #@UnresolvedImport

from ems.qt4.gui.mapper.sa.delegate.base import MapperDelegate  #@UnresolvedImport
from ems.qt4.gui.mapper.sa.delegate.unit import UnitColumnDelegate #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.stringtypecombobox import StringComboboxDelegate

class BaseStrategy(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self._rProperties = {}
    
    def getValueString(self, obj, property, colInfo=None):
        return "" % (self.getValuePrefix(obj, property, colInfo),
                     )
    
    def formatValue(self, obj, property, colInfo=None):
        pass
    
    def getValueFormatString(self, obj, rProperty):
        colInfo = self.getColInfos(rProperty)
        if colInfo is not None:
            if colInfo.has_key('textFormat'):
                return unicode(colInfo['textFormat'])
        return None
    
    def getValuePrefix(self, obj, rProperty):
        return u""
    
    def getValueSuffix(self, instance, rProperty):
        #colType = self.extractType(rProperty)
        colInfo = self.getColInfos(rProperty)
        if colInfo is not None:
            if colInfo.has_key('unit'):
                return u" %s" % colInfo['unit']
        return u""
    
    def getWidget(self, mapper, propertyName, rProperty, parent=None):
        
        
        try:
            colType = self.extractType(rProperty)
        except TypeError:
            return QLabel("?")
        
        if isinstance(colType, Integer):
            widget = QSpinBox(parent)
            self.setSpinBoxOptions(widget, rProperty, colType)
            self._setQWidgetParams(widget, rProperty)
            return widget
            
        elif isinstance(colType, Float):
            widget = QDoubleSpinBox(parent)
            self.setDoubleSpinBoxOptions(widget, rProperty, colType)
            self._setQWidgetParams(widget, rProperty)
            return widget
        
        else:
            widget = QLineEdit(parent)
            self.setLineEditOptions(widget, rProperty)
            self._setQWidgetParams(widget, rProperty)
            return widget
    
    def getColInfos(self, rProperty):
        if isinstance(rProperty, ColumnProperty):
            cols = rProperty.columns
            if len(cols) == 1:
                col = cols[0]
                return col.info
        elif isinstance(rProperty, hybrid_property):
            return {}
        #return col.info
    
    def setSpinBoxOptions(self, spinbox, rProperty, colType=None):
        if colType is None:
            colType = self.extractType(rProperty)
        
        colInfo = self.getColInfos(rProperty)
        if colInfo is not None:
            if colInfo.has_key('unit'):
                spinbox.setSuffix(self.trUtf8(colInfo['unit']))
                
        spinbox.setMaximum(99999)
        
    
    def setDoubleSpinBoxOptions(self, spinbox, rProperty, colType=None):
        if colType is None:
            colType = self.extractType(rProperty)
        
        colInfo = self.getColInfos(rProperty)
        
        if colInfo is not None:
            if colInfo.has_key('unit'):
                spinbox.setSuffix(self.trUtf8(u" %s" % colInfo['unit']))
        spinbox.setMaximum(100000.0)
    
    def setAbstractSliderOptions(self, spinbox, rProperty, colType=None):
        if colType is None:
            colType = self.extractType(rProperty)
        pass
    
    def setLineEditOptions(self, lineEdit, rProperty, colType=None):
        if colType is None:
            colType = self.extractType(rProperty)
        if isinstance(colType.length, int):
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
        elif isinstance(rProperty, hybrid_property):
            cmp = rProperty.expr(object()).comparator
            if not isinstance(cmp, Comparator):
                raise ValueError('Please implement a Comparator on hybrid_property "{0}"'.format(rProperty))
            if not hasattr(cmp,'type') or not isinstance(cmp.type, AbstractType):
                raise ValueError('Please implement {0}.type (AbstractType)'.format(cmp.__class__.__name__))
            
            colType = cmp.type
            
            
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
            raise TypeError("BaseStrategy can only handle ColumnProperties and hybrid_property")
    
    @staticmethod
    def buildObjectHash(obj):
        return obj.__module__ + "." + obj.__class__.__name__
    
    @staticmethod
    def buildPropertyHash(obj, propertyName):
        return BaseStrategy.buildObjectHash(obj) + '.' + propertyName
    
    def getRProperty(self, instance, propertyName):
        objHash = self.buildPropertyHash(instance, propertyName)
        if not self._rProperties.has_key(objHash):
            saMapper = object_mapper(instance)
            self._rProperties[objHash] = saMapper.get_property(propertyName)

        return self._rProperties[objHash]
    
    def getDelegateForItem(self, mapper, propertyName, rProperty, parent=None):
        prototype = mapper.ormObject
        try:
            colType = self.extractType(rProperty)
            if isinstance(colType, (Integer, Float)):
                return UnitColumnDelegate(mapper, propertyName,
                                          self.getValuePrefix(prototype,
                                                              rProperty),
                                          self.getValueSuffix(prototype,
                                                              rProperty),
                                          self.getValueFormatString(prototype,
                                                                    rProperty))
            else:
                return MapperDelegate(mapper, propertyName)
            
        except TypeError:
            return None
        return None
    
    def map(self, mapper, widget, propertyName, rProperty):

        colType = self.extractType(rProperty)
        columnIndex = mapper.model.columnOfName(propertyName)

        if isinstance(colType, String):
            if isinstance(widget, (QLineEdit, QTextEdit,
                                   QPlainTextEdit)):
                
                mapper.dataWidgetMapper.addMapping(widget,
                                                        columnIndex)
                if isinstance(widget, QLineEdit):
                    self.setLineEditOptions(widget, rProperty)
                self._setQWidgetParams(widget, rProperty)

            elif isinstance(widget, QComboBox):

                mapperDelegate = mapper.dataWidgetMapper.itemDelegate()
                delegate = StringComboboxDelegate(colType)
                delegate.setConnectedWidget(widget, mapper.model, columnIndex)
                delegate.currentRow = mapper.dataWidgetMapper.currentIndex()
                mapper.dataWidgetMapper.currentIndexChanged.connect(delegate.setCurrentRow)

                mapperDelegate._columnDelegates[columnIndex] = delegate

            else:
                raise TypeError("Could not map Widget %s to String" % \
                                widget)
        elif isinstance(colType, Integer):
            if isinstance(widget, (QSpinBox, QAbstractSlider)):
                mapper.dataWidgetMapper.addMapping(widget,
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
                mapper.dataWidgetMapper.addMapping(widget,
                                                        columnIndex)
            else:
                raise TypeError("Floats needs a QDoubleSpinBox")
        elif isinstance(colType, Boolean):
            raise NotImplementedError("Bools are currently not implemented")
                        
        
        
    def _setQWidgetParams(self, widget, rProperty):
        if isinstance(rProperty, ColumnProperty):
            col = rProperty.columns[0]
            if col.doc is not None:
                widget.setToolTip(self.trUtf8(col.doc))