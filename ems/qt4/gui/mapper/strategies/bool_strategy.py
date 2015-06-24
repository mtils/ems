'''
Created on 21.03.2012

@author: michi
'''
from PyQt4.QtCore import QVariant, Qt
from PyQt4.QtGui import QStyledItemDelegate, QComboBox, QButtonGroup

from ems.qt4.gui.mapper.base import BaseStrategy
from ems.xtype.base import BoolType #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.stringtype import StringTypeDelegate #@UnresolvedImport
from ems.qt4.gui.itemdelegate.xtypes.oneofalisttype import OneOfAListDelegate #@UnresolvedImport
from ems.xtype.base import OneOfAListType #@UnresolvedImport
from ems.qt4.itemmodel.xtype.oneofalistmodel import OneOfAListModel #@UnresolvedImport
from ems.qt4.util import variant_to_pyobject

class BoolButtonGroupDelegate(QStyledItemDelegate):
    def __init__(self, buttonGroup, model, columnIndex, dataWidgetMapper=None, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.buttonGroup = buttonGroup
        self.model = model
        self.columnIndex = columnIndex
        self.dataWidgetMapper = dataWidgetMapper
        
        self.trueButton = None
        for button in buttonGroup.buttons():
            prop = variant_to_pyobject(button.property('buttonValue'))
            if prop == True:
                self.trueButton = button
        if self.trueButton is None:
            raise NotImplementedError("One button of the buttongroup needs" +
                                      " to have a qproperty named buttonValue" +
                                      " which value is boolean True")
        
        self.buttonGroup.buttonClicked.connect(self.onButtonChanged)
        self.model.dataChanged.connect(self.onModelChanged)
        if self.dataWidgetMapper is not None:
            self.dataWidgetMapper.currentIndexChanged.connect(self.setCurrentModelData)
    
    def setCurrentModelData(self, currentIndex=0):
        modelData = variant_to_pyobject(self.getModelIndex().data())
        self.setButtonValue(modelData)
    
    def getButtonGroupValue(self):
        for button in self.buttonGroup.buttons():
            prop = variant_to_pyobject(button.property('buttonValue'))
            if prop == True:
                if button.isChecked():
                    return True
            else:
                if button.isChecked():
                    return False
                
        return None
    
    def getModelIndex(self):
        if self.dataWidgetMapper is not None:
            row = self.dataWidgetMapper.currentIndex()
        else:
            row = 0
        #print row
        return self.model.index(row, self.columnIndex, Qt.EditRole)
    
    def onButtonChanged(self, button):
        newValue = self.getButtonGroupValue()
        
        index = self.getModelIndex()
        oldValue = variant_to_pyobject(index.data())
        if newValue != oldValue:
            self.model.setData(index, newValue)
    
    def onModelChanged(self, fromIndex, toIndex):
        hit = False
        for i in range(fromIndex.column(), toIndex.column()+1):
            if i == self.columnIndex:
                hit = True
        if not hit:
            return

        index = self.getModelIndex()
        newValue = variant_to_pyobject(index.data())
        buttonValue = self.getButtonGroupValue()
        if newValue != buttonValue:
            self.setButtonValue(newValue)
    
    def setButtonValue(self, value):
        if value == True:
            for button in self.buttonGroup.buttons():
                if variant_to_pyobject(button.property("buttonValue")) == True:
                    button.setChecked(True)
                else:
                    button.setChecked(False)
        if value == False:
            for button in self.buttonGroup.buttons():
                if variant_to_pyobject(button.property("buttonValue")) == True:
                    button.setChecked(False)
                else:
                    button.setChecked(True)
        
    
    def setEditorData(self, editor, index):
        pyValue = variant_to_pyobject(index.data())
        if pyValue == True:
            editor.setChecked(True)
        else:
            editor.setChecked(False)
    
    def setModelData(self, editor, model, index):
        if editor.isChecked():
            model.setData(index, QVariant(True))
        else:
            model.setData(index, QVariant(False))

class BoolStrategy(BaseStrategy):
    
    def __init__(self, parent=None):
        BaseStrategy.__init__(self, parent)
        self.valueNames = {}
    
    def match(self, param):
        if isinstance(param, BoolType):
            return True
        return False
    
    def getDelegateForItem(self, mapper, type_, parent=None):
        delegate = OneOfAListDelegate(self.boolToOneOfAList(type_), parent)
        delegate.valueNames = self.valueNames
        return delegate
    
    def addMapping(self, mapper, widget, columnName, type_):

        columnIndex = mapper.model.columnOfName(columnName)

        if isinstance(widget, QComboBox):
            index = mapper.model.createIndex(0, columnIndex)
            delegate = mapper.dataWidgetMapper.itemDelegate()._getDelegate(index)
            delegate.configureEditor(widget, type_)
            delegate.valueNames = self.valueNames

        if isinstance(widget, QButtonGroup):
            widget.connection = BoolButtonGroupDelegate(widget, mapper.model, columnIndex, mapper.dataWidgetMapper)
            return

        mapper.dataWidgetMapper.addMapping(widget, columnIndex)
    
    def boolToOneOfAList(self, xType):
        pseudoBoolType = OneOfAListType(xType.canBeNone, xType.defaultValue)
        pseudoBoolType.possibleValues = (True, False)
        pseudoBoolType.xTypeOfItems = xType
        return pseudoBoolType
    
